# 

default_monitor_config = {
    "min_volume_amount": 300000000,
    "select_all_symbols": False,
    "selected_symbols": [],
    "checked_interval": "1m",
    "time_intervals": ['1m', '3m', '5m', '15m', '1h', '4h'],
    "checked_signals": [],
    "signal_types": [
        {'title': '横盘突破'},
        {'title': '均线交叉'},
        {'title': 'MACD背离'},
        {'title': 'OBV背离'},
        {'title': 'RSI超买/卖'},
        {'title': '成交量放大'}
    ]
}

default_place_order_config = {
    "margin_type": 'isolated',
    "leverage": 20
}

default_preferences = {
    "language": 'zh'
}

