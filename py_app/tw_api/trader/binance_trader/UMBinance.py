# 

from binance.um_futures import UMFutures
import requests
from requests.adapters import HTTPAdapter
from threading import Timer
import os, certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
from tw_api.utils.logger_tools import logger
import asyncio
import aiohttp
import json
from func_timeout import func_set_timeout
import time
import threading
from collections import defaultdict

rqsts = requests.Session()
rqsts.mount('https://fapi.binance.com', HTTPAdapter(max_retries=1))

class UMBinance(UMFutures):
    time_offset = 0.0
    network_ok = False
    get_time_timer = None
    timer_running = False
    js_port = 10689

    # 用于缓存函数调用
    _call_cache = defaultdict(dict)
    _cache_lock = threading.Lock()

    def get_timestamp(self):
        # 假设这是一个获取当前时间戳的方法
        return int(time.time() * 1000)

    def synced(self, fn_name, **args):
        exclude_fn_list = ['new_order']
        if fn_name not in exclude_fn_list:
            current_time = time.time()
            cache_key = (fn_name, frozenset(args.items()))

            with self._cache_lock:
                if cache_key in self._call_cache:
                    last_call_time, result = self._call_cache[cache_key]
                    if current_time - last_call_time < 1.0:
                        print(f"Skipping call to {fn_name} due to recent call within 1 second.")
                        return result
        else:
            pass
                
        result = None
        try:
            args['timestamp'] = self.get_timestamp()
            args['recvWindow'] = 60000
            print(f'synced---->{fn_name}', {**args})
            result = getattr(self, fn_name)(**args)
        except Exception as exp:
            (code, err_code, err_msg, extra) = exp.args
            self.handle_error_with_code(err_code=err_code)
            logger.error(f'synced--error--{fn_name}--{str(args)}-->{exp}')
        finally:
            if fn_name not in exclude_fn_list:
                with self._cache_lock:
                    self._call_cache[cache_key] = (current_time, result)
            else:
                pass

        return result

    def __del__(self):
        if self.get_time_timer is not None:
            self.get_time_timer.cancel()
            del self.get_time_timer
        else:
            pass
        class_name = self.__class__.__name__
        print(class_name, '__del__ 销毁')

    def __init__(self, key=None, secret=None, **kwargs):
        super().__init__(key, secret, **kwargs)
        if UMBinance.timer_running == False:
            UMBinance.timer_running = True
            self._get_time_offset()
        else:
            pass
        
    def update_time_offset(self):
        if self.get_time_timer is not None:
            self.get_time_timer.cancel()
            del self.get_time_timer
        else:
            pass
        
        self.get_time_timer = Timer(5*60, self._get_time_offset)
        self.get_time_timer.start()

    def _get_time_offset(self):
        logger.debug('start ----_get_time_offset----')
        try:
            response = requests.get('https://fapi.binance.com/fapi/v1/ping', timeout=(2, 1))  
            # 处理响应数据
            print(response.text)
            self.start_update_time()
        except Exception as exp:
            logger.debug(f'_get_time_offset--->{exp}')
        finally:
            logger.debug('end ----_get_time_offset----')
            return self
        
    @func_set_timeout(3)
    def start_update_time(self):
        try:
            res = self.time()
            cur_ts = int(time.time() * 1000)
            serverTime = int(res['serverTime'])
            UMBinance.time_offset = serverTime - cur_ts
            UMBinance.network_ok = True
            logger.debug(f'start_update_time--{cur_ts}--{UMBinance.time_offset}--{serverTime}')
        except Exception as exp:
            logger.debug(f'start_update_time--->{exp}')
        finally:
            self.update_time_offset()

        return self
    
    def get_timestamp(self):
        cur_ts = int(time.time() * 1000)
        timestamp = int(cur_ts + UMBinance.time_offset)
        logger.debug(f'get_timestamp--{cur_ts}--{UMBinance.time_offset}--{timestamp}')
 
        return timestamp
        
    def sign_request(self, http_method, url_path, payload=None, special=False):
        if payload is None:
            payload = {}
        payload["timestamp"] = self.get_timestamp()
        query_string = self._prepare_params(payload, special)
        payload["signature"] = self._get_sign(query_string)
        return self.send_request(http_method, url_path, payload, special)

    def limited_encoded_sign_request(self, http_method, url_path, payload=None):
        """This is used for some endpoints has special symbol in the url.
        In some endpoints these symbols should not encoded
        - @
        - [
        - ]

        so we have to append those parameters in the url
        """
        if payload is None:
            payload = {}
        payload["timestamp"] = self.get_timestamp()
        query_string = self._prepare_params(payload)
        url_path = (
            url_path + "?" + query_string + "&signature=" + self._get_sign(query_string)
        )
        return self.send_request(http_method, url_path)

    async def send_async_post_request(self, func_name: str, params: dict = {}):
            url = "http://localhost:" + str(self.js_port) + "/handleBackendRequest"
            data = {"func": func_name, "data": params}
            headers = {"Content-Type": "application/json"}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=json.dumps(data), headers=headers) as response:
                    return await response.text()
            
    def call_js_method(self, func_name: str, params: dict = {}):
        asyncio.run(self.send_async_post_request(func_name, params))

    def handle_error_with_code(self, err_code):
        err_infos = {
            '-1000': '发生未知错误。',
            '-1001': '无法处理您的请求。 请再试一次.',
            '-1002': '您无权执行此请求。',
            '-1003': '请求权重过多； IP被禁止, 请休息一会儿.',
            '-1004': 'IP地址已经在白名单',
            '-1005': '白名单上没有此IP地址',
            '-1006': '收到意外的响应。执行状态未知。',
            '-1007': '响应超时。 发送状态未知； 执行状态未知。',
            '-1008': '服务器响应超时。 请稍后重试',
            '-1014': '不支持当前的下单参数组合',
            '-1015': '新订单太多。',
            '-1016': '该服务不可用',
            '-1020': '不支持此操作。',
            '-1021': '此请求的时间戳在recvWindow之外。',
            '-1022': '此请求的签名无效。',
            '-1023': '参数里面的开始时间在结束时间之后',
            '-1099': 'unauthorized.',
            '-1100': '在参数中发现非法字符。',
            '-1101': '为此端点发送的参数太多。',
            '-1102': '未发送强制性参数，该参数为空/空或格式错误。',
            '-1103': '发送了未知参数。',
            '-1104': '并非所有发送的参数都被读取。',
            '-1105': '参数为空。',
            '-1106': '发送了不需要的参数。',
            '-1108': '资产不正确',
            '-1109': '非有效账户',
            '-1110': '交易对不正确',
            '-1111': '精度超过为此资产定义的最大值。',
            '-1112': '交易对没有挂单。',
            '-1113': '提现数量需要为负',
            '-1114': '发送的TimeInForce参数不需要。',
            '-1115': '无效的timeInForce',
            '-1116': '无效订单类型。',
            '-1117': '无效买卖方向。',
            '-1118': '新的客户订单ID为空。',
            '-1119': '客户自定义的订单ID为空。',
            '-1120': '无效时间间隔。',
            '-1121': '无效的交易对。',
            '-1122': '交易对状态不正确。',
            '-1125': '此listenKey不存在',
            '-1126': '不支持该资产',
            '-1127': '查询间隔太大。',
            '-1128': '可选参数组合无效。',
            '-1130': '发送的参数为无效数据。',
            '-1136': '无效的 newOrderRespType。',
            '-2010': '新订单被拒绝',
            '-2011': '取消订单被拒绝',
            '-2012': '批量取消失败',
            '-2013': '订单不存在。',
            '-2014': 'API-key 格式无效。',
            '-2015': '无效的API密钥，IP或操作权限。',
            '-2016': '找不到该交易对的交易窗口',
            '-2017': 'API key被上锁',
            '-2018': '余额不足',
            '-2019': '杠杆账户余额不足',
            '-2020': '无法成交',
            '-2021': '订单可能被立刻触发',
            '-2022': 'ReduceOnly订单被拒绝',
            '-2023': '用户正处于被强平模式',
            '-2024': '持仓不足',
            '-2025': '挂单量达到上限',
            '-2026': '当前订单类型不支持reduceOnly',
            '-2027': '挂单或持仓超出当前初始杠杆下的最大值',
            '-2028': '调整初始杠杆过低，导致可用余额不足',
            '-4000': '订单状态不正确',
            '-4001': '价格小于0',
            '-4002': '价格超过最大值',
            '-4003': '数量小于0',
            '-4004': '数量小于最小值',
            '-4005': '数量大于最大值',
            '-4006': '触发价小于最小值',
            '-4007': '触发价大于最大值',
            '-4008': '价格精度小于0',
            '-4009': '最大价格小于最小价格',
            '-4010': '最大数量小于最小数量',
            '-4011': '步进值小于0',
            '-4012': '最大订单量小于0',
            '-4013': '价格小于最小价格',
            '-4014': '价格增量不是价格精度的倍数。',
            '-4015': '客户订单ID有误。',
            '-4016': 'Price is higher than mark price multiplier cap.',
            '-4017': '价格上限小于0',
            '-4018': '价格下限小于0',
            '-4019': 'Composite scale too large.',
            '-4020': '目标策略值不适合订单状态, 只减仓',
            '-4021': '深度信息的limit值不正确。',
            '-4022': '发送的市场状态不正确。',
            '-4023': '数量的递增值不是步进值的倍数。',
            '-4024': 'Price is lower than mark price multiplier floor.',
            '-4025': 'Multiplier decimal less than zero.',
            '-4026': '收益值不正确',
            '-4027': '账户类型不正确。',
            '-4028': '杠杆倍数不正确',
            '-4029': '价格精度小数点位数不正确。',
            '-4030': '步进值小数点位数不正确。',
            '-4031': '不正确的参数类型',
            '-4032': '超过可以取消的最大订单量。',
            '-4033': '风险保障基金账号没找到。',
            '-4044': '余额类型不正确。',
            '-4045': '达到止损单的上限。',
            '-4046': '不需要切换仓位模式。',
            '-4047': '如果有挂单，仓位模式不能切换。',
            '-4048': '如果有仓位，仓位模式不能切换。',
            '-4049': 'Add margin only support for isolated position.',
            '-4050': '全仓余额不足。',
            '-4051': '逐仓余额不足。',
            '-4052': 'No need to change auto add margin.',
            '-4053': '自动增加保证金只适用于逐仓。',
            '-4054': '不能增加逐仓保证金: 持仓为0',
            '-4055': '数量必须是正整数',
            '-4056': 'API key的类型不正确',
            '-4057': 'API key不正确',
            '-4058': 'maxPrice和priceDecimal太大，请检查。',
            '-4059': '无需变更仓位方向',
            '-4060': '仓位方向不正确。',
            '-4061': '订单的持仓方向和用户设置不一致。',
            '-4062': '仅减仓的设置不正确。',
            '-4063': '无效的期权请求类型',
            '-4064': '无效的期权时间窗口',
            '-4065': '无效的期权数量',
            '-4066': '无效的期权事件类型',
            '-4067': '如果有挂单，无法修改仓位方向。',
            '-4068': '如果有仓位, 无法修改仓位方向。',
            '-4069': '无效的期权费',
            '-4070': '客户的期权ID不合法',
            '-4071': '期权的方向无效',
            '-4072': '期权费没有更新',
            '-4073': '输入的期权费小于0',
            '-4074': 'Order amount is bigger than upper boundary or less than 0, reject order',
            '-4075': 'output premium fee is less than 0, reject order',
            '-4076': '期权的费用比之前的费用高',
            '-4077': '下单的数量达到上限',
            '-4078': '期权内部系统错误',
            '-4079': '期权ID无效',
            '-4080': '用户找不到',
            '-4081': '期权找不到',
            '-4082': '批量下单的数量不正确',
            '-4083': '无法批量下单',
            '-4084': '方法不支持',
            '-4085': '期权的有限系数不正确',
            '-4086': '无效的价差阀值',
            '-4087': '用户只能下仅减仓订单',
            '-4088': '用户当前不能下单',
            '-4104': '无效的合约类型',
            '-4114': '客户的tranId长度应该小于64个字符',
            '-4115': 'clientTranId重复',
            '-4118': '仅减仓订单失败。请检查现有的持仓和挂单',
            '-4131': '交易对手的最高价格未达到PERCENT_PRICE过滤器限制',
            '-4135': '无效的激激活价格',
            '-4137': '数量必须为0，当closePosition为true时',
            '-4138': 'Reduce only 必须为true，当closePosition为true时',
            '-4139': '订 单类型不能为市价单如果不能取消',
            '-4140': '无效的交易对状态',
            '-4141': '交易对已下架',
            '-4142': '拒绝：止盈止损单将立即被触发',
            '-4144': '无效的pair',
            '-4161': '逐仓仓位模式下无法降低杠杆',
            '-4164': '订单的名义价值不可以小于，除了使用reduce only',
            '-4165': '无效的间隔',
            '-4167': '因有交易对在逐仓模式，无法切换多资产模式',
            '-4168': '多资产模式下无法使用逐仓',
            '-4169': '保证金不足无法切换多资产模式',
            '-4170': '账户有订单无法切换多资产模式',
            '-4171': '多资产模式已经被设置',
            '-4172': 'JOINT_MARGIN_REJECT_WITH_NEGATIVE_BALANCE',
            '-4183': '止盈止损订单价格不应高于触发价与报价乘数上限的乘积',
            '-4184': '止盈止损订单价格不应低于触发价与报价乘数下限的乘积',
            '-4192': '合约冷静期禁止开仓',
            '-4202': '需要通过中级KYC才能使用20x以上杠杆',
            '-4203': '开户1个月后才可以使用20倍以上杠杆',
            '-4205': '开户天后才可以使用20倍以上杠杆',
            '-4206': '该国家有杠杆限制',
            '-4208': '开启仓位放大功能的用户无法使用20x以上杠杆',
            '-4209': ' 杠杆调整失败。',
            '-4210': '触发价超过价格上限',
            '-4211': '触发价低于超过价格下限',
            '-4400': '违反合约量化交易规则，账户设置为近减仓，请之后再试',
            '-4401': '账户不满足合规条件，设置为仅减仓',
            '-4402': '根据合规要求，所在地区不提供此服务',
            '-4403': '根据合规要求，所在地区杠杆不可超过',
            '-5021': '订单无法完全成交，FOK订单被拒绝',
            '-5022': '订单无法仅做maker单， Post Only订单被拒绝',
            '-5024': '交易对不在交易状态，无法改单',
            '-5025': '仅支持限价单改单',
            '-5026': '超过单个订单改单次数上限',
            '-5027': '与原订单相同，非必要改单',
            '-5028': '请求的时间戳在撮合的recvWindow之外',
            '-5037': '非法价格匹配类型',
            '-5038': '价格匹配功能仅支持LIMIT/STOP/TAKE_PROFIT类型的订单',
            '-5039': '不正确的STP模式',
            '-5040': 'goodTillDate时间戳需要大于当前时间600秒',
            '-5041': '该档位没有对应价格'
        }
        err_msg = ''
        ignore_err_code = ['-4046']
        if str(err_code) in ignore_err_code:
            return
        elif str(err_code) in err_infos.keys():
            err_msg = err_infos[str(err_code)]
        else:
            err_msg = '未知错误'
        self.call_js_method('showMessage', {'message': err_msg, 'type': 'error'})

    


