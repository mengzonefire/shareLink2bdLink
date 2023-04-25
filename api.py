"""
Author: mengzonefire
Date: 2023-04-25 19:55:50
LastEditTime: 2023-04-25 21:33:34
LastEditors: mengzonefire
Description: 配置后端对应api的调用
"""

from json import loads, dumps
from http.server import BaseHTTPRequestHandler
from utils import bdpanHelper
import const


class messageHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "application/x-www-form-urlencoded")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()
        req_datas = self.rfile.read(int(self.headers["content-length"]))  # 加上限制读取的报文长度
        message = req_datas.decode()
        const.lastMsg = message
        jsonData = loads(message)
        print(jsonData)
        if "sharelink" in jsonData and "pw" in jsonData:
            respon = bdpanHelper(
                jsonData["sharelink"], jsonData["pw"]
            ).getBdlink()  # 单文件分享
            if respon["errno"]:
                msg = const.default_msg
                if respon["errno"] in const.errno_msg:
                    msg = const.errno_msg[respon["errno"]]
                respon["msg"] = msg
            self.wfile.write(dumps(respon).encode("utf-8"))
        else:
            self.wfile.write(dumps({"errno": 114514, "msg": "接口参数错误!"}).encode("utf-8"))
