# -*- coding: utf-8 -*-
# 下面这句必须在if下面添加
# 
from multiprocessing import freeze_support
from tw_api.app import app_run
import sys

if __name__ == "__main__":
    freeze_support()
    app_run(sys.argv)