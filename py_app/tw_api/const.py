# 
import platform
import re

sys_platform = platform.system().lower()
is_Windows = ("windows" in sys_platform)
is_MacOS = ("macos" in sys_platform)
is_Linux = ("linux" in sys_platform)

def remove_punctuation(line: str):
    rule = re.compile(r"[^a-zA-Z0-9\u4e00-\u9fa5]")
    line = rule.sub('_', line)

    return line

