# 

import time
from .SignalEngine import CustomIndicator, CustomSignal, SignalEngine
import requests
import datetime, sys
import pyperclip
import traceback
from tw_api.server.dbmodels.kv_info import KVInfo
from tw_api.trader.binance_trader.BAClient import BAClient
from tw_api.server.dbmodels.trade_signal import TradeSignalInfo
from tw_api.utils.path_tools import PathTools
import os
import json
from tw_api.utils.sound_tools import AudioTools
from .default_values import default_place_order_config, default_preferences
import asyncio
import aiohttp
import subprocess
from threading import Timer
from tw_api.const import is_Linux, is_Windows, is_MacOS
from tw_api.trader.binance_trader.UMBinance import UMBinance
from tw_api.utils.logger_tools import logger
import webbrowser
from tw_api.config import ScriptEnginerVersion

class BridgeTool(BAClient):
    appInfoConfig = {}
    klines_list_infos = {}

    def get_app_version(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        if is_Windows:
            version_key = 'latest_version_win'
        elif is_MacOS:
            version_key = 'latest_version_mac'
        else:
            version_key = 'latest_version_linux'

        return {'app_version': self.APP_VERSION, 'version_key': version_key}

    def copyCustomCode(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        price = data['text']
        pyperclip.copy(price)  # 复制
        self.call_js_method("showMessage", {'message': '源码已复制到粘贴板', 'type': 'success'})

    def copyText(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        text = data['text']
        pyperclip.copy(text)  # 复制
        self.call_js_method("showMessage", {'message': '已复制: ' + text, 'type': 'success'})

        return {'code':0, 'msg':'success', 'data':{}}

    def openWebUrlByDefaultBrowser(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        webbrowser.open(data["web_url"])

    def open_file_url(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        file_url = data["file_url"]
        if is_MacOS:								# Mac
            subprocess.call(['open', file_url])
        elif is_Linux:								# Linux
            subprocess.call(['xdg-open', file_url])
        else:																# Windows
            os.startfile(file_url)

class BridgeServer(BridgeTool):

    def get_trading_view_storage_url(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        chartsStorageUrl = PathTools.auto_complete_http_url(sub_url='/tradingview/charts/storage')
        return {'chartsStorageUrl':chartsStorageUrl}
    
    async def async_http_request(self, data: dict):
        async with aiohttp.ClientSession(self.API_HOST) as session:
            resp_data = None
            try:
                params = data['params']
                url_path = data['url_path']
                params['app_version'] = self.APP_VERSION
                async with session.post(self.API_PATH, json=data) as resp:
                    data = await resp.read()
                    resp_json = json.loads(data)
                    resp_code = resp_json['code']
                    resp_data = resp_json['data']
                    resp_msg = resp_json['msg']
                    if str(resp_code) == '0':
                        pass
                    else:
                        if url_path == '/user/infos':
                            resp_data['resp_code'] = resp_code
                        else:
                            resp_data = None
                            self.call_js_method("showMessage", {'message': resp_msg, 'type': 'error'})
            except Exception as exp:
                logger.debug(f'async_http_request--error-->{exp}, {data}')
                self.call_js_method("showMessage", {'message': str(exp), 'type': 'error'})
            finally:
                if resp_data is None:
                    pass
                elif isinstance(resp_data, dict):
                    pass
                else:
                    resp_data = {'data':resp_data}
            return resp_data
    
    def send_http_request(self, data: dict):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.async_http_request(data=data))
        loop.run_until_complete(task)
        resp_data = task.result()
        return resp_data
    

class BridgeBrowser(BridgeServer):

    def open_exchange_web_page_in_new_float_window( self, data: dict):
        print(datetime.datetime.now(), sys._getframe().f_code.co_name, data)
        url_path = data['url_path']
        webbrowser.open(url_path)

class BridgeUser(BridgeBrowser):
    auto_complete_user_info_key = 'k_auto_complete_user_info_key'
    current_login_user_info_key = 'k_current_login_user_info_key'
    user_preferences_key = 'k_user_preferences_key'
    user_api_key_secret_key = 'k_user_api_key_secret_key'
    user_stared_symbols_key = 'k_user_stared_symbols_key'
    user_trade_system_key = 'k_user_trade_system_key'

    
    keyValueInfo = {}
    userInfo = {}
    userPrefer = {}
    priceAlertInfos = {}

    def set_user_trade_system_infos(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        KVInfo.update(key=self.user_trade_system_key, value=data)

    def get_user_trade_system_infos(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        trade_system_infos = KVInfo.get_value_by_key(key=self.user_trade_system_key)
        if trade_system_infos is not None:
            return trade_system_infos
        else:
            return {}
        
    def save_local_storage_to_cache(self, storage_str: str):
        KVInfo.update(key='k_local_storage_str_cache', value=storage_str)
    
    def fetch_local_storage_from_cache(self):
        storage_str = KVInfo.get_value_by_key(key='k_local_storage_str_cache')
        return storage_str

    def get_user_stared_symbols(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        symbol_list = KVInfo.get_value_by_key(key=self.user_stared_symbols_key)
        if symbol_list is not None:
            return {'symbol_list': symbol_list}
        else:
            return {'symbol_list': []}

    def add_or_remove_user_stared_symbols(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        symbol_list = data['symbol_list']
        KVInfo.update(key=self.user_stared_symbols_key, value=symbol_list)

    def delete_user_api_key_secret_infos(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        KVInfo.delete(key=self.user_api_key_secret_key)

    def get_user_api_key_secret_infos(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        user_api_infos = KVInfo.get_value_by_key(key=self.user_api_key_secret_key)
        if user_api_infos is not None:
            return user_api_infos
        else:
            return {}

    def set_user_preferences(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        KVInfo.update(key=self.user_preferences_key, value=data)
        self.userPrefer = data

    def get_user_preferences(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        user_preferences = KVInfo.get_value_by_key(key=self.user_preferences_key)
        if user_preferences is not None:
            self.userPrefer = user_preferences
            return user_preferences
        else:
            self.userPrefer = default_preferences
            return default_preferences


    def getAutoCompleteUserInfo(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        user_info = KVInfo.get_value_by_key(key=self.auto_complete_user_info_key)
        if user_info is not None:
            return user_info
        else:
            return {}


    def set_current_login_user_info(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        if len(data) < 1:
            return
        else:
            pass
        self.userInfo = data
        PathTools.u_email = data['email']
        KVInfo.update(key=self.current_login_user_info_key, value=data)
        KVInfo.sign_in(key=self.current_login_user_info_key, value=data)
        self.get_notify_config_info(data=data)

    def check_vip_status(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        if 'vip_expire_time' in self.userInfo.keys():
            vip_expire_time = self.userInfo['vip_expire_time']
            vip_expire_time = int(vip_expire_time)
            cur_ts = int(time.time())
            if cur_ts > vip_expire_time:
                return {'is_vip': False}
            else:
                return {'is_vip': True}
        else:
            return {'is_vip': False}

class BridgeChart(BridgeUser):
    open_new_chart_in_new_float_window = None
    open_replay_chart_in_new_float_window = None
    open_exchange_web_page_in_new_float_window = None
    

class BridgeTrader(BridgeChart):

    def start_watch_ticker_and_user_datas(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        if UMBinance.network_ok==False:
            self.call_js_method("showMessage", {'message': '网络错误', 'type': 'error'})
            return {'succeed': False}
        else:
            return {'succeed': True}

class BridgeIndicator(BridgeTrader):
    useing_indicator_key = 'k_useing_indicator_key'

    indicatorList = []

    def version_int_with_str(self, v_str: str):
        deploy_version = v_str
        deploy_version = deploy_version.replace('.', '')
        deploy_version = int(deploy_version)
        
        return deploy_version
    
    def convert_tv_interval_to_ba_interval(self, tv_interval: str):
        ba_interval = tv_interval
        if tv_interval == '1m' or tv_interval == '1':
            ba_interval = '1m'
        elif tv_interval == '3m' or tv_interval == '3':
            ba_interval = '3m'
        elif tv_interval == '5m' or tv_interval == '5':
            ba_interval = '5m'
        elif tv_interval == '15m' or tv_interval == '15':
            ba_interval = '15m'
        elif tv_interval == '30m' or tv_interval == '30':
            ba_interval = '30m'
        elif tv_interval.upper() == '1H' or tv_interval == '60':
            ba_interval = '1h'
        elif tv_interval.upper() == '4H' or tv_interval == '240':
            ba_interval = '4h'
        elif tv_interval.upper() == '6H' or tv_interval == '360':
            ba_interval = '6h'
        elif tv_interval.upper() == '8H' or tv_interval == '480':
            ba_interval = '8h'
        elif tv_interval.upper() == '12H' or tv_interval == '720':
            ba_interval = '12h'
        elif tv_interval.upper() == '1D' or tv_interval == 'D':
            ba_interval = '1d'
        elif tv_interval.upper() == '3D':
            ba_interval = '3d'
        elif tv_interval.upper() == 'W' or tv_interval.upper() == '1W':
            ba_interval = '1w'
        elif tv_interval.upper() == '1M' or tv_interval.upper() == 'M':
            ba_interval = '1M'
        else:
            ba_interval = None
        return ba_interval
    
    def get_klines_from_ivst(self, datafeed_url: str, symbol: str, interval: str, limit: int):
        ts = int(time.time())
        data_url = f'{datafeed_url}/history?symbol={symbol}&resolution={interval}&from={ts}&to={ts}&countback={limit}'
        # 用requests发送get请求获取K线数据
        try:
            response = requests.get(data_url)
            response.raise_for_status()
            resp_info = response.json()
            s = resp_info['s']
            if s == 'ok':
                '''
                {
                    s: "ok",
                    t: [1386493512, 1386493572, 1386493632, 1386493692],
                    c: [42.1, 43.4, 44.3, 42.8],
                    o: [41.0, 42.9, 43.7, 44.5],
                    h: [43.0, 44.1, 44.8, 44.5],
                    l: [40.4, 42.1, 42.8, 42.3],
                    v: [12000, 18500, 24000, 45000]
                }
                '''
                for i in range(len(resp_info['t'])):
                    kline_info = [int(resp_info['t'][i])*1000, resp_info['o'][i], resp_info['h'][i], resp_info['l'][i], resp_info['c'][i], resp_info['v'][i]]
                    klines.push(kline_info)
            else:
                klines = []
        except requests.exceptions.RequestException as e:
            logger.error(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {e}')
            klines = []
        finally:
            return klines
    
    def get_klines_for_cache(self, symbol: str, interval: str, forIvst: bool = False, datafeed_url: str = None):
        line_key = f'{symbol}_{interval}'
        cache_keys = self.klines_list_infos.keys()
        if interval in ['1', '3', '5']: # 时间周期太短不缓存K线数据
            if forIvst:
                klines = self.get_klines_from_ivst(datafeed_url=datafeed_url, symbol=symbol, interval=interval, limit=1000)
            else:
                ba_interval = self.convert_tv_interval_to_ba_interval(tv_interval=interval)
                klines = self.get_kline_infos(symbol=symbol, interval=ba_interval, limit=1000)
        else:
            if line_key in cache_keys:
                klines = self.klines_list_infos[line_key]
                if forIvst:
                    klines_new = self.get_klines_from_ivst(datafeed_url=datafeed_url, symbol=symbol, interval=interval, limit=99)
                else:
                    ba_interval = self.convert_tv_interval_to_ba_interval(tv_interval=interval)
                    klines_new = self.get_kline_infos(symbol=symbol, interval=ba_interval, limit=99)
                # 删除klines数组中的最后99条数据
                count_new = len(klines_new)
                klines = klines[:-count_new]
                klines.extend(klines_new)
            else:
                if forIvst:
                    klines = self.get_klines_from_ivst(datafeed_url=datafeed_url, symbol=symbol, interval=interval, limit=1000)
                else:
                    ba_interval = self.convert_tv_interval_to_ba_interval(tv_interval=interval)
                    klines = self.get_kline_infos(symbol=symbol, interval=ba_interval, limit=1000)
            self.klines_list_infos[line_key] = klines
        return klines

    def run_developing_indicator_code(self, data: dict):
        indicator_code = data['indicator_code']
        forIvst = data['forIvst']
        datafeed_url = data['datafeed_url']
        symbol = data['symbol']
        chart_klines = data['chart_klines']
        interval = data['interval'] # 1/3/5/15/30/60/120/240/480/720/1D(D)/3D/1W(W)/1M(M)
        ba_interval = self.convert_tv_interval_to_ba_interval(tv_interval=interval)
        if ba_interval is None:
            return {'idct_id': '', 'symbol':symbol,'interval':interval,'shape_infos':[]}
        else:
            pass
        if forIvst:
            klines = chart_klines
        else:
            klines = self.get_klines_for_cache(symbol=symbol, interval=interval)
        cstm_indicator = CustomIndicator(indicator_code)
        cstm_indicator.idct_id = 'developing_indicator'
        idct_result = {
            'idct_id': cstm_indicator.idct_id
        }
        try:
            resp: dict = cstm_indicator.main(symbol=symbol, interval=ba_interval, klines=klines)
            for key, value in resp.items():
                idct_result[key] = value
        except Exception as e:
            logger.error(f'CustomIndicator-->{e}')
            logger.error(f'CustomIndicator-->{traceback.format_exc()}')
        finally:
            pass

        return idct_result
    
    def use_developing_indicator_code(self, data: dict):
        indicator_code = data['indicator_code']
        cstm_indicator = CustomIndicator(indicator_code)
        useing_idct_list = self.get_useing_custom_indicator_infos(data=data)
        find_old = False
        for index in range(0, len(useing_idct_list)):
            idct_info = useing_idct_list[index]
            if idct_info['name'] == cstm_indicator.name:
                cstm_indicator.idct_id = idct_info['idct_id']
                idct_info_new = cstm_indicator.to_dict()
                idct_info_new['enable'] = True
                useing_idct_list[index] = idct_info_new
                find_old = True
                break
            else:
                pass
        if find_old:
            pass
        else:
            mts = str(int(time.time()*1000))
            cstm_indicator.idct_id = f'local_{mts}'
            idct_info = cstm_indicator.to_dict()
            idct_info['enable'] = True
            useing_idct_list.append(idct_info)
        self.save_custom_indicator_infos(data={"indicatorList": useing_idct_list})
        self.indicatorList = useing_idct_list
        return {}

    def get_shape_infos_from_useing_indicator_list(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        indicator_list = self.get_useing_custom_indicator_infos(data=data)
        forIvst = data['forIvst']
        datafeed_url = data['datafeed_url']
        symbol = data['symbol']
        interval = data['interval'] # 1/3/5/15/30/60/240/1D(D)/3D/1W(W)/1M(M)
        chart_klines = data['chart_klines']
        ba_interval = self.convert_tv_interval_to_ba_interval(tv_interval=interval)
        if ba_interval is None:
            return [{'idct_id': '', 'symbol':symbol,'interval':interval,'shape_infos':[]}]
        else:
            pass
        
        if forIvst:
            klines = chart_klines
        else:
            klines = self.get_klines_for_cache(symbol=symbol, interval=interval)
            
        shape_info_list = []
        if len(klines) < 10:
            return []
        else:
            try:
                for id_info in indicator_list:
                    s_id = id_info.get('s_id', '')
                    idct_id = id_info.get('idct_id', '')
                    custom_code = id_info.get('custom_code', '')
                    input_params = id_info.get('input_params', {})
                    if s_id == '':
                        s_id = idct_id
                    else:
                        pass
                    
                    custom_indicator = CustomIndicator(custom_code)
                    custom_indicator.input_params = input_params
                    shape_info = {}
                    shape_info['s_id'] = s_id
                    shape_info['idct_id'] = idct_id
                    shape_info_list.append(shape_info)
                    if id_info['enable'] == True:
                        try:
                            shape_result = custom_indicator.main(symbol=symbol, interval=ba_interval, klines=klines)
                            for key, value in shape_result.items():
                                shape_info[key] = value
                        except Exception as e:
                            logger.error(f'CustomIndicator-->{e}')
                            logger.error(f'CustomIndicator-->{traceback.format_exc()}')
                        finally:
                            pass
                    else:
                        pass
            except Exception as exp:
                logger.error(f'tv_shape_infos--error-->{exp}, {traceback.print_exc()}')
            finally:
                pass

        return shape_info_list

    def upate_indicator_input_params_infos(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        t_id = data['idct_id']
        temp_list = []
        for index in range(0, len(self.indicatorList)):
            id_info = self.indicatorList[index]
            if id_info['idct_id'] == t_id:
                temp_list.append(data)
            else:
                temp_list.append(id_info)
        self.save_custom_indicator_infos(data={"indicatorList": temp_list})
        self.indicatorList = temp_list

        return {'indicator_list': temp_list}
    
    def use_custom_indicator_info_on_market(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        s_id = data['s_id']
        custom_code = data['custom_code']
        custom_code = CustomIndicator.decrypt_code(custom_code)
        custom_indicator = CustomIndicator(custom_code=custom_code)
        custom_id_name = custom_indicator.name
        custom_indicator.idct_id = s_id
        custom_indicator.s_id = s_id
        deploy_version: str = custom_indicator.deploy_version
        deploy_version = self.version_int_with_str(v_str=deploy_version)
        cur_version = self.version_int_with_str(v_str=ScriptEnginerVersion)
        if deploy_version > cur_version:
            self.call_js_method("showMessage", {'message': f'软件版本过低,{custom_id_name}不兼容,请升级后继续使用!', 'type': 'error'})
            return {'code': 0, 'msg': '', 'data': {}}
        else:
            pass
        custom_indicator = custom_indicator.to_dict()
        custom_indicator['custom_code'] = custom_code
        custom_indicator['status'] = 'release'
        custom_indicator['enable'] = True
        custom_indicator['idct_id'] = s_id
        custom_indicator['s_id'] = s_id
        self.add_custom_indicator_info(custom_indicator)

        return {'code': 0, 'msg': '', 'data': {}}

    def add_custom_indicator_info(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        temp_list = [data]
        for id_info in self.indicatorList:
            try:
                if id_info['idct_id'] == data['idct_id']:
                    pass
                elif id_info['name'] == data['name']:
                    pass
                else:
                    temp_list.append(id_info)
            except Exception as exp:
                logger.debug(f'add_custom_indicator_info---->{exp}')
            finally:
                pass
        self.save_custom_indicator_infos(data={"indicatorList": temp_list})
        self.indicatorList = temp_list

        return {'code': 0, 'msg': '', 'data': {}}
    
    def remove_custom_indicator_info(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        t_id = data['idct_id']
        temp_list = []
        for index in range(0, len(self.indicatorList)):
            id_info = self.indicatorList[index]
            id_id = id_info['idct_id']
            if id_id == t_id:
                pass
            else:
                temp_list.append(id_info)
        self.save_custom_indicator_infos(data={"indicatorList": temp_list})
        self.indicatorList = temp_list

    def get_current_useing_custom_indicator_infos(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        indicator_list = self.get_useing_custom_indicator_infos(data=data)
        
        return { 'indicator_list' : indicator_list }
    
    def get_useing_custom_indicator_infos(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        indicator_list = KVInfo.get_value_by_key(key=self.useing_indicator_key)
        if indicator_list is None:
            indicator_list = []
        else:
            pass
        self.indicatorList = indicator_list
        return indicator_list

    def save_custom_indicator_infos(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        indicatorList = data["indicatorList"]
        KVInfo.update(key=self.useing_indicator_key, value=indicatorList)

    def set_deving_indicator_info(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        self.clear_deving_indicator_info(data)
        custom_code = data['custom_code']
        custom_indicator = CustomIndicator(custom_code=custom_code)
        custom_indicator = custom_indicator.to_dict()
        custom_indicator['custom_code'] = custom_code
        custom_indicator['status'] = 'developing'
        custom_indicator['s_id'] = 'developing_s_id'
        custom_indicator['enable'] = True
        self.add_custom_indicator_info(custom_indicator)
    

    def clear_deving_indicator_info(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        temp_list = []
        for index in range(0, len(self.indicatorList)):
            id_info = self.indicatorList[index]
            id_status = id_info['status']
            if id_status == 'developing':
                pass
            else:
                temp_list.append(id_info)
        self.save_custom_indicator_infos(data={'indicatorList': temp_list})
        self.indicatorList = temp_list

    def read_public_custom_indicator_info_to_market(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        custom_code = data['custom_code']
        custom_indicator: CustomIndicator = CustomIndicator(custom_code=custom_code)
        (format_ok, msg) = custom_indicator.format_check()
        if format_ok == False:
            self.call_js_method("showMessage", {'message': msg, 'type': 'error'})
            return
        else:
            pass
        result = {
            'script_info': {
                'name': custom_indicator.name,
                'version': custom_indicator.version,
                'deploy_version': ScriptEnginerVersion,
                'detail_url': custom_indicator.detail_url,
                'open_source': custom_indicator.open_source,
                'custom_code': custom_code,
            }
        }

        return result

class BridgeSignals(BridgeIndicator):
    signal_engine: SignalEngine = None
    deving_custom_signal_key = 'k_deving_custom_signal_key'
    useing_custom_signal_key = 'k_useing_custom_signal_key'

    customSignalInfo = {}

    def copy_custom_signal_info_code(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        author_id = data['author_id']
        token = self.userInfo['token']
        s_id = data['s_id']
        params = {
            'url_path': '/get/signal/custom/code',
            'params': {
                'token': token,
                's_id': s_id,
                'author_id': author_id,
            }
        }
        code_info = self.local_send_http_request(data=params)
        custom_code = code_info['custom_code']
        self.copyCustomCode(data={'text': custom_code})
        return code_info

    def use_custom_signal_info(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        author_id = data['author_id']
        token = self.userInfo['token']
        s_id = data['s_id']
        params = {
            'url_path': '/get/signal/custom/code',
            'params': {
                'token': token,
                's_id': s_id,
                'author_id': author_id,
            }
        }
        code_info = self.local_send_http_request(data=params)
        custom_code = code_info['custom_code']
        data['custom_code'] = custom_code
        customSignal = CustomSignal(custom_code=custom_code)
        deploy_version: str = customSignal.deploy_version
        deploy_version = self.version_int_with_str(v_str=deploy_version)
        cur_version = self.version_int_with_str(v_str=self.APP_VERSION)
        if deploy_version > cur_version:
            self.call_js_method("showMessage", {'message': '软件版本过低,请升级后继续使用!', 'type': 'error'})
            return
        else:
            pass
        customSignalDict = customSignal.to_dict()
        data.update(customSignalDict)
        self.customSignalInfo = data
        self.set_useing_custom_signal_info(data=data)
        return self.customSignalInfo

    def set_useing_custom_signal_info(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        KVInfo.update(key=self.useing_custom_signal_key, value=self.customSignalInfo)

    def get_useing_custom_signal_info(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        useing_s_info = KVInfo.get_value_by_key(key=self.useing_custom_signal_key)
        if useing_s_info is not None:
            self.customSignalInfo = useing_s_info
            return useing_s_info
        else:
            return {}

    def get_history_signal_infos(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        def auto_complete_image_url(info_list: list):
            final_info_list = []
            for s_info in info_list:
                image_url = s_info['image_url']
                s_info['image_url'] = f'{PathTools.serverDomain}{image_url}'
                final_info_list.append(dict(s_info))
            return final_info_list

        signal_info_list = TradeSignalInfo.get_all();
        signal_info_list.reverse()
        signal_info_list = auto_complete_image_url(info_list=signal_info_list)
        return {'signal_info_list': signal_info_list}

    def save_deving_signal_info(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        custom_code = data['custom_code']
        customSignal = CustomSignal(custom_code=custom_code)
        customSignalInfo = customSignal.to_dict()
        customSignalInfo['status'] = 'developing'
        self.customSignalInfo = customSignalInfo
        KVInfo.update(key=self.deving_custom_signal_key, value=customSignalInfo)
        KVInfo.update(key=self.useing_custom_signal_key, value=customSignalInfo)

    def delete_deving_signal_info(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        KVInfo.delete(key=self.deving_custom_signal_key)

    def get_deving_signal_info(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        dev_s_info = KVInfo.get_value_by_key(key=self.deving_custom_signal_key)
        if dev_s_info is not None:
            return dev_s_info
        else:
            return {}
        
    def stop_ws_sockets(self, data: dict):
        self.stop_monitor_trade_signal(data=data)
        self.stop_watch()

    def stop_monitor_trade_signal(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        if self.signal_engine is not None:
            self.signal_engine.stop_monitor_signal()
        else:
            pass

    def trade_signal_did_appear(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        # 保存新的信号数据
        TradeSignalInfo.save(data)
        
        params = {}
        symbol = data["symbol"]
        interval = data["interval"]
        
        params['title'] = f'{symbol}/{interval} 出现交易信号'
        params['message'] = data['signal_info']['detail_msg']
        params['type'] = 'success'
        params['duration'] = 15000
        params['noti_type'] = 'trade_signal'
        self.call_js_method("showNotification", params)
        a_path = PathTools.app_audio_file_dir().joinpath('signal_tip.wav')
        AudioTools.play_audio(str(a_path))
        send_msg_timer = Timer(5, self.send_trade_signal_notify, (data,))
        send_msg_timer.start()
        self.create_signal_order_list(data=data)

    def create_signal_order_list(self, data: dict):
        try:
            if self.user_socket_ok == False:
                self.call_js_method("showMessage", {'message': 'user_socket_ok == False', 'type': 'error'})
                self.send_exception_notify(data={'exception_msg':'用户数据监听异常!请及时处理!'})
                return
            else:
                pass
            symbol = data["symbol"]
            order_list = data['signal_info']['order_list']
            if order_list is None:
                pass
            else:
                for order_info in order_list:
                    positionSide = order_info['positionSide']
                    side = order_info['side']
                    type = order_info['type']
                    if positionSide.lower() == 'long' and side.lower() == 'buy' and type.lower() == 'market':
                        no_position = True
                        position_infos = self.get_position_amount(data={'symbol':symbol})
                        longAmt = position_infos['longAmt']
                        longAmt = float(longAmt)
                        shortAmt = position_infos['shortAmt']
                        shortAmt = float(shortAmt)
                        if abs(longAmt) > 0.0 or abs(shortAmt) > 0.0:
                            no_position = False
                        else:
                            no_position = True
                        if no_position:
                            self.open_position_by_market_with_value(data=order_info)
                        else:
                            return
                    elif positionSide.lower() == 'long' and side.lower() == 'sell' and type.lower() == 'market':
                        self.clear_position_by_market_with_value(data=order_info)
                    elif positionSide.lower() == 'short' and side.lower() == 'sell' and type.lower() == 'market':
                        no_position = True
                        position_infos = self.get_position_amount(data={'symbol':symbol})
                        longAmt = position_infos['longAmt']
                        longAmt = float(longAmt)
                        shortAmt = position_infos['shortAmt']
                        shortAmt = float(shortAmt)
                        if abs(longAmt) > 0.0 or abs(shortAmt) > 0.0:
                            no_position = False
                        else:
                            no_position = True
                        if no_position:
                            self.open_position_by_market_with_value(data=order_info)
                        else:
                            return
                    elif positionSide.lower() == 'short' and side.lower() == 'buy' and type.lower() == 'market':
                        self.clear_position_by_market_with_value(data=order_info)
                    elif positionSide.lower() == 'long' and side.lower() == 'buy' and type.lower() == 'limit':
                        self.open_position_by_limit_with_value(data=order_info)
                    elif positionSide.lower() == 'long' and side.lower() == 'sell' and type.lower() == 'limit':
                        self.clear_position_by_limit_with_value(data=order_info)
                    elif positionSide.lower() == 'short' and side.lower() == 'sell' and type.lower() == 'limit':
                        self.open_position_by_limit_with_value(data=order_info)
                    elif positionSide.lower() == 'short' and side.lower() == 'buy' and type.lower() == 'limit':
                        self.clear_position_by_limit_with_value(data=order_info)
                    elif positionSide.lower() == 'long' and side.lower() == 'buy' and type.lower() == 'trailing':
                        pass
                    elif positionSide.lower() == 'long' and side.lower() == 'sell' and type.lower() == 'trailing':
                        self.create_trailing_stop_order(data=order_info);
                    elif positionSide.lower() == 'short' and side.lower() == 'sell' and type.lower() == 'trailing':
                        pass
                    elif positionSide.lower() == 'short' and side.lower() == 'buy' and type.lower() == 'trailing':
                        self.create_trailing_stop_order(data=order_info);
                    else:
                        pass
        except Exception as exp:
            logger.debug(f'trade_signal_did_appear--order_info--{exp}')
        finally:
            pass

    def start_monitor_trade_signal(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        self.signal_engine = SignalEngine()
        self.signal_engine.signal_did_appear_callback = self.trade_signal_did_appear
        self.customSignalInfo['input_params'] = data['input_params']
        self.set_useing_custom_signal_info(data=self.customSignalInfo)
        self.signal_engine.start_monitor_signal(data=data, tickers=self.getTickers())

    def init_custom_signal_from_disk(self, cache_key: str):
        useing_s_info = KVInfo.get_value_by_key(key=cache_key)
        if useing_s_info is not None:
            custom_code = useing_s_info['custom_code']
            input_params = useing_s_info['input_params']
            customSignal = CustomSignal(custom_code=custom_code)
            customSignal.input_params = input_params
            return customSignal
        else:
            return None

    def public_custom_signal_info_to_market(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        custom_code = data['custom_code']
        customSignal: CustomSignal = CustomSignal(custom_code=custom_code)
        (format_ok, msg) = customSignal.format_check()
        if format_ok == False:
            self.call_js_method("showMessage", {'message': msg, 'type': 'error'})
            return
        else:
            pass
            
        ts = time.time()
        update_time = str(int(round(ts * 1000000)))
        u_id = self.userInfo['u_id']
        token = self.userInfo['token']
        s_id = f'{u_id}_{update_time}'
        params = {
            'url_path': '/public/custom/signal/to/market',
            'params': {
                'v_code': data['v_code'],
                'v_code_type': data['v_code_type'],
                'token': token,
                'signal_info': {
                    's_id': s_id,
                    'update_time': update_time,
                    'name': customSignal.name,
                    'version': customSignal.version,
                    'deploy_version': customSignal.deploy_version,
                    'detail_url': customSignal.detail_url,
                    'open_source': customSignal.open_source,
                    'custom_code': customSignal.custom_code,
                    'author_id': u_id,
                    'author_name': '',
                },
            }
        }
        return self.local_send_http_request(data=params)
    
    def get_latest_log_text(self, data: dict):
        logText = ''
        # 日志文件名
        log_file_name = 'log-' + time.strftime(
            '%Y-%m-%d', time.localtime(time.time())) + '.log'
        log_dir_path = PathTools.app_temp_log_file_dir()
        log_file_path = log_dir_path.joinpath(log_file_name)
        # log_file_path = 'C:\\Users\\lfc\\Desktop\\test_log.txt'
        try:
            # 读取文件
            log_file = open(log_file_path, 'r', encoding='utf-8')
            log_str = log_file.read()
            logText = log_str
            log_file.close()
        except Exception as exp:
            logger.debug(f'get_latest_log_text--error-->{exp}, {data}')
        finally:
            pass
        
        return {'logText': logText}


class BridgeMonitor(BridgeSignals):
    monitor_config_key = 'k_monitor_config_cache'

    def getMonitorConfig(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        self.get_useing_custom_signal_info(data=data)
        config = KVInfo.get_value_by_key(key=self.monitor_config_key)
        if config is None or len(config) < 1:
            from .default_values import default_monitor_config
            config = default_monitor_config
        else:
            pass
        return config

    def startMonitor(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        KVInfo.update(key=self.monitor_config_key, value=data)
        self.start_monitor_trade_signal(data)
        return {'running': True}

    def stopMonitor(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        self.stop_monitor_trade_signal(data)
        return {'running': False}

    def getMonitorStatus(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        if self.signal_engine is not None:
            return {'running': self.signal_engine.running}
        else:
            return {'running': False}

class BridgePlayer(BridgeMonitor):

    def play_price_alert_audio(self, data: dict):
        symbol = data['symbol']
        condition = data['condition']
        to_price = data['to_price']
        notif_info = {
            'title': f'价格提醒: {symbol}',
            'message': f'现价 {condition} {to_price}',
            'type': 'success',
            'noti_type': 'price_alert',
            'duration': 10*60*1000
        }
        logger.debug(f'触发价格提醒警报-->{notif_info}')
        self.call_js_method("showNotification", notif_info)
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        a_path = PathTools.app_audio_file_dir().joinpath('price_alert2.wav')
        logger.debug(f'触发价格提醒警报-a_path->{a_path}')
        try:
            AudioTools.play_audio(str(a_path))
        except Exception as exp:
            logger.error(f'play_price_alert_audio--error-->{exp}')

class JSBridge(BridgePlayer):
    pass
