# 

from pydantic import BaseModel
from typing import Optional
import base64
import requests

class CustomSignalInfo(BaseModel):
    s_id: str
    update_time: str

    name: str = ''
    version: str = ''
    deploy_version: str = ''
    detail_url: str = ''
    open_source: str = ''
    custom_code: str
    auth_id: str = ''
    auth_name: str = ''
    status: str = ''

    def public_on_market(self, ot_url: str, params: dict):
        resp = requests.post(url=ot_url, json=params)

        return resp
