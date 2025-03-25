#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
from fastapi import FastAPI, Request, Body, Form, Response
import uvicorn
import os
fast_app = FastAPI()
from starlette.staticfiles import StaticFiles
from tw_api.utils.path_tools import PathTools
from tw_api.utils.logger_tools import logger
from tw_api.qt_js_bridge.JSBridgeQt5 import JSBridge
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
# item.py
from pydantic import BaseModel

fast_app.mount("/py/app/static", StaticFiles(directory=PathTools.app_temp_dir()), name="py_app_static")


class Params(BaseModel):
    func: str
    data: dict = {}


# 设置允许的源名单
origins = [
    "http://localhost:8168",
    "http://localhost:8268",
    "http://localhost:*",
    "https://app.forex-investing.net",
    "https://app.tradingwatcher.com",
    "http://app.tradingwatcher.com.s3-website-ap-southeast-1.amazonaws.com",
]

# 添加CORS中间件
fast_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许从这些源发起请求
    allow_credentials=True,  # 允许携带凭证
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

from .apis import *

@fast_app.get("/")
def read_root():
    return {"Hello": "World"}

#Front end
@fast_app.get("/handleFrontendRequest")
@fast_app.post("/handleFrontendRequest")
def handleFrontendRequest(params: Params, request: Request, response: Response):
    # print('handleFrontendRequest request:', request.headers)
    # print('handleFrontendRequest params:', params.func, params.data)
    response.headers["access-control-allow-origin"] = "*";

    func = params.func
    if func == 'initOK':
        return {'status': 200, 'data': {}}
    else:
        pass
    data = params.data
    jsBridge = JSBridge()
    result = getattr(jsBridge, func)(data)
    # print('callBackendMethod result:', result)
    if isinstance(result, dict):
        return result
    elif isinstance(result, list):
        return result
    else:
        return {}

def get_log_config():
    log_flie_path = PathTools.app_temp_log_file_dir().joinpath('uv_log.log')
    log_flie_path = str(log_flie_path)
    print(f'get_log_config--->{log_flie_path}')
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename":log_flie_path
            },
            "access": {
                "formatter": "access",
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": log_flie_path
    
            },
        },
        "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        },
    }

    return LOGGING_CONFIG

def start_local_http_server(port, js_port):
    print('start_local_http_server')
    jsBridge = JSBridge()
    PathTools.js_port = js_port
    PathTools.serverDomain = f'http://localhost:{port}'
    # 获取当前脚本的路径
    # current_script_directory = Path().resolve().parent
    # uvicorn.run(fast_app, host="localhost", port=port, reload=False, ssl_keyfile="./ssl/private.key", ssl_certfile="./ssl/cert.pem")
    uvicorn.run(fast_app, host="localhost", port=port, reload=False)


    