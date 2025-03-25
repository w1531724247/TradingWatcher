# 

import os 
import time 
import ntplib
import ctypes, sys
from py_app.const import is_Windows
from threading import Timer

def setSystemTime():
    if is_Windows == False:
        return
    else:
        pass
    try:
        import win32api
        clt = ntplib.NTPClient() 
        response = clt.request('pool.ntp.org') 
        ts = response.tx_time 
        ts = int(ts)
        _date = time.strftime('%Y-%m-%d',time.localtime(ts)) 
        _time = time.strftime('%X',time.localtime(ts)) 
        tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.gmtime(ts)
        def is_admin():
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False
        if is_admin():
            # 将要运行的代码加到这里
            win32api.SetSystemTime(tm_year, tm_mon, tm_wday, tm_mday, tm_hour, tm_min, tm_sec, 0)
        else:
            if sys.version_info[0] == 3:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            else:
                pass
        print('Set System OK! date {} && time {}'.format(_date,_time))
    except Exception as exp:
        print(f'setSystemTime--->{exp}')
    finally:
        auto_update_sys_time()

def auto_update_sys_time():
    update_Timer = Timer(5 * 60, setSystemTime)
    update_Timer.start()

if __name__ == "__main__":
    setSystemTime()