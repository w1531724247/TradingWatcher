# 
import subprocess
from tw_api.server.http_server import start_local_http_server
import platform
from tw_api.const import is_Linux, is_Windows, is_MacOS
from pathlib import Path
import sys
import os

sysstr = platform.system()
# 定义全局变量来保存子进程
dashboard_process = None
backend_process = None
def run_dashboard():
    # 使用Path获取当前脚本目录
    env_dir = Path(__file__).parent.parent.parent.joinpath('py_env').joinpath('dashboard_env')
    # 判断操作系统类型,如果是win则无需添加bin目录
    if sys.platform == 'win32':
        py_path = env_dir.joinpath('python')
    else:
        py_path = env_dir.joinpath('bin', 'python')

    script_path = Path(__file__).parent.parent.joinpath('hb_projects').joinpath('dashboard').joinpath('main.py')
    start_cmd = f'{py_path} -m streamlit run {script_path} --server.headless true'
    print(f'run_dashboard start_cmd {start_cmd}')
    global dashboard_process
    # 启动一个新的进程运行start_cmd
    dashboard_process = subprocess.Popen(start_cmd, shell=True)

    return dashboard_process

def run_backend():
    # 使用Path获取当前脚本目录
    env_dir = Path(__file__).parent.parent.parent.joinpath('py_env').joinpath('backend_env')
    # 判断操作系统类型,如果是win则无需添加bin目录
    if sys.platform == 'win32':
        py_path = env_dir.joinpath('python')
    else:
        py_path = env_dir.joinpath('bin', 'python')

    script_path = Path(__file__).parent.parent.joinpath('hb_projects').joinpath('backend-api').joinpath('main.py')
    start_cmd = f'{py_path} {script_path}'
    print(f'run_backend start_cmd {start_cmd}')
    global backend_process
    # 启动一个新的进程运行start_cmd
    backend_process = subprocess.Popen(start_cmd, shell=True, env=os.environ.copy())

    return backend_process

def app_run(argv: list):
    print('app_run: ', argv)
    port = 10688;
    js_port = 10689;
    if len(argv) > 1:
        port = int(argv[1])
        if len(argv) > 2:
            js_port = int(argv[2])

    # 保存子进程对象
    global dashboard_process, backend_process
    backend_process = run_backend()
    dashboard_process = run_dashboard()
    
    # 运行本地服务器
    start_local_http_server(port, js_port)
