#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 

import json, sys, os, certifi
import datetime, time
import asyncio
from threading import Timer
import traceback
from tw_api.utils.logger_tools import logger
from tw_api.trader.binance_trader.UMBinance import UMBinance
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from binance.websocket.binance_socket_manager import BinanceSocketManager
os.environ['SSL_CERT_FILE'] = certifi.where()
from tw_api.utils.logger_tools import logger

class BAWSDataSource:
    interval_list = []
    symbol_list = []
    continuousKline_did_change_callback = None
    min_volume_amount = 240000000.0
    um_http_client: UMBinance = UMBinance()
    um_ws_client: UMFuturesWebsocketClient = None

    def subscribe_all_symbol_ohlcv(self):
        interval_list = self.interval_list
        symbol_list = self.symbol_list
        logger.debug(f"subscribe_all_symbol_ohlcv->{interval_list} {symbol_list}")
        # logger.debug(f'ticker_infos---->{json.dumps(ticker_infos)}')
        symbol_str_list = []
        for symbol in symbol_list:
            for interval in self.interval_list:
                sb_str = symbol.lower()
                stream_str = "{}_{}@continuousKline_{}".format(sb_str.lower(), 'perpetual', interval)
                if stream_str in symbol_str_list:
                    continue
                elif len(symbol_str_list) > 188:
                    continue
                else:
                    symbol_str_list.append(stream_str)
        self.watch_symbols_ohlcv(symbol_list=symbol_str_list)

    def to_ohlcv_list(self, ohlcv_info: dict):
        '''
        :param ohlcv_info:{
        "e":"continuous_kline",   // 事件类型
        "E":1607443058651,        // 事件时间
        "ps":"BTCUSDT",           // 标的交易对
        "ct":"PERPETUAL",         // 合约类型
        "k":{
            "t":1607443020000,      // 这根K线的起始时间
            "T":1607443079999,      // 这根K线的结束时间
            "i":"1m",               // K线间隔
            "f":116467658886,       // 这根K线期间第一笔成交ID
            "L":116468012423,       // 这根K线期间末一笔成交ID
            "o":"18787.00",         // 这根K线期间第一笔成交价
            "c":"18804.04",         // 这根K线期间末一笔成交价
            "h":"18804.04",         // 这根K线期间最高成交价
            "l":"18786.54",         // 这根K线期间最低成交价
            "v":"197.664",          // 这根K线期间成交量
            "n":543,                // 这根K线期间成交笔数
            "x":false,              // 这根K线是否完结(是否已经开始下一根K线)
            "q":"3715253.19494",    // 这根K线期间成交额
            "V":"184.769",          // 主动买入的成交量
            "Q":"3472925.84746",    // 主动买入的成交额
            "B":"0"                 // 忽略此参数
        }
        }
        :return: [1672196880000, 16662.6, 16662.7, 16656.7, 16656.8, 131.074]
        '''
        ohlcv_list = [int(ohlcv_info['k']['t']), float(ohlcv_info['k']['o']), float(ohlcv_info['k']['h']), float(ohlcv_info['k']['l']), float(ohlcv_info['k']['c']), float(ohlcv_info['k']['v'])]

        return ohlcv_list

    def ohlcv_message_handler(self, stream_data: dict):
        ohlcv_info = {}
        if isinstance(stream_data, dict):
            pass
        else:
            return
        if 'e' in stream_data.keys():
            if stream_data['e'] == 'continuous_kline':
                ohlcv = self.to_ohlcv_list(stream_data)
                if callable(self.continuousKline_did_change_callback):
                    # logger.debug(f"watch_ohlcv-4->{symbol} {interval}")
                    symbol = stream_data['ps']
                    interval = stream_data['k']['i']
                    data = {
                        'symbol': symbol,
                        'interval': interval,
                        'ohlcv': ohlcv
                    }
                    # logger.debug(f"ohlcv_message_handler-->{json.dumps(data)}")
                    self.continuousKline_did_change_callback(data)
                else:
                    # logger.debug(f"watch_ohlcv-5->{symbol} {interval}")
                    pass
            else:
                pass
        else:
            pass

    def ba_watch_symbols_ohlcv(self, symbol_str: str):
        stream_id = int(round(time.time() * 1000))
        self.um_ws_client.subscribe(
            id=stream_id,
            stream=symbol_str
        )

    def list_split(self, items: list, n: int):
        return [items[i:i + n] for i in range(0, len(items), n)]

    def watch_symbols_ohlcv(self, symbol_list: list):
        for index in range(0, len(symbol_list)):
            symbol_str = symbol_list[index]
            timer = Timer(0.25*index, self.ba_watch_symbols_ohlcv, [symbol_str])
            timer.start()

    def stop_monitor(self):
        if self.um_ws_client is not None:
            try:
                self.um_ws_client.stop()
                del self.um_ws_client
                self.um_ws_client = None
            except Exception as exp:
                logger.debug(f'stop_monitor---->{exp}')
            finally:
                pass
        self.um_ws_client = None

    def um_ws_client_on_message(self, skt_mng: BinanceSocketManager, msg_str: str):
        message = json.loads(msg_str)
        self.ohlcv_message_handler(stream_data=message)
            
    def start_monitor(self):
        self.um_ws_client = UMFuturesWebsocketClient(on_message=self.um_ws_client_on_message)
        try:
            self.subscribe_all_symbol_ohlcv()
        except Exception as exp:
            logger.debug(f'subscribe_all_symbol_ohlcv---->{exp}')
        finally:
            pass