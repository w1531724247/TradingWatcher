# 

from tw_api.trader.binance_trader.BAWSDataSource import BAWSDataSource
from tw_api.utils.time_tools import getBeijingDateFromTimestamp
from tw_api.utils.path_tools import PathTools
from tw_api.config import ScriptEnginerVersion
import traceback
import pandas
import numpy
import pandas_ta
import itertools
import math
import copy
import logging
import time
import datetime
import json
import plotly.graph_objects as pygo
from plotly import subplots
from tw_api.utils.logger_tools import logger
from func_timeout import func_set_timeout
from pathlib import Path
import base64
from tw_api.tvShapes import *

class CustomIndicator:
    idct_id = '' # 本地用的id
    s_id = '' # 服务端存的id
    name = ''
    version = '1.0.0'
    deploy_version = ScriptEnginerVersion
    detail_url = ''
    open_source = 'YES'
    input_params = {}
    custom_code: str = ''

    def __init__(self, custom_code: str):
        self.override_functions(custom_code=custom_code)
    
    @classmethod
    def decrypt_code(cls, custom_code: str):
        de_code = custom_code
        for i in range(0, 5):
            bs64_str = str(base64.b64decode(de_code), "utf-8")
            de_code = bs64_str
        return de_code

    @classmethod
    def encrypt_code(cls, custom_code: str):
        en_code = custom_code
        for i in range(0, 5):
            bs64_str = str(base64.b64encode(en_code.encode('utf-8')), "utf-8")
            en_code = bs64_str
        return en_code

    def to_dict(self):
        idct_id = self.idct_id
        if idct_id == '':
            idct_id = self.s_id
        return {
            'idct_id': idct_id,
            'name': self.name,
            'version': self.version,
            'deploy_version': self.deploy_version,
            'detail_url': self.detail_url,
            'open_source': self.open_source,
            'input_params': self.input_params,
            'custom_code': self.custom_code
        }

    def override_functions(self, custom_code: str):
        if isinstance(custom_code, str) == False:
            return
        else:
            pass
        self.custom_code = custom_code
        indicator_code = '''
{custom_code}
    
    @classmethod
    def copy_functions(cls):
        # 复制所有属性以及方法
        attrs_list = dir(cls)
        for at_name in attrs_list:
            if at_name.startswith('__'):
                pass
            else:
                attr = getattr(cls, at_name)
                setattr(CustomIndicator, at_name, attr)
TWIndicator.copy_functions()
        '''.format(custom_code=custom_code)
        logger.debug('-' * 88)
        # logger.debug(f'override_functions-->{indicator_code}')
        logger.debug('-' * 88)
        try:
            executable = compile(indicator_code, 'TWIndicator.py', 'exec')
            exec(executable)
            self.complete_input_params_infos()
        except Exception as e:
            logger.error(f'CustomIndicator-->{e}')
            logger.error(f'CustomIndicator-->{traceback.format_exc()}')
        finally:
            pass
    
    def complete_input_params_infos(self):
        if len(self.input_params) > 0:
            for key in self.input_params.keys():
                p_info = self.input_params[key]
                p_info['default'] = p_info['value']
        else:
            pass

    def main(self, symbol: str, interval: str, klines: list):
        pass

    def format_check(self):
        enginer_version = int(ScriptEnginerVersion);
        (format_ok, msg) = (True, '格式正确')
        if self.custom_code.find('def main(self') == -1:
            return (False, '缺少main函数')
        if self.custom_code.find('import os') != -1:
            return (False, '包含非法字符import os')
        if self.custom_code.find('import sys') != -1:
            return (False, '包含非法字符import sys')
        if self.custom_code.find('exec()') != -1:
            return (False, '包含非法字符exec(')
        if self.name.strip().isspace() == True:
            return (False, 'name格式错误')
        if self.version.strip().isspace() == True:
            return (False, 'version格式错误')
        if self.deploy_version.strip().isspace() == True:
            return (False, 'deploy_version格式错误')
        if int(self.deploy_version.replace('.', '')) < enginer_version:
            return (False, f'deploy_version不能低于{enginer_version}')
        if isinstance(self.input_params, dict) == False:
            return (False, 'input_params类型错误')

        return (format_ok, msg)

