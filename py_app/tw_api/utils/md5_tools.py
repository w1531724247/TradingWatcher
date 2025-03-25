# 
import hashlib

def string_md5(a_str: str):
    md5_val = hashlib.md5(a_str.encode('utf8')).hexdigest()
    return md5_val