"""
Author: mengzonefire
Date: 2023-01-05 14:50:05
LastEditTime: 2023-04-25 21:33:25
LastEditors: mengzonefire
Description: 存放全局常量
"""

import re

author = "mengzonefire"
title = "度盘分享链转秒传后端"
version = "v1.0.3"
date = "23.4.25"

ua_web = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
ua_dl = "netdisk;"
tpl_url = "https://pan.baidu.com/share/tplconfig?fields=sign,timestamp&channel=chunlei&web=1&app_id=250528&clienttype=0&surl={surl}&logid={logid}"
sharedownload_url = "https://pan.baidu.com/api/sharedownload?channel=chunlei&clienttype=12&web=1&app_id=250528&sign={sign}&timestamp={timestamp}"
verify_url = "http://pan.baidu.com/share/verify?app_id=250528&channel=chunlei&clienttype=0&surl={surl}&web=1&bdstoken={bdstoken}"
create_url = "https://pan.baidu.com/api/create"
sharelist_url = "https://pan.baidu.com/share/list?showempty=0&num=10000&channel=chunlei&web=1&app_id=250528&clienttype=0&dir={dir}&logid={logid}&shareid={shareid}&uk={uk}&page={page}"
p_surl = re.compile(r"(s\/1|surl=)([a-zA-Z0-9_-]+)")
p_share_uk = re.compile(r'share_uk:"(\d+)"')
p_shareid = re.compile(r'shareid:"(\d+)"')
p_fileList = re.compile(r'"file_list":\[{(.+?)}\],')
p_bdstoken = re.compile(r"bdstoken:'([a-z\d]{32})'")
p_md5 = re.compile(r"'content-md5': '([\da-f]{32})'", flags=re.IGNORECASE)  # 忽略大小写
errno_msg = {
    -9: "提取码错误",
    114: "链接格式错误",
    514: "share_uk和shareid获取失败",
    119: "文件已被和谐",
    1919: "链接已失效",
    810: "账号cookie已失效",
    115: "fileList获取失败",
    116: "dlink获取失败, 请尝试更换cookie",
    996: "文件md5获取失败, 请下载后本地生成",
}
default_msg = "未知错误"
cookie_file = "baidu_cookie.txt"
issue_domain = "issuecdn.baidupcs.com"  # 用于检测文件是否被和谐
testPath = "/apps/生成秒传测试文件.mengzonefire"
lastMsg = ""  # 用于存储服务崩溃时接受的最后一条请求数据
