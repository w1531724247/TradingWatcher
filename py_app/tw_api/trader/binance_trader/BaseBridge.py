# 
from pydoc import plain
import datetime, sys, json, html, traceback, time, requests
from tw_api.server.dbmodels.kv_info import KVInfo
from tw_api.libs.corpwechatbot.app import AppMsgSender
from tw_api.libs.dingtalkchatbot.chatbot import DingtalkChatbot
from pylark import Lark, SendRawMessageReq, PyLarkError
from threading import Timer
from tw_api.utils.md5_tools import string_md5
from tw_api.utils.image_tools import base64_str_from_image_file
from tw_api.utils.logger_tools import logger
import json
import asyncio
import aiohttp
from tw_api.utils.path_tools import PathTools
from tw_api.const import is_Linux, is_Windows, is_MacOS
import os
import subprocess
import sys
import linecache
from pathlib import Path

class BaseBridge(object):
    _instance = None
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance
    
    def __init__(self):
        pass
    
class PathBridge(BaseBridge):

    # 放入缓存防止内存过载
    def get_line_count(self, file_path):
        try:
            # 确保文件存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return 0
                
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                logger.warning(f"文件存在但为空: {file_path}")
                return 0
                
            # 检查文件权限
            if not os.access(file_path, os.R_OK):
                logger.error(f"没有读取文件的权限: {file_path}")
                return 0
                
            # 读取文件行数
            count = 0
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                while True:
                    buffer = f.read(8192)  # 增加缓冲区大小提高效率
                    if not buffer:
                        break
                    count += buffer.count('\n')
        
            logger.debug(f"文件 {file_path} 共有 {count} 行")
            return count
            
        except PermissionError as e:
            logger.error(f"权限错误: {e}")
            return 0
        except UnicodeDecodeError as e:
            logger.error(f"编码错误: {e}")
            # 尝试使用二进制模式读取
            try:
                count = 0
                with open(file_path, 'rb') as f:
                    for line in f:
                        count += 1
                return count
            except Exception as e2:
                logger.error(f"二进制模式读取失败: {e2}")
                return 0
        except Exception as e:
            logger.error(f"读取文件行数时发生错误: {e}")
            return 0
    
    def open_py_log_file(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        try:
            # 使用默认文本编辑器打开日志文件
            if is_Windows:
                os.startfile(PathTools._log_file_path)
            elif is_MacOS:
                subprocess.run(['open', PathTools._log_file_path])
            elif is_Linux:
                subprocess.run(['xdg-open', PathTools._log_file_path])
            else:
                print(f"Platform not supported: {sys.platform}")
        except Exception as e:
            logger.error(f"Failed to open file: {e}")
        finally:
            return {"log_file_path": PathTools._log_file_path}
        
    def get_py_log_text(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        log_lines = []
        try:
            # 读取最后1000行
            file = PathTools._log_file_path
            n = 1000
            linecache.clearcache()
            line_count = self.get_line_count(file)
            if line_count > 1000:
                line_num = line_count - n - 1
            else:
                line_num = 0
            for line_index in range(line_num, line_count):
                last_line = linecache.getline(file, line_index)
                log_lines.append(last_line.strip())
        except Exception as e:
            logger.error(f"Failed to open file: {e}")
        finally:
            return {"log_lines": log_lines}

    async def send_async_post_request(self, func_name: str, params: dict = {}):
        url = "http://localhost:" + str(PathTools.js_port) + "/handleBackendRequest"
        data = {"func": func_name, "data": params}
        headers = {"Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(data), headers=headers) as response:
                return await response.text()
            
    def call_js_method(self, func_name: str, params: dict = {}):
        asyncio.run(self.send_async_post_request(func_name, params))

    def call_python_method(self, func_info_str: str):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name}')
        result = {}
        try:
            func_info = json.loads(func_info_str)
            func_code = func_info['code']
            func_name = func_info['func']
            func_params = func_info['data']
            result = getattr(self, func_name)(func_params)
        except Exception as exp:
            logger.error(f'{datetime.datetime.now()} call_python_method--error--> {exp} {traceback.print_exc()}');
        finally:
            if result is None:
                result = {}
            elif isinstance(result, dict):
                pass
            else:
                logger.error(f'不合适的返回值类型:{type(result)}, {result}, {func_info}')
                result = {}

            return result
    
    def record_script_logs(self, data: dict):
        # logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        log_type = data['type']
        log_text = data['text']
        if log_type == 'error':
            logger.error(f'{datetime.datetime.now()} {log_text}')
        elif log_type == 'warning':
            logger.warning(f'{datetime.datetime.now()} {log_text}')
        elif log_type == 'info':
            logger.info(f'{datetime.datetime.now()} {log_text}')
        else:
            logger.debug(f'{datetime.datetime.now()} {log_text}')
        return {}
        

class NotifyBridge(PathBridge):
    
    
    def set_notifyConfigInfo(self, new_value: dict):
        self._notifyConfigInfo = new_value

    def get_notifyConfigInfo(self):
        return self._notifyConfigInfo
    notifyConfigInfo = {}
    notify_config_info_key = 'kUserNotifyConfigInfo'

    def save_notify_config_info(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        KVInfo.update(key=self.notify_config_info_key, value=data)
        self.notifyConfigInfo = data

    def get_notify_config_info(self, data: dict = {}):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        notify_config_info = KVInfo.get_value_by_key(key=self.notify_config_info_key)
        if notify_config_info is not None:
            pass
        else:
            notify_config_info = {}
        self.notifyConfigInfo = notify_config_info
        return notify_config_info
    
    def get_corp_wechat_app(self):
        corpid = self.notifyConfigInfo['wc_corp_id']
        corpsecret = self.notifyConfigInfo['wc_secret_id']
        agentid = self.notifyConfigInfo['wc_agent_id']
        if len(corpid) > 0 and len(agentid) > 0 and len(corpsecret) > 0:
            app = AppMsgSender(corpid=corpid, # 你的企业id
                            corpsecret=corpsecret, # 你的应用凭证密钥
                            agentid=agentid) # 你的应用id
        else:
            app = AppMsgSender(
                            key=corpsecret # webhook的Key
                            )
        return app
    
    def send_corp_wechat_text_msg(self, msg_text: str):
        app = self.get_corp_wechat_app()
        app.send_text(content=msg_text)

    def send_corp_wechat_image_msg(self, img_path: str):
        app = self.get_corp_wechat_app()
        app.send_image(image_path=img_path)

    def send_corp_wechat_markdown_msg(self, md_text: str):
        app = self.get_corp_wechat_app()
        app.send_markdown(content=md_text)

    def get_ding_ding_app(self):
        # WebHook地址
        dd_token = self.notifyConfigInfo['dd_token']
        dd_secret = self.notifyConfigInfo['dd_secret']
        webhook = f'https://oapi.dingtalk.com/robot/send?access_token={dd_token}'
        secret = dd_secret #'SEC11b9...这里填写自己的加密设置密钥'  可选：创建机器人勾选“加签”选项时使用
        # 初始化机器人小丁
        # xiaoding = DingtalkChatbot(webhook)  # 方式一：通常初始化方式
        xiaoding = DingtalkChatbot(webhook, secret=secret)  # 方式二：勾选“加签”选项时使用（v1.5以上新功能）
        return xiaoding

    def send_ding_ding_text_msg(self, msg_text: str):
        xiaoding = self.get_ding_ding_app()
        # Text消息@所有人
        xiaoding.send_text(msg=msg_text)

    def send_ding_ding_markdown_msg(self, title: str, md_text: str):
        xiaoding = xiaoding = self.get_ding_ding_app()
        # Text消息@所有人
        xiaoding.send_markdown(title=title, text=md_text)

    def get_feishu_app(self):
        fs_app_id = self.notifyConfigInfo['fs_app_id']
        fs_app_secret = self.notifyConfigInfo['fs_app_secret']
        fs_custom_url = self.notifyConfigInfo['fs_custom_url']
        fs_custom_secret = self.notifyConfigInfo['fs_custom_secret']
        
        fs_app = Lark(app_id=fs_app_id, app_secret=fs_app_secret,
                  custom_url=fs_custom_url, custom_secret=fs_custom_secret)

        return fs_app

    def send_feishu_text_msg(self, title: str, md_text: str):
        fs_app = self.get_feishu_app()
        try:
            content = {
                "zh_cn": {
                    "title": title,
                    "content": [
                        [{
                            "tag": "md",
                            "text": md_text
                        }]
                    ]
                },
            }
            fs_chat_id = self.notifyConfigInfo['fs_chat_id']
            md_str = json.dumps(content)
            content_str = md_str
            msg_req = SendRawMessageReq(receive_id_type='chat_id', receive_id=fs_chat_id, content=content_str, msg_type='post')
            res, response = fs_app.message.send_raw_message(msg_req)
            logger.debug(f'send_feishu_text_msg--response-->{res} -- {response}')
        except PyLarkError as e:
            logger.debug(f'send_feishu_text_msg--error-->{e}')
        finally:
            pass
    
    def send_web_hook_msg(self, msg_type: str, data: dict):
        try:
            url_path = self.notifyConfigInfo['wh_url']
            ts = time.time()
            time_stamp = str(int(round(ts*1000)))
            secret_str = self.notifyConfigInfo['wh_secret'] + time_stamp
            secret = string_md5(secret_str)
            params = {
                'msg_type': msg_type,
                'data': data,
                'secret': secret,
                'time_stamp': time_stamp
            }
            logger.debug(f'send_web_hook_msg---->{params}')
            response = requests.post(url_path, json=params)
            logger.debug(f'send_web_hook_msg---->{response.text}')
        except Exception as exp:
            logger.debug(f'send_web_hook_msg--error-->{exp}')
        finally:
            pass

    def send_price_alert_notify(self, data: dict):
        if self.notifyConfigInfo is None or len(self.notifyConfigInfo) == 0:
            self.get_notify_config_info(data={})
        else:
            pass
        # 判断self.notifyConfigInfo是否有有效键值对,如果没有键值对,则返回
        if len(self.notifyConfigInfo) == 0:
            return
        else:
            pass
        try:
            if (self.notifyConfigInfo['enable_wechat']==True) and ('价格提醒' in self.notifyConfigInfo['wc_push_types']):
                detail_msg = data['md_msg']
                self.send_corp_wechat_markdown_msg(md_text=detail_msg)
            else:
                pass
        except Exception as exp:
            logger.debug(f'send_price_alert_notify--error--wechat-->{exp}')
        finally:
            pass
        try:
            if (self.notifyConfigInfo['enable_dingding']==True) and ('价格提醒' in self.notifyConfigInfo['dd_push_types']):
                detail_msg = data['md_msg']
                self.send_ding_ding_markdown_msg(title='价格提醒', md_text=detail_msg)
            else:
                pass
        except Exception as exp:
            logger.debug(f'send_price_alert_notify--error--dingding-->{exp}')
        finally:
            pass
        try:
            if (self.notifyConfigInfo['enable_feishu']==True) and ('价格提醒' in self.notifyConfigInfo['fs_push_types']):
                detail_msg = data['md_msg']
                self.send_feishu_text_msg(title='价格提醒', md_text=detail_msg)
            else:
                pass
        except Exception as exp:
            logger.debug(f'send_price_alert_notify--error--feishu-->{exp}')
        finally:
            pass
        try:
            if (self.notifyConfigInfo['enable_webhook']==True) and ('价格提醒' in self.notifyConfigInfo['wh_push_types']):
                data['md_msg'] = ''
                data['detail_msg'] = ''
                send_timer = Timer(0.1, self.send_web_hook_msg, ('价格提醒', data))
                send_timer.start()
            else:
                pass
        except Exception as exp:
            logger.debug(f'send_price_alert_notify--error--webhook-->{exp}')
        finally:
            pass

    def send_exception_notify(self, data: dict):
        if self.notifyConfigInfo is None or len(self.notifyConfigInfo) == 0:
            self.get_notify_config_info(data={})
        else:
            pass
        # 判断self.notifyConfigInfo是否有有效键值对,如果没有键值对,则返回
        if len(self.notifyConfigInfo) == 0:
            return
        else:
            pass

        exception_msg = data['exception_msg']
        now = datetime.datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        # 使用数组和join方法构建markdown消息
        md_msg_list = [
            '**异常通知**',
            f'> 时间: {current_time}',
            f'> 异常详情: {exception_msg}'
        ]
        detail_msg = '  \n'.join(md_msg_list)
        try:
            if (self.notifyConfigInfo['enable_wechat']==True) and ('异常通知' in self.notifyConfigInfo['wc_push_types']):
                self.send_corp_wechat_markdown_msg(md_text=detail_msg)
            else:
                pass
        except Exception as exp:
            logger.debug(f'send_exception_notify--error--1-->{exp}')
        finally:
            pass
        try:
            if (self.notifyConfigInfo['enable_webhook']==True) and ('异常通知' in self.notifyConfigInfo['wh_push_types']):
                send_timer = Timer(0.1, self.send_web_hook_msg, ('异常通知', data))
                send_timer.start()
            else:
                pass
        except Exception as exp:
            logger.debug(f'send_exception_notify--error--2-->{exp}')
        finally:
            pass

    def send_order_filled_notify(self, data: dict):
        if self.notifyConfigInfo is None or len(self.notifyConfigInfo) == 0:
            self.get_notify_config_info(data={})
        else:
            pass
        # 判断self.notifyConfigInfo是否有有效键值对,如果没有键值对,则返回
        if len(self.notifyConfigInfo) == 0:
            return
        else:
            pass

        detail_msg = ''
        try:
            symbol = data['symbol']
            positionSide = data['positionSide']
            side = data['side']
            avgPrice = data['avgPrice']
            origType = data['origType']
            origQty = data['origQty']
            type = data['type']
            od_time = data['time']
            ts = int(od_time)/1000
            _date = time.strftime('%Y-%m-%d',time.localtime(ts)) 
            _time = time.strftime('%X',time.localtime(ts))
            filled_time = f'{_date} {_time}'
            clientOrderId = data['clientOrderId']
            orderId = data['orderId']
            # order_str = json.dumps(data)
            # 使用数组和join方法构建markdown消息
            if origType == 'MARKET':
                priceType = '市价成交'
            else:
                priceType = '限价成交'

            if positionSide == 'LONG':
                if side == 'BUY':
                    orderType = '开多'
                else:
                    orderType = '平多'
            else:
                if side == 'BUY':
                    orderType = '平空'
                else:
                    orderType = '开空'
            
            md_msg_list = [
                '**订单成交**',
                f'> 交易对: {symbol}',
                f'> 订单类型: {orderType}',
                f'> 平均价格: {avgPrice}',
                f'> 订单数量: {origQty}',
                f'> 成交类型: {priceType}',
                f'> 时间: {filled_time}'
            ]
            detail_msg = '  \n'.join(md_msg_list)
        except Exception as exp:
            logger.debug(f'send_order_filled_notify--error-->{exp}')
        finally:
            pass
        if detail_msg == '':
            return
        else:
            pass
        try:
            if (self.notifyConfigInfo['enable_wechat']==True) and ('订单成交' in self.notifyConfigInfo['wc_push_types']):
                self.send_corp_wechat_markdown_msg(md_text=detail_msg)
            else:
                pass
        except Exception as exp:
            logger.debug(f'send_order_filled_notify--error--1-->{exp}')
        finally:
            pass
        
        # 添加钉钉通知
        try:
            if (self.notifyConfigInfo['enable_dingding']==True) and ('订单成交' in self.notifyConfigInfo['dd_push_types']):
                self.send_ding_ding_markdown_msg(title='订单成交', md_text=detail_msg)
            else:
                pass
        except Exception as exp:
            logger.debug(f'send_order_filled_notify--error--dingding-->{exp}')
        finally:
            pass
        
        # 添加飞书通知
        try:
            if (self.notifyConfigInfo['enable_feishu']==True) and ('订单成交' in self.notifyConfigInfo['fs_push_types']):
                self.send_feishu_text_msg(title='订单成交', md_text=detail_msg)
            else:
                pass
        except Exception as exp:
            logger.debug(f'send_order_filled_notify--error--feishu-->{exp}')
        finally:
            pass
            
        try:
            if (self.notifyConfigInfo['enable_webhook']==True) and ('订单成交' in self.notifyConfigInfo['wh_push_types']):
                send_timer = Timer(0.1, self.send_web_hook_msg, ('订单成交', data))
                send_timer.start()
            else:
                pass
        except Exception as exp:
            logger.debug(f'send_order_filled_notify--error--2-->{exp}')
        finally:
            pass

    def send_trade_signal_notify(self, data: dict):
        try:
            if (self.notifyConfigInfo['enable_wechat']==True) and ('信号通知' in self.notifyConfigInfo['wc_push_types']):
                img_path = data['image_path']
                self.send_corp_wechat_image_msg(img_path=img_path)
            else:
                pass
        except Exception as exp:
            logger.debug(f'send_trade_signal_notify--error--0-->{exp}')
        finally:
            pass
        try:
            if (self.notifyConfigInfo['enable_webhook']==True) and ('信号通知' in self.notifyConfigInfo['wh_push_types']):
                img_path = data['image_path']
                data['image_path'] = ''
                data['image_url'] = ''
                data['image_base64'] = base64_str_from_image_file(img_path=img_path)
                send_timer = Timer(0.1, self.send_web_hook_msg, ('信号通知', data))
                send_timer.start()
            else:
                pass
        except Exception as exp:
            logger.debug(f'send_trade_signal_notify--error--2-->{exp}')
        finally:
            pass

class HunterBridge(NotifyBridge):
    APP_ENV = ''
    API_HOST = ''
    API_PATH = ''
    APP_VERSION = ''

    def QWebChannelInit(self, data: dict):
        logger.debug(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name} {data}')
        
        
        