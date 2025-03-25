#------------------------------------------------------------------------------------
class SendFile:
    """
    * 钉钉发送文件
    * 需要钉钉后台绑定ip地址https://open-dev.dingtalk.com/fe/app#/corp/app(找到你创建的应用/开发管理/服务器出口IP,没有应用自己创建个小程序/企业自主开发)
    * https://open-dev.dingtalk.com/#/获取CorpId
    * 应用开发/企业内部开发/你创建的应用/应用信息获取AppKey，AppSecret
    """
    #------------------------------------------------------------------------------------
    def __init__(self):
        self.appkey = ""
        self.appsecret = ""
    #------------------------------------------------------------------------------------
    def get_access_token(self):
        url = f"https://oapi.dingtalk.com/gettoken?appkey={self.appkey}&appsecret={self.appsecret}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"appkey": self.appkey,
                "appsecret": self.appsecret}
        data = requests.request("GET", url, data=data, headers=headers)
        access_token = data.json()["access_token"]
        return access_token
    #------------------------------------------------------------------------------------
    def get_media_id(self,file_path:str):
        access_token = self.get_access_token()  # 拿到接口凭证
        url = f"https://oapi.dingtalk.com/media/upload?access_token={access_token}&type=file"
        files = {"media": open(file_path, "rb")}
        js_data = {"access_token": access_token,
                "type": "file"}
        response = requests.post(url, files=files, data=js_data)
        data = response.json()
        if data["errcode"]:
            print(f"获取media_id出错，错误代码：{data['errcode']}，错误信息：{data['errmsg']}")
            return
        return data["media_id"]
    #------------------------------------------------------------------------------------
    def send_file(self,file_path:str):
        """
        * 发送文件到钉钉
        * 需要用到上面获取的Corpld
        * 钉钉扫描http://wsdebug.dingtalk.com/定位到v0.1.2输入{"corpId":"","isAllowCreateGroup":true,"filterNotOwnerGroup":false}获取chatid
        """
        access_token = self.get_access_token()
        media_id = self.get_media_id(file_path)
        chatid = ""
        url = "https://oapi.dingtalk.com/chat/send?access_token=" + access_token
        header = {
            "Content-Type": "application/json"
        }
        js_data = {"access_token": access_token,
                "chatid": chatid,
                "msg": {
                    "msgtype": "file",
                    "file": {"media_id": media_id}
                }}
        request_data = requests.request("POST", url, data=json.dumps(js_data), headers=header)
        data = request_data.json()
        if data["errcode"]:
            print(f"发送文件出错，错误代码：{data['errcode']}，错误信息：{data['errmsg']}")