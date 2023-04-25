"""
Author: mengzonefire
Date: 2023-01-08 01:13:00
LastEditTime: 2023-04-25 21:33:41
LastEditors: mengzonefire
Description: 主函数入口, 创建http服务
"""

import sys
import const
import traceback
import argparse
from utils import inital, readCookie, write_log
from api import messageHandler
from http.server import ThreadingHTTPServer

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--www", action="store_true")
parser.add_argument("-p", "--port", dest="port", type=int)
args = parser.parse_args()


def main():
    print(f"{const.title} by {const.author} {const.version} {const.date}")
    inital()
    if not readCookie():
        sys.exit()
    PORT = args.port or 9001
    HOST = "0.0.0.0" if args.www else "localhost"
    print("http服务运行在 {}:{}".format(HOST, PORT))
    server = ThreadingHTTPServer((HOST, PORT), messageHandler)
    server.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()  # 打印报错信息
        write_log(
            "msg: {}\nerror_log: {}".format(const.lastMsg, traceback.format_exc())
        )  # 报错信息写入log
        raise