class CustomSignal:
    name = ''
    version = '1.0.0'
    deploy_version = '100.100.100'
    detail_url = ''
    open_source = 'YES'
    input_params = {}
    custom_code: str = ''

    def __init__(self, custom_code: str):
        self.override_functions(custom_code=custom_code)
        
    @classmethod
    def decrypt_code(cls, custom_code: str):
        de_code = custom_code
        for i in range(0, 5):
            bs64_str = str(base64.b64decode(de_code), "utf-8")
            de_code = bs64_str
        return de_code

    @classmethod
    def encrypt_code(cls, custom_code: str):
        en_code = custom_code
        for i in range(0, 5):
            bs64_str = str(base64.b64encode(en_code.encode('utf-8')), "utf-8")
            en_code = bs64_str
        return en_code

    def to_dict(self):
        return {
            'name': self.name,
            'version': self.version,
            'deploy_version': self.deploy_version,
            'detail_url': self.detail_url,
            'open_source': self.open_source,
            'input_params': self.input_params,
            'custom_code': self.custom_code
        }

    def override_functions(self, custom_code: str):
        if isinstance(custom_code, str) == False:
            return
        else:
            pass
        self.custom_code = custom_code
        signal_code = '''
{custom_code}
    
    @classmethod
    def copy_functions(cls):
        # 复制所有属性以及方法
        attrs_list = dir(cls)
        for at_name in attrs_list:
            if at_name.startswith('__'):
                pass
            else:
                attr = getattr(cls, at_name)
                setattr(CustomSignal, at_name, attr)
TWSignal.copy_functions()
        '''.format(custom_code=custom_code)
        logger.debug('-' * 88)
        # logger.debug(f'override_functions-->{signal_code}')
        logger.debug('-' * 88)
        try:
            executable = compile(signal_code, 'CustomMonitor.py', 'exec')
            exec(executable)
            self.complete_input_params_infos()
        except Exception as e:
            logger.error(f'CustomSignal-->{e}')
            logger.error(f'CustomSignal-->{traceback.format_exc()}')
        finally:
            pass

    def complete_input_params_infos(self):
        if len(self.input_params) > 0:
            for key in self.input_params.keys():
                p_info = self.input_params[key]
                p_info['default'] = p_info['value']
        else:
            pass

    def check_signal(self, symbol: str, interval: str, klines: list):
        pass

    def save_image(self, symbol: str, interval: str, klines: list, to_path: str):
        pass

    def shapes_on_tv_chart(self, symbol: str, interval: str, klines: list):
        pass

    def format_check(self):
        (format_ok, msg) = (True, '格式正确')
        if self.custom_code.find('def check_signal(self') == -1:
            return (False, '缺少check_signal函数')
        if self.custom_code.find('def save_image(self') == -1:
            return (False, '缺少save_image函数')
        if self.name.strip().isspace() == True:
            return (False, 'name格式错误')
        if self.version.strip().isspace() == True:
            return (False, 'version格式错误')
        if self.deploy_version.strip().isspace() == True:
            return (False, 'deploy_version格式错误')
        if int(self.deploy_version.replace('.', '')) < 10000:
            return (False, 'deploy_version不能低于10000')
        if isinstance(self.input_params, dict) == False:
            return (False, 'input_params类型错误')

        return (format_ok, msg)

