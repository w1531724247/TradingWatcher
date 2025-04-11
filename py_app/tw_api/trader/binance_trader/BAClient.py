# 

from tw_api.server.dbmodels.kv_info import KVInfo
import random
from decimal import Decimal, ROUND_DOWN
import threading
from .BATrader import BATrader
from .UMBinance import UMBinance
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from binance.websocket.binance_socket_manager import BinanceSocketManager
import json
import time, math
from threading import Timer
import os, certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
from tw_api.utils.logger_tools import logger
from tw_api.utils.path_tools import PathTools

class BAClient(BATrader):
    user_socket_ok: bool = False
    call_time_infos = {}
    ba_api_key = None
    ba_secret_key = None
    um_ws_client_connected = False
    um_auth_ws_client_connected = False
    
    # 添加重连相关参数
    reconnect_attempts = 0
    max_reconnect_attempts = 20
    base_reconnect_delay = 5  # 基础重连延迟(秒)
    max_reconnect_delay = 300  # 最大重连延迟(秒)
    
    # 添加心跳检测相关参数
    last_heartbeat_time = 0
    heartbeat_interval = 30  # 心跳间隔(秒)
    heartbeat_timeout = 60  # 心跳超时(秒)
    heartbeat_timer = None

    stream_url = "wss://fstream.binance.com"
    base_url = "https://fapi.binance.com"

    def __del__(self):
        class_name = self.__class__.__name__
        print(class_name, '__del__ 销毁')    
        # 清理定时器
        self._clear_timers()
    
    def _clear_timers(self):
        """清理所有定时器"""
        # 原代码缺少对connection_check_timer的清理
        for timer in [self.updateListenKeyTimer, self.updateInfoTimer, self.heartbeat_timer, self.connection_check_timer]:  # ✅ 已包含所有定时器
            if timer is not None and timer.is_alive():
                timer.cancel()
    
    listenKey: str = None
    updateListenKeyTimer : Timer = None
    updateInfoTimer : Timer = None
    connection_check_timer : Timer = None  # 新增连接状态检查定时器

    um_http_client: UMBinance = None
    um_ws_client: UMFuturesWebsocketClient = None

    # 更新WebSocket事件处理函数，添加时间戳记录
    def um_ws_client_on_close(self, *args, **kwargs):
        logger.warning(f'um_ws_client_on_close args: {args}, kwargs: {kwargs}')
        self.um_ws_client_connected = False
        # 触发重连
        self._schedule_reconnect(is_auth=False)
    
    def um_ws_client_on_error(self, *args, **kwargs):
        logger.error(f'um_ws_client_on_error args: {args}, kwargs: {kwargs}')
        self.um_ws_client_connected = False
        # 触发重连
        self._schedule_reconnect(is_auth=False)

    def um_ws_client_on_ping(self, *args, **kwargs):
        self.um_ws_client_connected = True
        self.last_heartbeat_time = time.time()
        logger.debug(f'um_ws_client_on_ping: 收到ping，更新心跳时间 {self.last_heartbeat_time}')

    def um_ws_client_on_pong(self, *args, **kwargs):
        self.um_ws_client_connected = True
        self.last_heartbeat_time = time.time()
        logger.debug(f'um_ws_client_on_pong: 收到pong，更新心跳时间 {self.last_heartbeat_time}')
    
    def um_auth_ws_client_on_close(self, *args, **kwargs):
        logger.warning(f'um_auth_ws_client_on_close args: {args}, kwargs: {kwargs}')
        self.um_auth_ws_client_connected = False
        # 触发重连
        self._schedule_reconnect(is_auth=True)
    
    def um_auth_ws_client_on_error(self, *args, **kwargs):
        logger.error(f'um_auth_ws_client_on_error args: {args}, kwargs: {kwargs}')
        self.um_auth_ws_client_connected = False
        # 触发重连
        self._schedule_reconnect(is_auth=True)

    def um_auth_ws_client_on_ping(self, *args, **kwargs):
        self.um_auth_ws_client_connected = True
        self.last_heartbeat_time = time.time()
        logger.debug(f'um_auth_ws_client_on_ping: 收到ping，更新心跳时间 {self.last_heartbeat_time}')

    def um_auth_ws_client_on_pong(self, *args, **kwargs):
        self.um_auth_ws_client_connected = True
        self.last_heartbeat_time = time.time()
        logger.debug(f'um_auth_ws_client_on_pong: 收到pong，更新心跳时间 {self.last_heartbeat_time}')

    def _schedule_reconnect(self, is_auth=False):
        """使用指数退避策略安排重连"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"已达到最大重连尝试次数 ({self.max_reconnect_attempts})，停止重连")
            return
        
        # 计算延迟时间（指数退避）
        delay = min(self.base_reconnect_delay * (2 ** self.reconnect_attempts), 
               self.max_reconnect_delay)
        # 添加随机抖动，避免多个客户端同时重连
        delay = delay * (0.8 + 0.4 * random.random())
        
        logger.info(f"计划在 {delay:.2f} 秒后进行第 {self.reconnect_attempts + 1} 次重连尝试")
        
        # 创建定时器进行重连
        timer = Timer(delay, self._do_reconnect, args=[is_auth])
        timer.daemon = True
        timer.start()
        
        self.reconnect_attempts += 1
    
    def _do_reconnect(self, is_auth=False):
        """执行实际的重连操作"""
        try:
            if is_auth:
                logger.info("正在重连认证WebSocket...")
                if self.um_auth_ws_client is not None:
                    try:
                        # 确保停止WebSocket连接
                        self.um_auth_ws_client.stop()
                        # 关闭底层连接
                        if hasattr(self.um_auth_ws_client, '_conn') and self.um_auth_ws_client._conn:
                            self.um_auth_ws_client._conn.close()
                        # 等待连接完全关闭
                        time.sleep(0.5)
                    except Exception as e:
                        logger.error(f"关闭认证WebSocket连接时出错: {e}")
                    finally:
                        # 无论如何都要清除引用
                        del self.um_auth_ws_client
                        self.um_auth_ws_client = None
                
                listenKeyInfos = self.um_auth_http_client.new_listen_key()
                self.listenKey = listenKeyInfos["listenKey"]
                self.um_auth_ws_client = UMFuturesWebsocketClient(
                    stream_url=self.stream_url, 
                    on_message=self.auth_um_ws_client_on_message, 
                    on_close=self.um_auth_ws_client_on_close, 
                    on_error=self.um_auth_ws_client_on_error, 
                    on_ping=self.um_auth_ws_client_on_ping, 
                    on_pong=self.um_auth_ws_client_on_pong
                )
                self.um_auth_ws_client.user_data(
                    listen_key=self.listenKey,
                    id=self.ms_ts()
                )
                logger.info("认证WebSocket重连成功")
                self.um_auth_ws_client_connected = True
            else:
                logger.info("正在重连公共WebSocket...")
                if self.um_ws_client is not None:
                    try:
                        # 确保停止WebSocket连接
                        self.um_ws_client.stop()
                        # 关闭底层连接
                        if hasattr(self.um_ws_client, '_conn') and self.um_ws_client._conn:
                            self.um_ws_client._conn.close()
                        # 等待连接完全关闭
                        time.sleep(0.5)
                    except Exception as e:
                        logger.warning(f"关闭公共WebSocket连接时出错: {e}")
                    finally:
                        # 无论如何都要清除引用
                        del self.um_ws_client
                        self.um_ws_client = None
                
                self.um_ws_client = UMFuturesWebsocketClient(
                    stream_url=self.stream_url, 
                    on_message=self.um_ws_client_on_message, 
                    on_close=self.um_ws_client_on_close, 
                    on_error=self.um_ws_client_on_error, 
                    on_ping=self.um_ws_client_on_ping, 
                    on_pong=self.um_ws_client_on_pong
                )
                self.um_ws_client.ticker(id=self.ms_ts())
                logger.info("公共WebSocket重连成功")
                self.um_ws_client_connected = True
            
            # 重连成功，重置重连尝试次数
            self.reconnect_attempts = 0
            
        except Exception as exp:
            logger.error(f'重连失败: {exp}')
            # 重连失败，安排下一次重连
            self._schedule_reconnect(is_auth)
    
    def start_connection_check(self):
        """启动连接状态检查定时器"""
        if self.connection_check_timer is not None and self.connection_check_timer.is_alive():
            self.connection_check_timer.cancel()
        
        self.connection_check_timer = Timer(self.heartbeat_interval, self.check_connection_status)
        self.connection_check_timer.daemon = True
        self.connection_check_timer.start()
        logger.debug("已启动连接状态检查定时器")
    
    def check_connection_status(self):
        """检查连接状态，如果超时则重连"""
        current_time = time.time()
        
        # 添加未初始化状态的判断
        if self.last_heartbeat_time == 0:  # ✅ 添加初始化逻辑
            self.last_heartbeat_time = current_time
            return

        # 检查心跳超时
        if self.last_heartbeat_time > 0 and (current_time - self.last_heartbeat_time) > self.heartbeat_timeout:
            logger.warning(f"心跳超时: 上次心跳时间 {self.last_heartbeat_time}, 当前时间 {current_time}")
            
            # 检查公共WebSocket
            if self.ticker_watching and not self.um_ws_client_connected:
                logger.warning("公共WebSocket连接已断开，尝试重连")
                self._do_reconnect(is_auth=False)
            
            # 检查认证WebSocket
            if self.user_data_watching and not self.um_auth_ws_client_connected:
                logger.warning("认证WebSocket连接已断开，尝试重连")
                self._do_reconnect(is_auth=True)
        
        # 主动发送ping以保持连接活跃
        self._send_ping()
        
        # 重新启动定时器
        self.start_connection_check()
    
    def _send_ping(self):
        """向WebSocket服务器发送ping以保持连接活跃"""
        try:
            if self.um_ws_client is not None and self.ticker_watching:
                self.um_ws_client.ping()
                logger.debug("已向公共WebSocket发送ping")
        except Exception as e:
            logger.error(f"公共WebSocket 发送ping失败: {e}")
            # 判断输入的错误内容是否是'发送ping失败: socket is already closed.', 如果是则重连
            if 'socket is already closed' in str(e):
                self.um_ws_client_connected = False
            else:
                pass

        try:
            if self.um_auth_ws_client is not None and self.user_data_watching:
                self.um_auth_ws_client.ping()
                logger.debug("已向认证WebSocket发送ping")
        except Exception as e:
            logger.error(f"认证WebSocket 发送ping失败: {e}")
            # 判断输入的错误内容是否是'发送ping失败: socket is already closed.', 如果是则重连
            if 'socket is already closed' in str(e):
                self.um_auth_ws_client_connected =  False
            else:
                pass

    # 在初始化方法中添加启动连接检查
    def initPublicClientIfNeed(self, data: dict):
        result_info = {"code": 0, "msg": "success"}
        if self.ticker_watching:
            return result_info
        else:
            pass
        self.stream_url = data.get('stream_url', 'wss://fstream.binance.com')
        self.base_url = data.get('base_url', 'https://fapi.binance.com')
        try:
            if self.um_http_client is None:
                self.um_http_client = UMBinance(base_url=self.base_url)
                self.um_http_client.js_port = PathTools.js_port
            else:
                pass
            
            if self.um_ws_client is None:
                self.um_ws_client = UMFuturesWebsocketClient(stream_url=self.stream_url, on_message=self.um_ws_client_on_message, on_close=self.um_ws_client_on_close, on_error=self.um_ws_client_on_error, on_ping=self.um_ws_client_on_ping, on_pong=self.um_ws_client_on_pong)
            else:
                pass
            # 获取交易对交易规则信息
            self.get_exchange_info()
            # 获取24小时交易信息
            self.init_ticker_infos()
            # 订阅市场最新成交信息
            self.watch_ticker()
            # 定时更新本地信息
            self.start_update_local_info_timer()
            # 启动连接状态检查
            self.start_connection_check()
            # 初始化心跳时间
            self.last_heartbeat_time = time.time()
        except Exception as e:
            logger.error('initPublicClientIfNeed:', e)
            result_info = {"code": -200, "msg": "访问国际互联网失败"}
        finally:
            return result_info
    
    um_auth_http_client: UMBinance = None
    um_auth_ws_client: UMFuturesWebsocketClient = None
    def initPrivateClientIfNeed(self, data: dict):
        print('initPrivateClientIfNeed--end--', data)
        api_key = data["api_key"]
        self.ba_api_key = api_key
        secret_key = data["secret_key"]
        self.ba_secret_key = secret_key
        if self.um_auth_http_client is None:
            self.um_auth_http_client = UMBinance(base_url=self.base_url, key=api_key, secret=secret_key)
            self.um_auth_http_client.js_port = PathTools.js_port
        else:
            pass
        if self.um_auth_ws_client is None:
            self.um_auth_ws_client = UMFuturesWebsocketClient(stream_url=self.stream_url, on_message=self.auth_um_ws_client_on_message, on_close=self.um_auth_ws_client_on_close, on_error=self.um_auth_ws_client_on_error, on_ping=self.um_auth_ws_client_on_ping, on_pong=self.um_auth_ws_client_on_pong)
        else:
            pass
        resp = {'code':0, 'status':'success'}
        try:
            # 获取持仓方向
            self.get_position_mode()
            # 初始化用户信息(获取仓位信息,余额信息)
            self.init_user_data_infos()
            # 获取所有挂单信息
            self.init_open_orders()
            # 订阅用户数据
            self.start_watch_user_data(data={})
        except Exception as e:
            logger.error('initPrivateClientIfNeed---Exception----:', e)
            {'code':-200, 'status':'fail'}
        finally:
            return resp

    exchangeInfos: dict = None
    def get_exchange_info(self):
        '''
        {
            "exchangeFilters": [],
            "rateLimits": [ // API访问的限制
                {
                    "interval": "MINUTE", // 按照分钟计算
                    "intervalNum": 1, // 按照1分钟计算
                    "limit": 2400, // 上限次数
                    "rateLimitType": "REQUEST_WEIGHT" // 按照访问权重来计算
                },
                {
                    "interval": "MINUTE",
                    "intervalNum": 1,
                    "limit": 1200,
                    "rateLimitType": "ORDERS" // 按照订单数量来计算
                }
            ],
            "serverTime": 1565613908500, // 请忽略。如果需要获取当前系统时间，请查询接口 “GET /fapi/v1/time”
            "assets": [ // 资产信息
                {
                    "asset": "BUSD",
                    "marginAvailable": true, // 是否可用作保证金
                    "autoAssetExchange": 0 // 保证金资产自动兑换阈值
                },
                {
                    "asset": "USDT",
                    "marginAvailable": true, // 是否可用作保证金
                    "autoAssetExchange": 0 // 保证金资产自动兑换阈值
                },
                {
                    "asset": "BNB",
                    "marginAvailable": false, // 是否可用作保证金
                    "autoAssetExchange": null // 保证金资产自动兑换阈值
                }
            ],
            "symbols": [ // 交易对信息
                {
                    "symbol": "BLZUSDT",  // 交易对
                    "pair": "BLZUSDT",  // 标的交易对
                    "contractType": "PERPETUAL",    // 合约类型
                    "deliveryDate": 4133404800000,  // 交割日期
                    "onboardDate": 1598252400000,     // 上线日期
                    "status": "TRADING",  // 交易对状态
                    "maintMarginPercent": "2.5000",  // 请忽略
                    "requiredMarginPercent": "5.0000", // 请忽略
                    "baseAsset": "BLZ",  // 标的资产
                    "quoteAsset": "USDT", // 报价资产
                    "marginAsset": "USDT", // 保证金资产
                    "pricePrecision": 5,  // 价格小数点位数(仅作为系统精度使用，注意同tickSize 区分）
                    "quantityPrecision": 0,  // 数量小数点位数(仅作为系统精度使用，注意同stepSize 区分）
                    "baseAssetPrecision": 8,  // 标的资产精度
                    "quotePrecision": 8,  // 报价资产精度
                    "underlyingType": "COIN",
                    "underlyingSubType": ["STORAGE"],
                    "settlePlan": 0,
                    "triggerProtect": "0.15", // 开启"priceProtect"的条件订单的触发阈值
                    "filters": [
                        {
                            "filterType": "PRICE_FILTER", // 价格限制
                            "maxPrice": "300", // 价格上限, 最大价格
                            "minPrice": "0.0001", // 价格下限, 最小价格
                            "tickSize": "0.0001" // 订单最小价格间隔
                        },
                        {
                            "filterType": "LOT_SIZE", // 数量限制
                            "maxQty": "10000000", // 数量上限, 最大数量
                            "minQty": "1", // 数量下限, 最小数量
                            "stepSize": "1" // 订单最小数量间隔
                        },
                        {
                            "filterType": "MARKET_LOT_SIZE", // 市价订单数量限制
                            "maxQty": "590119", // 数量上限, 最大数量
                            "minQty": "1", // 数量下限, 最小数量
                            "stepSize": "1" // 允许的步进值
                        },
                        {
                            "filterType": "MAX_NUM_ORDERS", // 最多订单数限制
                            "limit": 200
                        },
                        {
                            "filterType": "MAX_NUM_ALGO_ORDERS", // 最多条件订单数限制
                            "limit": 100
                        },
                        {
                            "filterType": "MIN_NOTIONAL",  // 最小名义价值
                            "notional": "1",
                        },
                        {
                            "filterType": "PERCENT_PRICE", // 价格比限制
                            "multiplierUp": "1.1500", // 价格上限百分比
                            "multiplierDown": "0.8500", // 价格下限百分比
                            "multiplierDecimal": 4
                        }
                    ],
                    "OrderType": [ // 订单类型
                        "LIMIT",  // 限价单
                        "MARKET",  // 市价单
                        "STOP", // 止损单
                        "STOP_MARKET", // 止损市价单
                        "TAKE_PROFIT", // 止盈单
                        "TAKE_PROFIT_MARKET", // 止盈暑市价单
                        "TRAILING_STOP_MARKET" // 跟踪止损市价单
                    ],
                    "timeInForce": [ // 有效方式
                        "GTC", // 成交为止, 一直有效
                        "IOC", // 无法立即成交(吃单)的部分就撤销
                        "FOK", // 无法全部立即成交就撤销
                        "GTX" // 无法成为挂单方就撤销
                    ],
                    "liquidationFee": "0.010000",   // 强平费率
                    "marketTakeBound": "0.30",  // 市价吃单(相对于标记价格)允许可造成的最大价格偏离比例
                }
            ],
            "timezone": "UTC" // 服务器所用的时间区域
        }
        :return:
        '''
        try:
            if self.exchangeInfos is None:
                self.exchangeInfos = self.um_http_client.exchange_info()
            else:
                pass
        except Exception as exp:
            logger.debug(f'exchange_info--->{exp}')
        finally:
            return self.exchangeInfos
    
    def init_ticker_infos(self, force: bool = False):
        try:
            ticker_infos = self.um_http_client.ticker_24hr_price_change()
            new_tickers = {}
            for t_info in ticker_infos:
                symbol = t_info['symbol']
                new_tickers[symbol] = t_info
            self.tickers = new_tickers
        except Exception as exp:
            logger.debug(f'ticker_24hr_price_change--->{exp}')
        finally:
            return self.tickers
        
    def update_local_infos(self):
        # 检查虚拟限价订单
        self.check_faker_order_list()
        # 更新价格提醒信息
        self.check_price_alert()
        # 更新仓位盈亏值
        self.update_local_position_data()
        # 重新启动定时器
        self.start_update_local_info_timer()

    def get_current_milliseconds(self):
        return int(time.time() * 1000)

    tickers = None
    def getTickers(self, data: dict = {}):
        if self.tickers is None:
            self.tickers = {}
            
        return self.tickers
    
    price_alert_infos_key = "price_alert_infos_key"

    def get_price_alert_infos(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        alert_infos = KVInfo.get_value_by_key(key=self.price_alert_infos_key)
        if alert_infos is not None:
            self.priceAlertInfos = alert_infos
            return alert_infos
        else:
            return {}

    def save_price_alert_infos(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        KVInfo.update(key=self.price_alert_infos_key, value=data)
        self.priceAlertInfos = data

    def getFakerOpenOrders(self, data: dict):
        if self.faker_order_list == None:
            faker_order_list = KVInfo.get_value_by_key(key=self.faker_order_list_key)
            if faker_order_list is None:
                faker_order_list = []
            else:
                pass
            self.faker_order_list = faker_order_list
        else:
            pass

        return {
            'faker_order_list': self.faker_order_list
        }

    def check_faker_order_list(self):
        self.getFakerOpenOrders({})
        temp_faker_order_list = []
        for order_info in self.faker_order_list:
            '''
            {
                'symbol':symbol, 
                'side':side, 
                'positionSide':positionSide, 
                'type':type,
                'quantity':amount, 
                'newClientOrderId':newClientOrderId, 
                'price':price, 
                'stopPrice':stopPrice,
                'trigger_price': trigger_price,
                'enter_type': lastPrice
            }
            '''
            symbol = order_info.get('symbol', '')
            ticker_info = self.tickers.get(symbol, None)
            if ticker_info is None:
                continue
            lastPrice = ticker_info['lastPrice']
            lastPrice = float(lastPrice)

            enter_price = order_info.get('price', '')
            enter_price = float(enter_price)

            trigger_price = order_info.get('trigger_price', '')
            trigger_price = float(trigger_price)

            enter_type = order_info.get('enter_type', '')

            side = order_info.get('side', '')
            positionSide = order_info.get('positionSide', '')
            amount = order_info.get('quantity', '')
            newClientOrderId = order_info.get('newClientOrderId', '')
            value = order_info.get('value', '')
            loss_price = order_info.get('loss_price', '')
            profit_price = order_info.get('profit_price', '')

            if enter_type == ">=" and lastPrice >= trigger_price:
                order_info = self.open_position_by_limit_with_value({
                    'symbol': symbol,
                    'positionSide': positionSide,
                    'value': value,
                    'price': enter_price,
                    'newClientOrderId': newClientOrderId
                })
                if loss_price != '' or profit_price != '':
                    self.save_stop_and_profit_order_info_for_limit({
                        'loss_price': loss_price,
                        'profit_price': profit_price,
                        'order_info': order_info,
                    })
                else:
                    pass
            elif enter_type == "<=" and lastPrice <= trigger_price:
                order_info = self.open_position_by_limit_with_value({
                    'symbol': symbol,
                    'positionSide': positionSide,
                    'value': value,
                    'price': enter_price,
                    'newClientOrderId': newClientOrderId
                })
                
                if loss_price != '' or profit_price != '':
                    self.save_stop_and_profit_order_info_for_limit({
                        'loss_price': loss_price,
                        'profit_price': profit_price,
                        'order_info': order_info,
                    })
                else:
                    pass
            else:
                low_invaild_price = order_info.get('low_invaild_price', '')
                high_invaild_price = order_info.get('high_invaild_price', '')
                if low_invaild_price != '' and lastPrice <= float(low_invaild_price):
                    pass
                elif high_invaild_price != '' and lastPrice >= float(high_invaild_price):
                    pass
                else:
                    temp_faker_order_list.append(order_info)
        if len(temp_faker_order_list) != len(self.faker_order_list):
            self.faker_order_list = temp_faker_order_list
            KVInfo.update(key=self.faker_order_list_key, value=temp_faker_order_list)
        else:
            pass
    def check_price_alert(self):
        # print('check_price_alert---->', symbol, lastPrice)
        if self.priceAlertInfos is None:
            return
        else:
            pass
        
        for symbol in self.priceAlertInfos.keys():
            ticker_info = self.tickers.get(symbol, None)
            if ticker_info is None:
                continue
            lastPrice = ticker_info['lastPrice']
            lastPrice = float(lastPrice)

            alt_infos: list = self.priceAlertInfos.get(symbol, [])
            temp_alt_infos = []
            for a_info in alt_infos:
                from_price = a_info['from_price']
                from_price = float(from_price)
                to_price = a_info['to_price']
                to_price = float(to_price)
                trigger = False
                valid = a_info['status']
                if to_price < from_price and lastPrice <= to_price and valid == 'valid':
                    a_info['status'] = 'invalid'
                    a_info['detail_msg'] = f'价格提醒:{symbol}当前价格{lastPrice}<={to_price}'
                    md_msg_list = [
                        '**价格提醒**',
                        f'> 交易对: {symbol}',
                        f'> 当前价格: {lastPrice}',
                        f'> 提醒条件: <= {to_price}'
                    ]
                    md_msg = '  \n'.join(md_msg_list)
                    a_info['md_msg'] = md_msg
                    trigger = True
                elif to_price > from_price and lastPrice >= to_price and valid == 'valid':
                    a_info['status'] = 'invalid'
                    a_info['detail_msg'] = f'价格提醒:{symbol}当前价格{lastPrice}>={to_price}'
                    md_msg_list = [
                        '**价格提醒**',
                        f'> 交易对: {symbol}',
                        f'> 当前价格: {lastPrice}',
                        f'> 提醒条件: >= {to_price}'
                    ]
                    md_msg = '  \n'.join(md_msg_list)
                    a_info['md_msg'] = md_msg
                    trigger = True
                else:
                    pass
                if trigger:
                    self.play_price_alert_audio(data=a_info)
                    self.send_price_alert_notify(data=a_info)
                else:
                    temp_alt_infos.append(a_info)
            if len(alt_infos) != len(temp_alt_infos):
                self.priceAlertInfos[symbol] = temp_alt_infos
                KVInfo.update(key=self.price_alert_infos_key, value=self.priceAlertInfos)
            else:
                pass

    def convert_ws_ticker_info_to_http(self, ws_ticker: dict):
        '''
        :param ws_ticker: [
            {
              "e": "24hrTicker",  # 事件类型
              "E": 123456789,     # 事件时间
              "s": "BNBUSDT",      # 交易对
              "p": "0.0015",      # 24小时价格变化
              "P": "250.00",      # 24小时价格变化(百分比)
              "w": "0.0018",      # 平均价格
              "c": "0.0025",      # 最新成交价格
              "Q": "10",          # 最新成交价格上的成交量
              "o": "0.0010",      # 24小时内第一比成交的价格
              "h": "0.0025",      # 24小时内最高成交价
              "l": "0.0010",      # 24小时内最低成交价
              "v": "10000",       # 24小时内成交量
              "q": "18",          # 24小时内成交额
              "O": 0,             # 统计开始时间
              "C": 86400000,      # 统计结束时间
              "F": 0,             # 24小时内第一笔成交交易ID
              "L": 18150,         # 24小时内最后一笔成交交易ID
              "n": 18151          # 24小时内成交数
            }
        ]
        :return:
        '''
        symbol = ws_ticker['s']
        lastPrice = ws_ticker['c']

        return {
          "symbol": symbol,
          "priceChange": ws_ticker['p'],    #24小时价格变动
          "priceChangePercent": ws_ticker['P'],  #24小时价格变动百分比
          "weightedAvgPrice": ws_ticker['w'], #加权平均价
          "lastPrice": lastPrice,        #最近一次成交价
          "lastQty": ws_ticker['Q'],        #最近一次成交额
          "openPrice": ws_ticker['o'],       #24小时内第一次成交的价格
          "highPrice": ws_ticker['h'],      #24小时最高价
          "lowPrice": ws_ticker['l'],         #24小时最低价
          "volume": ws_ticker['v'],        #24小时成交量
          "quoteVolume": ws_ticker['q'],     #24小时成交额
          "openTime": ws_ticker['F'],        #24小时内，第一笔交易的发生时间
          "closeTime": ws_ticker['L'],       #24小时内，最后一笔交易的发生时间
          "firstId": ws_ticker['F'],   # 首笔成交id
          "lastId": ws_ticker['L'],    # 末笔成交id
          "count": ws_ticker['n']         # 成交笔数
        }


    positions = None
    def getPositions(self, data: dict = {}):
        if self.positions is None:
            self.positions = {}

        return self.positions

    openOrders = None
    def getOpenOrders(self, data: dict = {}):
        if self.openOrders is None:
            self.openOrders = {}

        return self.openOrders

    assets = None
    def getAssets(self):
        if self.assets is None:
            self.assets = {}

        return self.assets

    def ms_ts(self):
        ts = time.time()
        return int(round(ts*1000))

    # 订阅K线的回调
    def um_ws_client_on_message(self, skt_mng: BinanceSocketManager, msg_str: str):
        print('um_ws_client_on_message:', type(msg_str))
        message = json.loads(msg_str)
        if isinstance(message, list):
            # print('um_ws_client_on_message:', message[0])
            for t_info in message:
                e = t_info['e']
                if e == '24hrTicker':
                    self.watch_ticker_call_back(message=message)
                else:
                    pass
        else:
            pass
    
    # 订阅用户数据的回调
    def auth_um_ws_client_on_message(self, skt_mng: BinanceSocketManager, msg_str: str):
        print('um_ws_client_on_message:', type(msg_str))
        message = json.loads(msg_str)
        if isinstance(message, list):
            pass
        else:
            self.watch_user_data_call_back(message=message)
        
    leverageBrackets = None
    def get_leverage_brackets(self):
        try:
            if self.leverageBrackets is None:
                self.leverageBrackets = self.um_auth_http_client.synced("leverage_brackets")
            else:
                pass
        except Exception as exp:
            logger.debug(f'get_leverage_brackets-->{exp}')
        finally:
            pass

        return self.leverageBrackets
    
    dualSidePosition = False
    def getDualSidePosition(self, data: dict = None):
        return {'dualSidePosition': self.dualSidePosition}

    def get_position_mode(self):
        if self.um_auth_http_client is None:
            return
        try:
            dualInfo = self.um_auth_http_client.synced("get_position_mode")
            self.dualSidePosition = dualInfo['dualSidePosition']
        except Exception as exp:
            logger.debug(f'change_position_mode-->{exp}')
        finally:
            pass

    def changePositionMode(self, data: dict):
        dualSidePosition = data['dualSidePosition']
        self.change_position_mode(dualSidePosition=dualSidePosition)
        return {'code': 0, 'msg': 'success', 'data':{}}

    def change_position_mode(self, dualSidePosition: bool = True):
        if self.um_auth_http_client is None:
            return
        try:
            if dualSidePosition:
                self.um_auth_http_client.synced("change_position_mode", dualSidePosition='true')
            else:
                self.um_auth_http_client.synced("change_position_mode", dualSidePosition='false')
        except Exception as exp:
            logger.debug(f'change_position_mode-->{exp}')
        finally:
            pass

    def set_margin_type_for_symbol(self, data: dict):
        symbol = data['symbol']
        isolated = data['isolated']
        if isolated:
            marginType = 'ISOLATED'
        else:
            marginType = 'CROSSED'
        if self.um_auth_http_client is None:
            return
        try:
            self.um_auth_http_client.synced("change_margin_type", symbol=symbol, marginType=marginType)
        except Exception as exp:
            logger.debug(f'change_margin_type-->{exp}')
        finally:
            pass

    def set_leverage_for_symbol(self, data: dict):
        symbol = data['symbol']
        leverage = data['leverage']
        leverage = int(leverage)
        key = 'symbol_default_leverage'
        KVInfo.update(key=key, value=leverage)
        self.change_leverage(symbol=symbol, leverage=leverage)

    def change_leverage(self, symbol: str, leverage: str):
        if self.um_auth_http_client is None:
            return
        try:
            self.um_auth_http_client.synced("change_leverage", symbol=symbol, leverage=leverage)
        except Exception as exp:
            logger.debug(f'change_leverage-->{exp}')
        finally:
            pass
        
    def get_position_risk(self, data: dict):
        if self.um_auth_http_client is None:
            return
        try:
            symbol = data['symbol']
            positionRisk = self.um_auth_http_client.synced("get_position_risk", symbol=symbol)
        except Exception as exp:
            logger.debug(f'get_position_risk-->{exp}')
        finally:
            return positionRisk

    def get_max_leverage(self, data: dict):
        symbol = data['symbol']
        leverage_brackets = self.get_leverage_brackets()

        max_leverage = 1
        for l_info in leverage_brackets:
            if l_info['symbol'] == symbol:
                brackets = l_info['brackets']
                for b_info in brackets:
                    initial_leverage = int(b_info['initialLeverage'])
                    if initial_leverage > max_leverage:
                        max_leverage = initial_leverage

        key = 'symbol_default_leverage'
        default_leverage = KVInfo.get_value_by_key(key=key)
        if default_leverage is None:
            default_leverage = 10

        return {'maxLeverage': str(max_leverage), 'defaultLeverage': default_leverage}

    def get_usdt_balance(self, data: dict):
        return {'balance': str(self.usdt_balance())}

    def get_position_amount(self, data: dict):
        symbol = data['symbol']
        p_infos = {
            'longAmt': '0.0',
            'longQuote': '0.0',
            'shortAmt': '0.0',
            'shortQuote': '0.0'
        }
        
        p_list = self.getPositions().get(symbol, None)
        if p_list is None:
            return p_infos
        else:
            pass

        for p_info in p_list:
            positionSide = p_info['positionSide']
            positionAmt = p_info['positionAmt']
            entryPrice = p_info['entryPrice']
            positionValue = str(math.fabs(float(positionAmt))*float(entryPrice))
            if '-' in positionAmt:
                p_infos['shortAmt'] = positionAmt
                p_infos['shortQuote'] = positionValue
            else:
                p_infos['longAmt'] = positionAmt
                p_infos['longQuote'] = positionValue

        return p_infos

    # 适配小数精度
    def adapter_float(self, tick, f_num):
        tick_dec = Decimal(str(tick))
        num_dec = Decimal(str(f_num))
        # 使用ROUND_DOWN确保价格向下取整到tick_size的倍数
        adjusted_num = (num_dec / tick_dec).quantize(Decimal('1'), rounding=ROUND_DOWN) * tick_dec
        return str(adjusted_num)

    def fix_order_price(self, symbol: str, price: str):
        limit_infos = self.get_place_order_limit_infos(symbol=symbol)
        pricePrecision = limit_infos['pricePrecision']
        pricePrecision = int(pricePrecision)
        tickSize = limit_infos['tickSize']
        fixed_price = self.adapter_float(tick=tickSize, f_num=price)
        logger.debug(f'fixed_price---->{fixed_price}')

        return fixed_price

    def price_tick_size_for_symbol(self, symbol: str):
        limit_infos = self.get_place_order_limit_infos(symbol=symbol)
        pricePrecision = limit_infos['pricePrecision']
        pricePrecision = int(pricePrecision)
        tickSize = limit_infos['tickSize']
        if pricePrecision > 0:
            tickSize = float(tickSize)
        else:
            tickSize = int(tickSize)

        return tickSize

    def fix_order_amount(self, symbol: str, amount: str):
        limit_infos = self.get_place_order_limit_infos(symbol=symbol)
        quantityPrecision = limit_infos['quantityPrecision']
        quantityPrecision = int(quantityPrecision)
        stepSize = limit_infos['stepSize']
        fixed_amount = self.adapter_float(tick=stepSize, f_num=amount)
        # 如果fixed_amount是一个负数字符串,则将其转换为正数
        if fixed_amount.startswith('-'):
            fixed_amount = fixed_amount[1:]
        logger.debug(f'fixed_amount----{fixed_amount}')
        
        return fixed_amount

    def get_place_order_limit_infos(self, symbol: str):
        exchangeInfos = self.get_exchange_info()
        limit_infos = {}
        e_symbols = exchangeInfos['symbols']
        for s_infos in e_symbols:
            s_symbol = s_infos['symbol']
            if s_symbol == symbol:
                limit_infos['pricePrecision'] = s_infos['pricePrecision']
                limit_infos['quantityPrecision'] = s_infos['quantityPrecision']
                filters = s_infos['filters']
                for f_info in filters:
                    filterType = f_info['filterType']
                    if filterType == 'PRICE_FILTER':
                        limit_infos['maxPrice'] = f_info['maxPrice']
                        limit_infos['minPrice'] = f_info['minPrice']
                        limit_infos['tickSize'] = f_info['tickSize']
                    elif filterType == 'MIN_NOTIONAL':
                        limit_infos['notional'] = f_info['notional']
                    elif filterType == 'MARKET_LOT_SIZE':
                        limit_infos['maxQty'] = f_info['maxQty']
                        limit_infos['minQty'] = f_info['minQty']
                        limit_infos['stepSize'] = f_info['stepSize']
                    else:
                        pass
            else:
                pass
        return limit_infos

    def get_kline_infos(self, symbol: str, interval: str, limit: int = 499, start_time: str = None, end_time: str = None):
        kline_infos = []
        try:
            kline_infos = self.um_http_client.klines(symbol=symbol, interval=interval, limit=limit,
                                                                startTime=start_time, endTime=end_time)
        except Exception as exp:
            logger.debug(f'klines--->{exp}')
        finally:
            return kline_infos

    def get_24hr_quote_volume(self, symbol: str):
        ticker = self.getTickers().get(symbol, None)
        if ticker is None:
            return '0.0'
        quoteVolume = ticker['quoteVolume']

        return quoteVolume

    def get_last_price(self, symbol: str):
        ticker = self.getTickers().get(symbol, None)
        if ticker is None:
            return '0.0'
        lastPrice = ticker['lastPrice']

        return str(lastPrice)

    def get_all_usdt_symbol_list(self, data: dict):
        symbol_list = self.get_PERPETUAL_symbol_list()
        return {'symbol_list':symbol_list}

    # 获取永续合约交易对列表
    def get_PERPETUAL_symbol_list(self):
        usdt_symbol_list = []
        if self.tickers is None:
            return usdt_symbol_list
        else:
            pass
        for symbol in self.tickers.keys():
            if symbol.endswith('USDT'):
                usdt_symbol_list.append(symbol)
            else:
                pass

        return usdt_symbol_list

    def update_local_position_data(self):
        '''
        :param ticker: {
          "symbol": ws_ticker['s'],
          "priceChange": ws_ticker['p'],    #24小时价格变动
          "priceChangePercent": ws_ticker['P'],  #24小时价格变动百分比
          "weightedAvgPrice": ws_ticker['w'], #加权平均价
          "lastPrice": ws_ticker['c'],        #最近一次成交价
          "lastQty": ws_ticker['Q'],        #最近一次成交额
          "openPrice": ws_ticker['o'],       #24小时内第一次成交的价格
          "highPrice": ws_ticker['h'],      #24小时最高价
          "lowPrice": ws_ticker['l'],         #24小时最低价
          "volume": ws_ticker['v'],        #24小时成交量
          "quoteVolume": ws_ticker['q'],     #24小时成交额
          "openTime": ws_ticker['F'],        #24小时内，第一笔交易的发生时间
          "closeTime": ws_ticker['L'],       #24小时内，最后一笔交易的发生时间
          "firstId": ws_ticker['F'],   # 首笔成交id
          "lastId": ws_ticker['L'],    # 末笔成交id
          "count": ws_ticker['n']         # 成交笔数
        }
        :return:
        '''
        
        for symbol in self.getPositions().keys():
            p_list = self.getPositions().get(symbol, None)
            if p_list is None:
                # print('update_position_data_with_ticker---> p_list is None return')
                continue
            if len(p_list) > 0:
                # print(f'update_position_data_with_ticker {len(p_list)} { symbol } : { lastPrice }')
                ticker_info = self.tickers.get(symbol, None)
                if ticker_info is None:
                    # print('update_position_data_with_ticker---> ticker_info is None return')
                    continue
                lastPrice = ticker_info['lastPrice']
                for p_info in p_list:
                    '''
                    {
                        "symbol": "BTCUSDT",  # 交易对
                        "initialMargin": "0",   # 当前所需起始保证金(基于最新标记价格)
                        "maintMargin": "0" #维持保证金
                        "unrealizedProfit": "0.00000000",  # 持仓未实现盈亏
                        "positionInitialMargin": "0",  # 持仓所需起始保证金(基于最新标记价格)
                        "openOrderInitialMargin": "0",  # 当前挂单所需起始保证金(基于最新标记价格)
                        "leverage": "100",  # 杠杆倍率
                        "isolated": true,  # 是否是逐仓模式
                        "entryPrice": "0.00000",  # 持仓成本价
                        "maxNotional": "250000",  # 当前杠杆下用户可用的最大名义价值
                        "bidNotional": "0",  # 买单净值，忽略
                        "askNotional": "0",  # 买单净值，忽略
                        "positionSide": "BOTH",  # 持仓方向
                        "positionAmt": "0",      # 持仓数量
                        "updateTime": 0         # 更新时间
                    }
                    '''
                    symbol = p_info['symbol']
                    positionSide = p_info['positionSide']
                    entryPrice = p_info['entryPrice']
                    positionAmt = p_info['positionAmt']
                    curValue = float(positionAmt) * float(lastPrice)
                    entryValue = float(positionAmt) * float(entryPrice)

                    unrealizedProfit = curValue - entryValue
                    p_info['unrealizedProfit'] = unrealizedProfit
                    # print(f'{symbol} unrealizedProfit---->{unrealizedProfit}')
            else:
                pass

    def watch_ticker_call_back(self, message: list):
        # logger.debug(f'watch_ticker_call_back-->{message[0]}')
        try:
            if isinstance(message, list):
                for t_info in message:
                    e = t_info['e']
                    if e == '24hrTicker':
                        ticker_info = self.convert_ws_ticker_info_to_http(ws_ticker=t_info)
                    
                        symbol = ticker_info['symbol']
    
                        new_tickers = self.getTickers()
                        new_tickers[symbol] = ticker_info
                        self.tickers = new_tickers
                    else:
                        pass
            else:
                logger.debug(f'watch_ticker_call_back-->{message}')
        except Exception as exp:
            logger.debug(f'watch_ticker_call_back-->{exp}')
        finally:
            pass

    

    ticker_watching = False
    def watch_ticker(self):
        if self.ticker_watching:
            return
        else:
            pass
        self.um_ws_client.ticker(
            id=self.ms_ts()
        )
        self.ticker_watching = True

    def convert_ws_user_data_info_to_http(self, message):
        '''
        :param message: {
          "e": "ACCOUNT_UPDATE",                # 事件类型
          "E": 1564745798939,                   # 事件时间
          "T": 1564745798938 ,                  # 撮合时间
          "a":                                  # 账户更新事件
            {
              "m":"ORDER",                      # 事件推出原因
              "B":[                             # 余额信息
                {
                  "a":"USDT",                   # 资产名称
                  "wb":"122624.12345678",       # 钱包余额
                  "cw":"100.12345678",          # 除去逐仓仓位保证金的钱包余额
                  "bc":"50.12345678"            # 除去盈亏与交易手续费以外的钱包余额改变量
                },
                {
                  "a":"BUSD",
                  "wb":"1.00000000",
                  "cw":"0.00000000",
                  "bc":"-49.12345678"
                }
              ],
              "P":[
               {
                  "s":"BTCUSDT",            # 交易对
                  "pa":"0",                 # 仓位
                  "ep":"0.00000",            # 入仓价格
                  "cr":"200",               # (费前)累计实现损益
                  "up":"0",                     # 持仓未实现盈亏
                  "mt":"isolated",              # 保证金模式
                  "iw":"0.00000000",            # 若为逐仓，仓位保证金
                  "ps":"BOTH"                   # 持仓方向
               }，
               {
                    "s":"BTCUSDT",
                    "pa":"20",
                    "ep":"6563.66500",
                    "cr":"0",
                    "up":"2850.21200",
                    "mt":"isolated",
                    "iw":"13200.70726908",
                    "ps":"LONG"
                 },
               {
                    "s":"BTCUSDT",
                    "pa":"-10",
                    "ep":"6563.86000",
                    "cr":"-45.04000000",
                    "up":"-1423.15600",
                    "mt":"isolated",
                    "iw":"6570.42511771",
                    "ps":"SHORT"
               }
              ]
            }
        }
        :return:
        '''
        if message['e'] == 'listenKeyExpired':
            self.user_socket_ok = False
        else:
            pass

        m_T = message['T']
        m_a = message['a']
        if 'B' in m_a.keys():
            B = m_a['B']
            for b_info in B:
                a = b_info['a']
                wb = b_info['wb']
                cw = b_info['cw']
                bc = b_info['bc']
                a_info = self.getAssets().get(a, '0')
                a_info['walletBalance'] = wb
                a_info['availableBalance'] = cw
                a_info['unrealizedProfit'] = bc
        else:
            pass

        if 'P' in m_a.keys():
            P = m_a['P']
            for p_i in P:
                s = p_i['s'] # 交易对
                pa = p_i['pa'] # 仓位
                ep = p_i['ep'] # 入仓价格
                cr = p_i['cr'] # (费前) 累计实现损益
                up = p_i['up'] # 持仓未实现盈亏
                mt = p_i['mt'] # 保证金模式
                iw = p_i['iw'] # 若为逐仓，仓位保证金
                ps = p_i['ps'] # 持仓方向
                if float(pa) == 0.0:
                    # 清空了仓位
                    # 取消止盈止损订单,如果有的话
                    open_orders = self.getOpenOrders().get(s, None)
                    if open_orders is None:
                        continue
                    if ps == 'BOTH':
                        pass
                    elif ps == 'LONG':
                        for od_info in open_orders:
                            od_ps = od_info['positionSide']
                            sd = od_info['side']
                            if od_ps == 'LONG' and sd == 'SELL':
                                self.delete_open_order(data=od_info)
                            else:
                                pa
                    elif ps == 'SHORT':
                        for od_info in open_orders:
                            od_ps = od_info['positionSide']
                            sd = od_info['side']
                            if od_ps == 'SHORT' and sd == 'BUY':
                                self.delete_open_order(data=od_info)
                            else:
                                pass
                    else:
                        pass
                else:
                    pass
            if len(P) > 0:
                # 用户仓位信息有更新
                self.init_user_data_infos()
            else:
                pass
        else:
            pass

    def convert_ws_order_info_to_http(self, message):
        '''
        :param message: {
          "e":"ORDER_TRADE_UPDATE",         # 事件类型
          "E":1568879465651,                # 事件时间
          "T":1568879465650,                # 撮合时间
          "o":{
            "s":"BTCUSDT",                  # 交易对
            "c":"TEST",                     # 客户端自定订单ID
              # 特殊的自定义订单ID:
              # "autoclose-"开头的字符串: 系统强平订单
              # "adl_autoclose": ADL自动减仓订单
              # "settlement_autoclose-": 下架或交割的结算订单
            "S":"SELL",                     # 订单方向
            "o":"TRAILING_STOP_MARKET" # 订单类型
            "f":"GTC",                      # 有效方式
            "q":"0.001",                    # 订单原始数量
            "p":"0",                        # 订单原始价格
            "ap":"0",                       # 订单平均价格
            "sp":"7103.04",                 # 条件订单触发价格，对追踪止损单无效
            "x":"NEW",                      # 本次事件的具体执行类型
            "X":"NEW",                      # 订单的当前状态
            "i":8886774,                    # 订单ID
            "l":"0",                        # 订单末次成交量
            "z":"0",                        # 订单累计已成交量
            "L":"0",                        # 订单末次成交价格
            "N": "USDT",                    # 手续费资产类型
            "n": "0",                       # 手续费数量
            "T":1568879465650,              # 成交时间
            "t":0,                          # 成交ID
            "b":"0",                        # 买单净值
            "a":"9.91",                     # 卖单净值
            "m": false,                     # 该成交是作为挂单成交吗？
            "R":false   ,                   # 是否是只减仓单
            "wt": "CONTRACT_PRICE",         # 触发价类型
            "ot": "TRAILING_STOP_MARKET",   # 原始订单类型
            "ps":"LONG"                     # 持仓方向
            "cp":false,                     # 是否为触发平仓单; 仅在条件订单情况下会推送此字段
            "AP":"7476.89",                 # 追踪止损激活价格, 仅在追踪止损单时会推送此字段
            "cr":"5.0",                     # 追踪止损回调比例, 仅在追踪止损单时会推送此字段
            "pP": false,              # 忽略
            "si": 0,                  # 忽略
            "ss": 0,                  # 忽略
            "rp":"0"                       # 该交易实现盈亏
          }

        }
        :return:
        '''
        od_info = message['o']
        od_T = message['T']
        order_info = {
            "avgPrice": od_info['ap'],              # 平均成交价
            "clientOrderId": od_info['c'],             # 用户自定义的订单号
            "cumQuote": str(float(od_info['z'])*float(od_info['ap'])),                        # 成交金额
            "executedQty": od_info['z'],                 # 成交量
            "orderId": od_info['i'],                # 系统订单号
            "origQty": od_info['q'],                  # 原始委托数量
            "origType": od_info['ot'], # 触发前订单类型
            "price": od_info['p'],                   # 委托价格
            "reduceOnly": od_info['R'],                # 是否仅减仓
            "side": od_info['S'],                      # 买卖方向
            "positionSide": od_info['ps'], # 持仓方向
            "status": od_info['X'],                    # 订单状态
            "stopPrice": od_info['sp'],                    # 触发价，对`TRAILING_STOP_MARKET`无效
            "closePosition": od_info['cp'] if 'cp' in od_info.keys() else False,   # 是否条件全平仓
            "symbol": od_info['s'],                # 交易对
            "time": od_info['T'],              # 订单时间
            "timeInForce": od_info['f'],               # 有效方法
            "type": od_info['o'],     # 订单类型
            "activatePrice": od_info['AP'] if 'AP' in od_info.keys() else '0.0', # 跟踪止损激活价格, 仅`TRAILING_STOP_MARKET` 订单返回此字段
            "priceRate": od_info['cr'] if 'cr' in od_info.keys() else '0.0', # 跟踪止损回调比例, 仅`TRAILING_STOP_MARKET` 订单返回此字段
            "updateTime": od_T,        # 更新时间
            "workingType": od_info['wt'], # 条件价格触发类型
            "priceProtect": True            # 是否开启条件单触发保护
        }

        symbol = order_info['symbol']
        if order_info['status'] == 'FILLED' and order_info['type'] != 'MARKET':
            logger.debug(f'限价单完全成交')
            self.update_open_orders_for_symbol(symbol=order_info['symbol'])
            message = f'{symbol}限价单已成交'
            self.call_js_method("showMessage", {'message': message, 'type': 'success'})
            self.create_stop_or_profit_order_if_need(order_info)
        elif order_info['status'] == 'NEW' and order_info['type'] != 'MARKET':
            logger.debug(f'新的限价单')
            self.update_open_orders_for_symbol(symbol=order_info['symbol'])
        elif order_info['status'] == 'CANCELED' or order_info['status'] == 'EXPIRED':
            logger.debug(f'订单取消或过期')
            self.update_open_orders_for_symbol(symbol=order_info['symbol'])
            message = f'{symbol}订单已取消'
            self.call_js_method("showMessage", {'message': message, 'type': 'success'})
            self.create_stop_or_profit_order_if_need(order_info)
        else:
            '''
            NEW
            PARTIALLY_FILLED
            FILLED
            CANCELED
            EXPIRED
            '''
            pass
        if order_info['status'] == 'FILLED':
            self.send_order_filled_notify(data=order_info)
        else:
            pass

    def create_stop_or_profit_order_if_need(self, order_info: dict):
        logger.debug(f'create_stop_or_profit_order_if_need--0-->', order_info)
        order_info_list = KVInfo.get_value_by_key(key='k_save_stop_and_profit_order_info_list')
        if order_info_list is None:
            return
        else:
            if len(order_info_list) < 1:
                return
            else:
                pass
        order_info_keys = order_info.keys()
        if 'clientOrderId' in order_info_keys:
            cur_orderId = order_info['clientOrderId']
        else:
            cur_orderId = order_info['orderId']
        final_order_info_list = []
        for od_info in order_info_list:
            old_order_info = od_info['order_info']
            old_order_info_keys = old_order_info.keys()
            if 'clientOrderId' in old_order_info_keys:
                old_orderId = old_order_info['clientOrderId']
            elif 'orderId' in old_order_info_keys:
                old_orderId = old_order_info['orderId']
            else:
                continue
            if cur_orderId == old_orderId:
                logger.debug(f'create_stop_or_profit_order_if_need--1-->', od_info)
                if order_info['status'] == 'CANCELED':
                    continue
                else:
                    pass
                loss_price = od_info['loss_price']
                profit_price = od_info['profit_price']
                origQty = order_info['origQty']
                if '-' in origQty:
                    positionSide = "SHORT"
                else:
                    positionSide = "LONG"
                symbol = order_info['symbol']
                self.create_clear_position_order_by_limit(data={
                    'symbol': symbol,
                    'price': loss_price,
                    'positionSide': positionSide,
                    'origQty': origQty
                })
                self.create_clear_position_order_by_limit(data={
                    'symbol': symbol,
                    'price': profit_price,
                    'positionSide': positionSide,
                    'origQty': origQty
                })
            else:
                final_order_info_list.append(od_info)
        KVInfo.update(key='k_save_stop_and_profit_order_info_list', value=final_order_info_list)

    def update_open_orders_for_symbol(self, symbol: str):
        if self.um_auth_http_client is None:
            return
        try:
            order_infos = self.um_auth_http_client.synced("get_orders",symbol=symbol)
            self.openOrders[symbol] = order_infos
        except Exception as exp:
            logger.debug(f'get_orders--->{exp}')
        finally:
            pass

    def watch_user_data_call_back(self, message):
        logger.debug(f'watch_user_data_call_back-->{message}')
        try:
            if isinstance(message, dict):
                if 'e' in message.keys():
                    e = message['e']
                    if e =='ACCOUNT_UPDATE': #Balance和Position更新推送
                        self.convert_ws_user_data_info_to_http(message=message)
                    elif e =='ORDER_TRADE_UPDATE': #订单/交易 更新推送
                        self.convert_ws_order_info_to_http(message=message)
                    else:
                        pass
                else:
                    pass
            else:
                pass
        except Exception as exp:
            logger.debug(f'watch_user_data_call_back-error->{exp}')
        finally:
            pass

    def update_listen_key(self):
        if self.um_auth_http_client is None:
            return
        try:
            self.um_auth_http_client.renew_listen_key(listenKey=self.listenKey)
            # 重新启动定时器
            self.start_listen_key_update_timer()
            self.user_socket_ok = True
        except Exception as exp:
            logger.debug(f'renew_listen_key--->{exp}')
            self.user_socket_ok = False
        finally:
            pass

    def init_open_orders(self, force: bool = False):
        '''
        [
          {
            "avgPrice": "0.00000",              # 平均成交价
            "clientOrderId": "abc",             # 用户自定义的订单号
            "cumQuote": "0",                        # 成交金额
            "executedQty": "0",                 # 成交量
            "orderId": 1917641,                 # 系统订单号
            "origQty": "0.40",                  # 原始委托数量
            "origType": "TRAILING_STOP_MARKET" # 触发前订单类型
            "price": "0",                   # 委托价格
            "reduceOnly": false,                # 是否仅减仓
            "side": "BUY",                      # 买卖方向
            "positionSide": "SHORT" # 持仓方向
            "status": "NEW",                    # 订单状态
            "stopPrice": "9300",                    # 触发价，对`TRAILING_STOP_MARKET`无效
            "closePosition": false,   # 是否条件全平仓
            "symbol": "BTCUSDT",                # 交易对
            "time": 1579276756075,              # 订单时间
            "timeInForce": "GTC",               # 有效方法
            "type": "TRAILING_STOP_MARKET",     # 订单类型
            "activatePrice": "9020" # 跟踪止损激活价格, 仅`TRAILING_STOP_MARKET` 订单返回此字段
            "priceRate": "0.3" # 跟踪止损回调比例, 仅`TRAILING_STOP_MARKET` 订单返回此字段
            "updateTime": 1579276756075,        # 更新时间
            "workingType": "CONTRACT_PRICE" # 条件价格触发类型
            "priceProtect": false            # 是否开启条件单触发保护
          }
        ]
        :return:
        '''
        if self.um_auth_http_client is None:
            return
        
        try:
            order_infos = self.um_auth_http_client.synced("get_orders")
            new_openOrders = {}
            for od_info in order_infos:
                symbol = od_info['symbol']
                od_list = []
                if symbol in new_openOrders.keys():
                    od_list = new_openOrders[symbol]
                else:
                    new_openOrders[symbol] = od_list
                od_list.append(od_info)
            self.openOrders = new_openOrders
            self.cancel_stop_and_profit_order_if_no_position()
        except Exception as exp:
            logger.debug(f'get_orders--->{exp}')
        finally:
            pass

    def get_open_orders_by_symbol(self, symbol: str):
        '''
        [
          {
            "avgPrice": "0.00000",              # 平均成交价
            "clientOrderId": "abc",             # 用户自定义的订单号
            "cumQuote": "0",                        # 成交金额
            "executedQty": "0",                 # 成交量
            "orderId": 1917641,                 # 系统订单号
            "origQty": "0.40",                  # 原始委托数量
            "origType": "TRAILING_STOP_MARKET" # 触发前订单类型
            "price": "0",                   # 委托价格
            "reduceOnly": false,                # 是否仅减仓
            "side": "BUY",                      # 买卖方向
            "positionSide": "SHORT" # 持仓方向
            "status": "NEW",                    # 订单状态
            "stopPrice": "9300",                    # 触发价，对`TRAILING_STOP_MARKET`无效
            "closePosition": false,   # 是否条件全平仓
            "symbol": "BTCUSDT",                # 交易对
            "time": 1579276756075,              # 订单时间
            "timeInForce": "GTC",               # 有效方法
            "type": "TRAILING_STOP_MARKET",     # 订单类型
            "activatePrice": "9020" # 跟踪止损激活价格, 仅`TRAILING_STOP_MARKET` 订单返回此字段
            "priceRate": "0.3" # 跟踪止损回调比例, 仅`TRAILING_STOP_MARKET` 订单返回此字段
            "updateTime": 1579276756075,        # 更新时间
            "workingType": "CONTRACT_PRICE" # 条件价格触发类型
            "priceProtect": false            # 是否开启条件单触发保护
          }
        ]
        :return:
        '''
        if self.um_auth_http_client is None:
            return
        try:
            order_infos = self.um_auth_http_client.synced("get_orders", symbol=symbol)
            self.openOrders[symbol] = order_infos
        except Exception as exp:
            logger.debug(f'get_open_orders_by_symbol--->{exp}')
            order_infos = []
        finally:
            return order_infos

    def delete_faker_open_order(self, data: dict):
        clientOrderId = data['clientOrderId']
        temp_faker_order_list = []
        for order_info in self.faker_order_list:
            '''
            {
                'symbol':symbol, 
                'side':side, 
                'positionSide':positionSide, 
                'type':type,
                'quantity':amount, 
                'newClientOrderId':newClientOrderId, 
                'price':price, 
                'stopPrice':stopPrice,
                'trigger_price': trigger_price,
                'enter_type': lastPrice
            }
            '''
            if order_info['clientOrderId'] == clientOrderId:
                pass
            else:
                temp_faker_order_list.append(order_info)
        if len(temp_faker_order_list) != len(self.faker_order_list):
            self.faker_order_list = temp_faker_order_list
            KVInfo.update(key=self.faker_order_list_key, value=temp_faker_order_list)
        else:
            pass
            

    def delete_open_order(self, data: dict):
        result = data
        if self.um_auth_http_client is None:
            return
        try:
            symbol = data['symbol']
            clientOrderId = data['clientOrderId']
            result = self.um_auth_http_client.synced("cancel_order",symbol=symbol, origClientOrderId=clientOrderId)
            od_list = self.getOpenOrders().get(symbol, None)
            if od_list is None:
                return result
            temp_od_list = []
            for od_info in od_list:
                od_id = od_info['clientOrderId']
                if od_id == clientOrderId:
                    pass
                else:
                    temp_od_list.append(od_info)
            self.openOrders[symbol] = temp_od_list
        except Exception as exp:
            logger.debug(f'delete_open_order--->{exp}')
        finally:
            return result
    
    def delete_open_order_by_id(self, symbol: str, order_id: str):
        if self.um_auth_http_client is None:
            return
        try:
            result = self.um_auth_http_client.synced("cancel_order",symbol=symbol, orderId=order_id)
        except Exception as exp:
            logger.debug(f'delete_open_order_by_id--->{exp}')
            result = None
        finally:
            return result
        
    def get_open_order_by_id(self, symbol: str, order_id: str):
        result = None
        try:
            od_list = self.getOpenOrders().get(symbol, None)
            if od_list is None:
                return result
            for od_info in od_list:
                if od_info['orderId'] == order_id:
                    result = od_info
                    break
                elif od_info['clientOrderId'] == order_id:
                    result = od_info
                    break
                else:
                    pass
        except Exception as exp:
            logger.debug(f'get_open_order_by_id--->{exp}')
            result = None
        finally:
            return result
    
    def get_income_history(self, data: dict):
        income_history = []
        if self.um_auth_http_client is None:
            return
        try:
            income_history = self.um_auth_http_client.synced("get_income_history", incomeType='REALIZED_PNL')
            income_history.reverse()
        except Exception as exp:
            logger.debug(f'get_income_history--->{exp}')
        finally:
            result = {'income_history': income_history}
            return result


    def cancel_stop_and_profit_order_if_no_position(self):
        if self.dualSidePosition == False:
            return 
        else:
            pass
        def cancel_orders_if_need(od_list: list):
            for od_info in od_list:
                side = od_info['side']
                positionSide = od_info['positionSide']
                type = od_info['type']
                is_clear_order = (type == 'STOP_MARKET' or type == 'TAKE_PROFIT_MARKET' or type == 'TRAILING_STOP_MARKET')
                if positionSide == "BOTH":
                    pass
                else:
                    if side == 'SELL' and positionSide == 'LONG' and is_clear_order:
                        self.delete_open_order(data=od_info)
                    elif side == 'BUY' and positionSide == 'SHORT' and is_clear_order:
                        self.delete_open_order(data=od_info)
                    else:
                        pass
     
        for p_symbol in self.getPositions().keys():  # 没有仓位
            p_list = self.getPositions().get(p_symbol, None)
            if p_list is None:
                continue
            if p_symbol in self.getOpenOrders().keys():
                od_list = self.getOpenOrders().get(p_symbol, None)
                if od_list is None:
                    continue
                if len(p_list) == 0 and len(od_list) != 0: # 没有仓位了, 删除所有的止盈止损单
                    cancel_orders_if_need(od_list)
                else:
                    vaild_orders = []
                    for p_info in p_list:
                        p_positionSide = p_info['positionSide']
                        for od_info in od_list:
                            o_positionSide = od_info['positionSide']
                            type = od_info['type']
                            is_clear_order = (type == 'STOP_MARKET' or type == 'TAKE_PROFIT_MARKET' or type == 'TRAILING_STOP_MARKET')
                            if p_positionSide == o_positionSide and is_clear_order:
                                vaild_orders.append(od_info)
                            else:
                                pass
                    invaild_orders = []
                    for od_info in od_list:
                        if od_info not in vaild_orders:
                            invaild_orders.append(od_info)
                        else:
                            pass
                    cancel_orders_if_need(invaild_orders)

    def init_user_data_infos(self, force: bool = False):
        '''
        {
            "feeTier": 0,  # 手续费等级
            "canTrade": true,  # 是否可以交易
            "canDeposit": true,  # 是否可以入金
            "canWithdraw": true # 是否可以出金
            "updateTime": 0,     # 保留字段，请忽略
            "multiAssetsMargin": true,
            "totalInitialMargin": "0.00000000",  # 以USD计价的所需起始保证金总额
            "totalMaintMargin": "0.00000000",  # 以USD计价的维持保证金总额
            "totalWalletBalance": "126.72469206",   # 以USD计价的账户总余额
            "totalUnrealizedProfit": "0.00000000",  # 以USD计价的持仓未实现盈亏总额
            "totalMarginBalance": "126.72469206",  # 以USD计价的保证金总余额
            "totalPositionInitialMargin": "0.00000000",  # 以USD计价的持仓所需起始保证金(基于最新标记价格)
            "totalOpenOrderInitialMargin": "0.00000000",  # 以USD计价的当前挂单所需起始保证金(基于最新标记价格)
            "totalCrossWalletBalance": "126.72469206",  # 以USD计价的全仓账户余额
            "totalCrossUnPnl": "0.00000000",    # 以USD计价的全仓持仓未实现盈亏总额
            "availableBalance": "126.72469206",       # 以USD计价的可用余额
            "maxWithdrawAmount": "126.72469206"     # 以USD计价的最大可转出余额
            "assets": [
                {
                    "asset": "USDT",        #资产
                    "walletBalance": "23.72469206",  #余额
                    "unrealizedProfit": "0.00000000",  # 未实现盈亏
                    "marginBalance": "23.72469206",  # 保证金余额
                    "maintMargin": "0.00000000",    # 维持保证金
                    "initialMargin": "0.00000000",  # 当前所需起始保证金
                    "positionInitialMargin": "0.00000000",  # 持仓所需起始保证金(基于最新标记价格)
                    "openOrderInitialMargin": "0.00000000" # 当前挂单所需起始保证金(基于最新标记价格)
                    "crossWalletBalance": "23.72469206",  #全仓账户余额
                    "crossUnPnl": "0.00000000" # 全仓持仓未实现盈亏
                    "availableBalance": "23.72469206",       # 可用余额
                    "maxWithdrawAmount": "23.72469206",     # 最大可转出余额
                    "marginAvailable": true,   # 是否可用作联合保证金
                    "updateTime": 1625474304765  #更新时间
                },
                {
                    "asset": "BUSD",        #资产
                    "walletBalance": "103.12345678",  #余额
                    "unrealizedProfit": "0.00000000",  # 未实现盈亏
                    "marginBalance": "103.12345678",  # 保证金余额
                    "maintMargin": "0.00000000",    # 维持保证金
                    "initialMargin": "0.00000000",  # 当前所需起始保证金
                    "positionInitialMargin": "0.00000000",  # 持仓所需起始保证金(基于最新标记价格)
                    "openOrderInitialMargin": "0.00000000" # 当前挂单所需起始保证金(基于最新标记价格)
                    "crossWalletBalance": "103.12345678",  #全仓账户余额
                    "crossUnPnl": "0.00000000" # 全仓持仓未实现盈亏
                    "availableBalance": "103.12345678",       # 可用余额
                    "maxWithdrawAmount": "103.12345678",     # 最大可转出余额
                    "marginAvailable": true,   # 否可用作联合保证金
                    "updateTime": 0  # 更新时间
                    }
            ],
            "positions": [  # 头寸，将返回所有市场symbol。
                #根据用户持仓模式展示持仓方向，即单向模式下只返回BOTH持仓情况，双向模式下只返回 LONG 和 SHORT 持仓情况
                {
                    "symbol": "BTCUSDT",  # 交易对
                    "initialMargin": "0",   # 当前所需起始保证金(基于最新标记价格)
                    "maintMargin": "0" #维持保证金
                    "unrealizedProfit": "0.00000000",  # 持仓未实现盈亏
                    "positionInitialMargin": "0",  # 持仓所需起始保证金(基于最新标记价格)
                    "openOrderInitialMargin": "0",  # 当前挂单所需起始保证金(基于最新标记价格)
                    "leverage": "100",  # 杠杆倍率
                    "isolated": true,  # 是否是逐仓模式
                    "entryPrice": "0.00000",  # 持仓成本价
                    "maxNotional": "250000",  # 当前杠杆下用户可用的最大名义价值
                    "bidNotional": "0",  # 买单净值，忽略
                    "askNotional": "0",  # 买单净值，忽略
                    "positionSide": "BOTH",  # 持仓方向
                    "positionAmt": "0",      # 持仓数量
                    "updateTime": 0         # 更新时间
                }
            ]
        }
        :return:
        '''
        if self.um_auth_http_client is None:
            print(f"init_user_data_infos self.um_auth_http_client is None {self.ba_api_key}")
            return
        else:
            pass
        if self.ba_api_key is None:
            return
        if self.ba_api_key == "":
            return
        if self.ba_secret_key is None:
            return
        if self.ba_secret_key == "":
            return
        
        try:
            user_datas = self.um_auth_http_client.synced("account")
            assets = user_datas['assets']
            new_assets = {}
            for a_info in assets:
                asset = a_info['asset']
                new_assets[asset] = a_info
            self.assets = new_assets

            positions = user_datas['positions']
            new_positions = {}
            for p_info in positions:
                symbol = p_info['symbol']
                p_list = []
                if symbol in new_positions.keys():
                    p_list = new_positions[symbol]
                else:
                    new_positions[symbol] = p_list
                positionAmt = p_info['positionAmt']
                if float(positionAmt) != 0.0:
                    p_list.append(p_info)
                else:
                    pass
            self.positions = new_positions
        except Exception as exp:
            logger.debug(f'account--->{exp}')
        finally:
            pass

    def usdt_balance(self):
        availableBalance = '0.0'
        if self.getAssets() == {}:
            return '0.0'
        else:
            try:
                b_info = self.assets['USDT']
                availableBalance = b_info['availableBalance']
            except Exception as exp:
                availableBalance = '0.0'
                logger.debug(f'usdt_balance--->{exp}')
            finally:
                return availableBalance

    def start_update_local_info_timer(self):
        self.updateInfoTimer = Timer(1, self.update_local_infos)
        self.updateInfoTimer.start()

    def start_listen_key_update_timer(self):
        self.updateListenKeyTimer = Timer(29 * 60, self.update_listen_key)
        self.updateListenKeyTimer.start()

    def start_watch_user_data(self, data: dict):
        self.watch_user_data()

    user_data_watching = False
    def watch_user_data(self):
        print('watch_user_data----0')
        if self.ba_api_key is None:
            print('watch_user_data----1')
            return
        else:
            pass
        if self.user_data_watching:
            print('watch_user_data----2')
            return
        else:
            pass
        if self.um_auth_ws_client is None:
            print('um_auth_ws_client----2.1')
            return
        else:
            pass
        print('watch_user_data----3')
        try:
            print('watch_user_data----4')
            self.start_listen_key_update_timer()
            print('watch_user_data----5')
            listenKeyInfos = self.um_auth_http_client.new_listen_key()
            print('watch_user_data----6')
            self.listenKey = listenKeyInfos["listenKey"]
            self.user_socket_ok = True
            self.um_auth_ws_client.user_data(
                listen_key=self.listenKey,
                id=self.ms_ts()
            )
            self.user_data_watching = True
            print('watch_user_data----7')
        except Exception as exp:
            logger.debug(f'new_listen_key--->{exp}')
            print('watch_user_data----8')
            self.user_socket_ok = False
        finally:
            print('watch_user_data----9')

    def stop_watch(self):
        try:
            if self.um_ws_client is not None:
                try:
                    self.um_ws_client.stop()
                    del self.um_ws_client
                    self.um_ws_client = None
                except Exception as exp:
                    logger.debug(f'stop_watch--1-->{exp}')
                finally:
                    pass      
            else:
                pass
        except Exception as exp:
            logger.debug(f'stop_watch--2-->{exp}')
        finally:
            pass

