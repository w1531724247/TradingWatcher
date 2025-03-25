# 

import math
from tw_api.server.dbmodels.kv_info import KVInfo
from tw_api.utils.logger_tools import logger
from .BaseBridge import HunterBridge
import random


class BATrader(HunterBridge):
    faker_order_list = None
    faker_order_list_key = "key_faker_order_list"

    def generateNewClientOrderId(self, str_length = 32):
        """
            生成一个指定长度的随机字符串
        """
        random_str = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
        length = len(base_str) - 1
        for i in range(str_length):
            random_str += base_str[random.randint(0, length)]

        return random_str

    def clear_position(self, data: dict):
        try:
            symbol = data['symbol']
            positionSide = data['positionSide']
            p_list = self.getPositions()[symbol]
            for p_info in p_list:
                p_positionAmt = p_info['positionAmt']
                if "-" not in p_positionAmt:
                    positionSide = "LONG"
                    self.clear_position_by_market(symbol=symbol, positionSide=positionSide, amount=p_positionAmt)
                elif "-" in p_positionAmt:
                    positionSide = "SHORT"
                    self.clear_position_by_market(symbol=symbol, positionSide=positionSide, amount=p_positionAmt)
                else:
                    pass
        except Exception as exp:
            logger.debug(f'clear_positions--->{exp}')
        finally:
            pass

    def calculate_amount_with_value(self, symbol: str, value: str, price: str = None):
        if value == '':
            return '0.0'
        elif value is None:
            return '0.0'
        else:
            pass
        
        if price is None:
            lastPrice = self.get_last_price(symbol=symbol)
            amount = float(value) / float(lastPrice)
        else:
            amount = float(value) / float(price)

        return str(amount)
    
    def open_position_by_market_with_value(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        value = data['value']
        amount = self.calculate_amount_with_value(symbol=symbol, value=value)
        return self.open_position_by_market(symbol=symbol, positionSide=positionSide, amount=amount)

    def open_position_by_market_with_percent(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        percent = data['percent']
        leverage = data['leverage']
        rate = float(percent)/100.0
        value = float(self.usdt_balance())*rate*int(leverage)
        return self.open_position_by_market_with_value({'symbol': symbol, 'positionSide': positionSide, 'value': value})

    def create_trailing_stop_order(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        
        value = data['value']
        activationPrice = data['activationPrice']
        callbackRate = data['callbackRate']
        callbackRate = round(callbackRate, 1) # 保留一位小数
        amount = self.calculate_amount_with_value(symbol=symbol, value=value)

        lastPrice = self.get_last_price(symbol=symbol)
        lastPrice = float(lastPrice)
        
        newClientOrderId = self.generateNewClientOrderId()
        message = '下单成功'
        activationPrice = self.fix_order_price(symbol=symbol, price=activationPrice)
        amount = self.fix_order_amount(symbol=symbol, amount=amount)
        order_info = {}
        try:
            logger.debug(f'create_trailing_stop_order--2')
            if positionSide.upper() == 'LONG':
                logger.debug(f'create_trailing_stop_order--3')
                side = 'SELL'
                message = message + f'{symbol}追踪止损平多'
                # activationPrice = lastPrice + self.price_tick_size_for_symbol(symbol=symbol)*2
            else:
                logger.debug(f'create_trailing_stop_order--4')
                side = 'BUY'
                message = message + f'{symbol}追踪止损平空'
                # activationPrice = lastPrice - self.price_tick_size_for_symbol(symbol=symbol)*2
            logger.debug(f'create_trailing_stop_order--callbackRate-->{callbackRate}--{activationPrice}')
            # 追踪止损
            if self.dualSidePosition:
                positionSide = data['positionSide']
            else:
                positionSide = 'BOTH'
            order_info = self.um_auth_http_client.synced("new_order",symbol=symbol, side=side, positionSide=positionSide, type='TRAILING_STOP_MARKET',
                                                activationPrice = activationPrice,
                                            quantity=amount, callbackRate=callbackRate, newClientOrderId=newClientOrderId)
            logger.debug(f'create_trailing_stop_order--order_info-->{order_info}')
            self.call_js_method("showMessage", {'message': message, 'type': 'success'})
        except Exception as exp:
            logger.debug(f'create_trailing_stop_order---->{exp}')
            self.call_js_method("showMessage", {'message': str(exp), 'type': 'error'})
        finally:
            pass
        return order_info
    
    def open_position_by_market_with_amount(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        amount = data['amount']
        return self.open_position_by_market(symbol=symbol, positionSide=positionSide, amount=amount)

    def open_position_by_market(self, symbol: str, positionSide: str, amount: str):
        newClientOrderId = self.generateNewClientOrderId()
        message = '下单成功'
        if positionSide.upper() == 'LONG':
            side = 'BUY'
            message = message + f'{symbol}市价开多'
        else:
            side = 'SELL'
            message = message + f'{symbol}市价开空'
        amount = self.fix_order_amount(symbol=symbol, amount=amount)
        order_info = {}
        try:
            if self.dualSidePosition:
                pass
            else:
                positionSide = 'BOTH'
            order_info = self.um_auth_http_client.synced("new_order",symbol=symbol, side=side, positionSide=positionSide, type='MARKET',
                                          quantity=amount
                                          , newClientOrderId=newClientOrderId)
            self.call_js_method("showMessage", {'message': message, 'type': 'success'})
        except Exception as exp:
            logger.debug(f'open_position_by_market---->{exp}')
            self.call_js_method("showMessage", {'message': str(exp), 'type': 'error'})
        finally:
            pass
        return order_info
    
    def save_stop_and_profit_order_info_for_limit(self, data: dict):
        order_info_list = KVInfo.get_value_by_key(key='k_save_stop_and_profit_order_info_list')
        if order_info_list is None:
            order_info_list = []
        else:
            if len(order_info_list) > 200:
                order_info_list = order_info_list[-200:]
            else:
                pass
        order_info_list.append(data)
        KVInfo.update(key='k_save_stop_and_profit_order_info_list', value=order_info_list)

    def open_position_by_limit_with_value(self, data: dict):
        symbol = data.get('symbol', '')
        positionSide = data.get('positionSide', '')
        value = data.get('value', '')
        price = data.get('price', '')
        amount = self.calculate_amount_with_value(symbol=symbol, value=value)
        newClientOrderId = data.get('newClientOrderId', None)
        return self.open_position_by_limit(symbol=symbol, positionSide=positionSide, amount=amount, price=price, client_OrderId=newClientOrderId)
    
    def faker_open_position_by_limit_with_value(self, data: dict):
        symbol = data.get('symbol', '')
        positionSide = data.get('positionSide', '')
        value = data.get('value', '')
        price = data.get('price', '')
        trigger_price = data.get('trigger_price', '')
        amount = self.calculate_amount_with_value(symbol=symbol, value=value)
        loss_price = data.get('loss_price', '')
        profit_price = data.get('profit_price', '')
        low_invaild_price = data.get('low_invaild_price', '')
        high_invaild_price = data.get('high_invaild_price', '')
        return self.faker_open_position_by_limit(symbol=symbol, 
                                                 positionSide=positionSide, 
                                                 value=value, 
                                                 amount=amount, 
                                                 price=price, 
                                                 trigger_price=trigger_price,
                                                 loss_price=loss_price,
                                                 profit_price=profit_price,
                                                 low_invaild_price=low_invaild_price,
                                                 high_invaild_price=high_invaild_price)

    def faker_open_position_by_limit_with_percent(self, data: dict):
        symbol = data.get('symbol', '')
        positionSide = data.get('positionSide', '')
        percent = data.get('percent', '')
        price = data.get('price', '')
        leverage = data.get('leverage', '')
        rate = float(percent) / 100.0
        value = float(self.usdt_balance()) * rate *int(leverage)
        order_info = {}
        trigger_price = data.get('trigger_price', '')
        loss_price = data.get('loss_price', '')
        profit_price = data.get('profit_price', '')
        low_invaild_price = data.get('low_invaild_price', '')
        high_invaild_price = data.get('high_invaild_price', '')
        return self.faker_open_position_by_limit_with_value({'symbol': symbol, 
                                                             'positionSide': positionSide, 
                                                             'value': value, 
                                                             'price': price, 
                                                             'trigger_price': trigger_price,
                                                             'loss_price':loss_price,
                                                             'profit_price':profit_price,
                                                             'low_invaild_price': low_invaild_price,
                                                             'high_invaild_price': high_invaild_price})

    def open_position_by_limit_with_percent(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        percent = data['percent']
        price = data['price']
        leverage = data['leverage']
        rate = float(percent) / 100.0
        value = float(self.usdt_balance()) * rate *int(leverage)
        order_info = {}

        return self.open_position_by_limit_with_value({'symbol': symbol, 'positionSide': positionSide, 'value': value, 'price': price})

    def open_position_by_limit_with_amount(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        amount = data['amount']
        price = data['price']
        return self.open_position_by_limit(symbol=symbol, positionSide=positionSide, amount=amount, price=price)

    def faker_open_position_by_limit(self, symbol: str, 
                                     positionSide: str, 
                                     value:str, 
                                     amount: str, 
                                     price: str, 
                                     trigger_price: str,
                                     loss_price: str,
                                     profit_price: str,
                                     low_invaild_price: str,
                                     high_invaild_price: str):
        newClientOrderId = self.generateNewClientOrderId()
        message = '下单成功'
        lastPrice = self.get_last_price(symbol=symbol)
        amount = self.fix_order_amount(symbol=symbol, amount=amount)
        stopPrice = self.fix_order_price(symbol=symbol, price=price)
        price = float(stopPrice)
        enter_type = '=='
        if positionSide.upper() == 'LONG':
            side = 'BUY'
            if float(lastPrice) > float(trigger_price):
                type = 'TAKE_PROFIT'
                message = message + f'虚拟{symbol}限价(开多)'
                price = price + self.price_tick_size_for_symbol(symbol=symbol)
                enter_type = "<="
            else:
                type = 'STOP'
                message = message + f'虚拟{symbol}限价(开多)'
                price = price - self.price_tick_size_for_symbol(symbol=symbol)
                enter_type = ">="
        else:
            side = 'SELL'
            if float(lastPrice) > float(trigger_price):
                type = 'STOP'
                message = message + f'虚拟{symbol}限价(开空)'
                price = price + self.price_tick_size_for_symbol(symbol=symbol)
                enter_type = "<="
            else:
                type = 'TAKE_PROFIT'
                message = message + f'虚拟{symbol}限价(开空)'
                price = price - self.price_tick_size_for_symbol(symbol=symbol)
                enter_type = ">="
        try:
            price = self.fix_order_price(symbol=symbol, price=price)
            if self.dualSidePosition:
                pass
            else:
                positionSide = 'BOTH'
            order_info = {
                'clientOrderId': newClientOrderId,
                'symbol':symbol, 
                'side':side, 
                'positionSide':positionSide, 
                'type':type,
                'quantity':amount, 
                'positionAmt': amount,
                'origQty': amount,
                'newClientOrderId':newClientOrderId, 
                'price':price, 
                'stopPrice':stopPrice,
                'trigger_price': trigger_price,
                'enter_type': enter_type,
                'value': value,
                'loss_price': loss_price,
                'profit_price': profit_price,
                'low_invaild_price': low_invaild_price,
                'high_invaild_price': high_invaild_price
            }
            faker_order_list = KVInfo.get_value_by_key(key=self.faker_order_list_key)
            if faker_order_list is None:
                faker_order_list = []
            else:
                pass
            faker_order_list.append(order_info)
            KVInfo.update(key=self.faker_order_list_key, value=faker_order_list)
            self.faker_order_list = faker_order_list
            self.call_js_method("showMessage", {'message': message, 'type': 'success'})
        except Exception as exp:
            logger.debug(f'faker_open_position_by_limit---->{exp}')
            self.call_js_method("showMessage", {'message': str(exp), 'type': 'error'})
        finally:
            pass
        return order_info

    def open_position_by_limit(self, symbol: str, positionSide: str, amount: str, price: str, client_OrderId: str = None):
        if client_OrderId is None:
            newClientOrderId = self.generateNewClientOrderId()
        else:
            newClientOrderId = client_OrderId
        message = '下单成功'
        lastPrice = self.get_last_price(symbol=symbol)
        amount = self.fix_order_amount(symbol=symbol, amount=amount)
        stopPrice = self.fix_order_price(symbol=symbol, price=price)
        price = float(stopPrice)
        if positionSide.upper() == 'LONG':
            side = 'BUY'
            if float(lastPrice) > float(price):
                type = 'TAKE_PROFIT'
                message = message + f'{symbol}限价(开多)'
                price = price + self.price_tick_size_for_symbol(symbol=symbol)
            else:
                type = 'STOP'
                message = message + f'{symbol}限价(开多)'
                price = price - self.price_tick_size_for_symbol(symbol=symbol)
        else:
            side = 'SELL'
            if float(lastPrice) > float(price):
                type = 'STOP'
                message = message + f'{symbol}限价(开空)'
                price = price + self.price_tick_size_for_symbol(symbol=symbol)
            else:
                type = 'TAKE_PROFIT'
                message = message + f'{symbol}限价(开空)'
                price = price - self.price_tick_size_for_symbol(symbol=symbol)
        try:
            price = self.fix_order_price(symbol=symbol, price=price)
            if self.dualSidePosition:
                pass
            else:
                positionSide = 'BOTH'
            order_info = self.um_auth_http_client.synced("new_order",symbol=symbol, side=side, positionSide=positionSide, type=type,
                                             quantity=amount, newClientOrderId=newClientOrderId, price=price, stopPrice=stopPrice, timeInForce='GTC')
            self.call_js_method("showMessage", {'message': message, 'type': 'success'})
        except Exception as exp:
            logger.debug(f'open_position_by_limit---->{exp}')
            self.call_js_method("showMessage", {'message': str(exp), 'type': 'error'})
        finally:
            pass
        return order_info

    def create_clear_position_order_by_limit(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        amount = data['origQty']
        price = data['price']
        return self.clear_position_by_limit(symbol=symbol, positionSide=positionSide, amount=amount, price=price)

    def clear_position_by_market_with_value(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        value = data['value']
        amount = self.calculate_amount_with_value(symbol=symbol, value=value)
        return self.clear_position_by_market(symbol=symbol, positionSide=positionSide, amount=amount)

    def clear_position_by_market_with_percent(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        percent = data['percent']

        amount = '0.0'
        rate = float(percent)/100.0
        p_list = self.getPositions()[symbol]
        for p_info in p_list:
            positionAmt = p_info['positionAmt']
            if positionSide == "LONG" and ("-" not in positionAmt):
                amount = math.fabs(float(positionAmt))*rate
                break
            elif positionSide == "SHORT" and ("-" in positionAmt):
                amount = math.fabs(float(positionAmt))*rate
                break
            else:
                pass
        return self.clear_position_by_market(symbol=symbol, positionSide=positionSide, amount=amount)
    
    def clear_position_by_market_with_amount(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        amount = data['amount']
        return self.clear_position_by_market(symbol=symbol, positionSide=positionSide, amount=amount)

    def clear_position_by_market(self, symbol: str, positionSide: str, amount: str):
        entryPrice = "0.0"
        p_list = self.getPositions()[symbol]
        for p_info in p_list:
            if positionSide == p_info['positionSide']:
                entryPrice = p_info['entryPrice']
                break
            else:
                pass

        newClientOrderId = self.generateNewClientOrderId()
        lastPrice = self.get_last_price(symbol=symbol)
        message = '下单成功'
        if positionSide.upper() == 'LONG':
            side = 'SELL'
            if float(lastPrice) > float(entryPrice):
                type = 'MARKET'
                message = message + f'{symbol}市价止盈(多)'
            else:
                type = 'MARKET'
                message = message + f'{symbol}市价止损(多)'
        else:
            side = 'BUY'
            if float(lastPrice) > float(entryPrice):
                type = 'MARKET'
                message = message + f'{symbol}市价止损(空)'
            else:
                type = 'MARKET'
                message = message + f'{symbol}市价止损(多)'
        amount = self.fix_order_amount(symbol=symbol, amount=amount)
        order_info = {}
        try:
            if self.dualSidePosition:
                reduceOnly = None
            else:
                reduceOnly = 'true'
                positionSide = 'BOTH'
            order_info = self.um_auth_http_client.synced("new_order",symbol=symbol, side=side, positionSide=positionSide, 
                                                         type=type, reduceOnly=reduceOnly,
                                                         quantity=amount, newClientOrderId=newClientOrderId)
            self.call_js_method("showMessage", {'message': message, 'type': 'success'})
        except Exception as exp:
            logger.debug(f'clear_position_by_market---->{exp}')
            self.call_js_method("showMessage", {'message': str(exp), 'type': 'error'})
        finally:
            pass
        return order_info

    def clear_position_by_limit_with_value(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        value = data['value']
        price = data['price']
        amount = self.calculate_amount_with_value(symbol=symbol, value=value, price=price)
        return self.clear_position_by_limit(symbol=symbol, positionSide=positionSide, amount=amount, price=price)

    def clear_position_by_limit_with_percent(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        percent = data['percent']
        price = data['price']
        amount = '0.0'
        rate = float(percent) / 100.0
        p_list = self.getPositions()[symbol]
        for p_info in p_list:
            positionAmt = p_info['positionAmt']
            if positionSide == 'LONG' and ('-' not in positionAmt):
                amount = math.fabs(float(positionAmt)) * rate
                break
            elif positionSide == 'SHORT' and ('-' in positionAmt):
                amount = math.fabs(float(positionAmt)) * rate
                break
            else:
                pass
        return self.clear_position_by_limit(symbol=symbol, positionSide=positionSide, amount=amount, price=price)

    def clear_position_by_limit_with_amount(self, data: dict):
        symbol = data['symbol']
        positionSide = data['positionSide']
        amount = data['amount']
        price = data['price']
        return self.clear_position_by_limit(symbol=symbol, positionSide=positionSide, amount=amount, price=price)

    def fixOrderAmount(self, data: dict):
        symbol = data['symbol']
        amount = data['amount']
        fixed_amount = self.fix_order_amount(symbol=symbol, amount=amount)
        return {'amount': fixed_amount}

    def fixOrderPrice(self, data: dict):
        symbol = data['symbol']
        price = data['price']
        fixed_price = self.fix_order_price(symbol=symbol, price=price)
        return {'price': fixed_price}

    def clear_position_by_limit(self, symbol: str, positionSide: str, amount: str, price: str):
        newClientOrderId = self.generateNewClientOrderId()
        lastPrice = self.get_last_price(symbol=symbol)
        amount = self.fix_order_amount(symbol=symbol, amount=amount)
        stopPrice = self.fix_order_price(symbol=symbol, price=price)
        price = float(stopPrice)
        message = '下单成功'
        if positionSide.upper() == 'LONG':
            side = 'SELL'
            if float(lastPrice) > float(price):
                type = 'STOP_MARKET'
                message = message + f'{symbol}限价止损(多)'
                price = price + self.price_tick_size_for_symbol(symbol=symbol)
            else:
                type = 'TAKE_PROFIT_MARKET'
                message = message + f'{symbol}限价止盈(多)'
                price = price - self.price_tick_size_for_symbol(symbol=symbol)
        else:
            side = 'BUY'
            if float(lastPrice) > float(price):
                type = 'TAKE_PROFIT_MARKET'
                message = message + f'{symbol}限价止盈(空)'
                price = price + self.price_tick_size_for_symbol(symbol=symbol)
            else:
                type = 'STOP_MARKET'
                message = message + f'{symbol}限价止损(空)'
                price = price - self.price_tick_size_for_symbol(symbol=symbol)
        
        order_info = {}
        try:
            price = self.fix_order_price(symbol=symbol, price=price)
            if self.dualSidePosition:
                reduceOnly = None
            else:
                reduceOnly = 'true'
                positionSide = 'BOTH'
            order_info = self.um_auth_http_client.synced("new_order",symbol=symbol, side=side, positionSide=positionSide, type=type,
                                             quantity=amount, newClientOrderId=newClientOrderId, reduceOnly=reduceOnly,
                                             stopPrice=stopPrice)
            self.call_js_method("showMessage", {'message': message, 'type': 'success'})
        except Exception as exp:
            logger.debug(f'clear_position_by_limit---->{exp}')
            self.call_js_method("showMessage", {'message': str(exp), 'type': 'error'})
        finally:
            pass
        return order_info
    
    def modify_order(self, data: dict):
        order_info = None
        try:
            clientOrderId = data['clientOrderId']
            newPrice = data['newPrice']
            symbol = data['symbol']
            od_info = self.get_open_order_by_id(order_id=clientOrderId, symbol=symbol)
            if od_info is not None:
                clientOrderId = od_info['clientOrderId']
                orderId = od_info['orderId']
                side = od_info['side']
                quantity = od_info['origQty']
                to_price = self.fix_order_price(symbol=symbol, price=newPrice)
                positionSide = od_info['positionSide']
                if self.dualSidePosition:
                    if (positionSide == 'LONG' and side == 'SELL') or (positionSide == 'SHORT' and side == 'BUY'):
                        order_info = self.clear_position_by_limit(symbol=symbol, amount=quantity, price=to_price, positionSide=positionSide)
                    if (positionSide == 'LONG' and side == 'BUY') or (positionSide == 'SHORT' and side == 'SELL'):
                        self.call_js_method("showMessage", {'message': f'仅支持平仓订单', 'type': 'error'})
                        # order_info = self.um_auth_http_client.synced("modify_order", symbol=symbol, side=side, quantity=quantity, price=to_price, orderId=orderId, origClientOrderId=clientOrderId)
                else:
                    positionSide = 'BOTH'
                    if side == 'SELL':
                        positionSide = 'LONG'
                    elif side == 'BUY':
                        positionSide = 'SHORT'
                    order_info = self.clear_position_by_limit(symbol=symbol, amount=quantity, price=to_price, positionSide=positionSide)
                        # order_info = self.um_auth_http_client.synced("modify_order", symbol=symbol, side=side, quantity=quantity, price=to_price, orderId=orderId, origClientOrderId=clientOrderId)
                if order_info is not None:
                    self.delete_open_order(data=od_info)
                    self.get_open_orders_by_symbol(symbol=symbol)
                else:
                    pass
                # self.call_js_method("showMessage", {'message': f'{symbol} 订单已修改', 'type': 'success'})
            else:
                pass
        except Exception as exp:
            logger.debug(f'modify_order---->{exp}')
            self.call_js_method("showMessage", {'message': str(exp), 'type': 'error'})
        finally:
            pass

        return order_info