class SignalEngine:
    kline_data_infos = {}
    min_volume_amount = 0
    dataSource: BAWSDataSource = None
    customSignal: CustomSignal = None
    signal_did_appear_callback = None
    running = False
    tickers = None

    def start_monitor_signal(self, data: dict, tickers: dict):
        checked_interval_list = data["checked_interval_list"]
        symbol_list = data["selected_symbols"]
        min_volume_amount = data["min_volume_amount"]
        custom_code = data["custom_code"]
        input_params = data["input_params"]

        self.customSignal = CustomSignal(custom_code=custom_code)
        self.customSignal.input_params = input_params

        self.tickers = tickers
        self.min_volume_amount = float(min_volume_amount)
        vaild_symbol_list = self.get_vaild_symbol_list(symbol_list=symbol_list)

        self.dataSource = BAWSDataSource()
        self.dataSource.continuousKline_did_change_callback = self.update_kline_data_from_secket
        self.dataSource.symbol_list = vaild_symbol_list
        self.dataSource.interval_list = checked_interval_list
        self.dataSource.start_monitor()
        self.running = True

    def get_vaild_symbol_list(self, symbol_list: list):
        vaild_symbol_list = []
        for symbol in symbol_list:
            min_volume_ok = self.check_min_volume_amount(symbol=symbol)
            if min_volume_ok:
                vaild_symbol_list.append(symbol)
            else:
                pass
        return vaild_symbol_list

    def stop_monitor_signal(self):
        self.kline_data_infos = {}
        self.min_volume_amount = 0
        self.dataSource.stop_monitor()
        self.dataSource = None
        self.customSignal = None
        self.signal_did_appear_callback = None
        self.running = False

    # 更新websocket实时返回的K线数据
    def update_kline_data_from_secket(self, data: dict):
        '''
            {
                'symbol': symbol,
                'interval': interval,
                'ohlcv': ohlcv
            }
        '''
        symbol = data['symbol'];
        interval = data['interval']
        ohlcv = data['ohlcv']
        info_list: list = self.get_kline_data_with_symbol_interval(symbol=symbol, interval=interval)
        if len(info_list) > 0:
            latest_infos = info_list.pop()
            old_t = latest_infos[0]
            new_t = ohlcv[0]
            have_new = False
            if old_t == new_t:
                pass
            else:
                have_new = True
                info_list.append(latest_infos)
            info_list.append(ohlcv)
            if have_new:
                # 出现新K线
                self.check_signal_for_latest_data(symbol=symbol, interval=interval)
            else:
                # 旧K线更新
                pass
        else:
            self.init_klines(symbol=symbol, interval=interval)

    # 从HTTP请求返回的数据初始化K线数据
    def update_kline_data_from_http(self, symbol: str, interval: str, kline_data: list):
        symbol_interval = symbol + "_" + interval
        self.kline_data_infos[symbol_interval] = kline_data

    def init_klines(self, symbol: str, interval: str):
        amount_ok = self.check_min_volume_amount(symbol=symbol)
        # 初始化K线数据
        if amount_ok:
            try:
                kline_data = self.dataSource.um_http_client.continuous_klines(pair=symbol, contractType="PERPETUAL",
                                                                              interval=interval, limit=498)
                # print(f'{symbol}/{interval} 初始化K线数据: {len(kline_data)}')
                self.update_kline_data_from_http(symbol=symbol, interval=interval, kline_data=kline_data)
            except Exception as e:
                self.update_kline_data_from_http(symbol=symbol, interval=interval, kline_data=[[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
                # print(f'continuous_klines-exception->{str(e)}')
            finally:
                pass
        else:
            pass

    def get_kline_data_with_symbol_interval(self, symbol, interval):
        symbol_interval = symbol + "_" + interval
        if symbol_interval in self.kline_data_infos.keys():
            info_list: list = self.kline_data_infos[symbol_interval]
            if info_list is None:
                info_list = []
            else:
                pass
        else:
            info_list = []

        return info_list

    def check_min_volume_amount(self, symbol: str):
        ticker_infos = self.tickers
        if symbol in ticker_infos.keys():
            infos = ticker_infos[symbol]
            quoteVolume = infos["quoteVolume"]
            # print("check_min_volume_amount--total_money--min_volume_amount-->", quoteVolume, self.min_volume_amount)
            if float(quoteVolume) > float(self.min_volume_amount):
                return True
            else:
                return False
        else:
            return False

    def check_signal_for_latest_data(self, symbol: str, interval: str):
        if self.customSignal is None:
            return
        else:
            pass
        try:
            amount_ok = self.check_min_volume_amount(symbol=symbol)
            if amount_ok:
                kline_list: list = self.get_kline_data_with_symbol_interval(symbol=symbol, interval=interval)
                signal_info = self.customSignal.check_signal(symbol=symbol, interval=interval, klines=copy.deepcopy(kline_list))
                # print('check_signal_for_latest_data-->', signal_info)
                signal_appear = signal_info['appear']
                if signal_appear and callable(self.signal_did_appear_callback):
                    s_id = str(int(round(time.time() * 1000)))
                    image_path = PathTools.app_temp_image_file_dir().joinpath(f'{symbol}_{interval}_{s_id}.jpg')
                    image_path = str(image_path)
                    image_url = image_path.replace(str(PathTools.app_temp_dir()), str(PathTools.temp_image_http_file_path()))
                    data = {'s_id': s_id, 
                    'symbol': symbol, 
                    'interval': interval, 
                    'time': int(time.time()), 
                    'name': self.customSignal.name, 
                    'image_path': image_path, 
                    'image_url': image_url,
                    'signal_info': signal_info}
                    # print('signal_did_appear: ', json.dumps(data))
                    self.signal_did_appear_callback(data)
                    self.customSignal.save_image(symbol=symbol, interval=interval, klines=copy.deepcopy(kline_list), to_path=image_path)
                else:
                    pass
            else:
                pass
        except Exception as exp:
            error_msg = '{exp}, {print_exc}'.format(exp=exp, print_exc=traceback.print_exc())
            logger.error(f'check_signal--error-->{error_msg}')
        finally:
            pass