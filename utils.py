'''
Author: mengzonefire
Date: 2023-01-05 14:49:01
LastEditTime: 2023-03-24 16:20:56
LastEditors: mengzonefire
Description: 存放工具函数
'''

import os
import re
import sys
import base64
import json
import copy
import time
import requests
from urllib.parse import quote, unquote
from const import *

s = requests.Session()
baidu_cookies_dict = dict()

'''
description: 初始化步骤
'''


def inital():
    exe_path, _ = os.path.split(sys.argv[0])
    if exe_path:
        os.chdir(exe_path)  # 切换工作目录到可执行文件所在目录


def write_log(err):
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    with open('./{}.log'.format(now_time), 'a') as f:
        f.write(err)
        f.close()


def readCookie():
    global logid
    if not os.path.isfile(cookie_file):
        print(
            f'cookie文件{cookie_file}不存在, 请使用浏览器cookie插件导出度盘cookie, 并复制到程序所在目录下的cookie文件内')
        return False
    with open(cookie_file, 'r') as f:
        try:
            cookie_json = json.loads(f.read())
        except:
            print('cookie格式错误, 请使用浏览器cookie插件导出度盘cookie')
            return False
        for cookie in cookie_json:
            baidu_cookies_dict[cookie['name']] = cookie['value']
    logid = str(base64.b64encode(
        unquote(baidu_cookies_dict['BAIDUID']).encode("utf-8")), "utf-8")
    return True


# def outputCookie():
#     cookie_text = ""
#     for key in baidu_cookies_dict:
#         cookie_text += f'{key}={baidu_cookies_dict[key]}; '
#     with open('baidu_cookie_output.txt', 'w') as f:
#         f.write(cookie_text)


'''
description: 解密已加密的md5
param {str} encryptMd5 (加密)
return {str} (解密)
'''


def decryptMd5(encryptMd5):
    if re.compile(r'[a-f\d]').match(encryptMd5[9]):
        return encryptMd5
    key = '{:x}'.format(ord(encryptMd5[9]) - ord('g'))
    key2 = encryptMd5[0:9] + key + encryptMd5[10:]
    key3 = ''
    for i in range(len(key2)):
        key3 += '{:x}'.format(int(key2[i], 16) ^ (15 & i))
    md5 = key3[8:16] + key3[0:8] + key3[24:32] + key3[16:24]
    return md5


'''
description: 从接口元数据解析出正确文件路径
param {*} fileInfo 接口获取的文件/目录数据
return {str} path 文件路径
'''


def parseFilePath(fileInfo):
    path = str
    if 'app_id' in fileInfo:
        path = fileInfo['path'] if fileInfo['isdir'] else fileInfo['server_filename']
    else:
        path = fileInfo['path']
    if path[0] != '/':
        path = '/' + path
    return path.replace('\u200b', '')


class bdpanHelper:
    cookie: dict
    bdstoken: str
    logid: str
    extra: str
    shareid: int
    share_uk: int
    url: str
    pwd: str
    surl: str

    def __init__(self, url: str, pwd: str):
        self.url = url
        self.pwd = pwd
        self.cookie = copy.deepcopy(baidu_cookies_dict)

    def getBdlink(self):
        fileInfoList = []
        outputInfoList = []  # [{path:, errno:, bdlink?:,}]
        respon = self.verify()

        if not respon['errno']:
            self.cookie['BDCLND'] = respon['randsk']
            self.extra = f'{{"sekey":"{unquote(self.cookie["BDCLND"])}"}}'
            respon = self.getFileList()
            if not respon['errno']:
                fileInfoList = respon['data']
            else:
                return respon
        else:
            return respon

        for fileInfo in fileInfoList:
            if fileInfo['md5']:
                fileInfo['md5'] = decryptMd5(fileInfo['md5'])
            result = self.checkMd5(fileInfo)['errno']
            if not result:
                outputInfoList.append(
                    {'path': fileInfo['path'], 'bdlink': f"{fileInfo['md5']}#{fileInfo['size']}#{fileInfo['path']}", 'errno': 0})
            elif result == 404:
                outputInfoList.append(self.getMd5FromDlink(fileInfo))
            else:
                outputInfoList.append(
                    {'path': fileInfo['path'], 'errno': result})

        for outputInfo in outputInfoList:
            if outputInfo['errno']:
                msg = default_msg
                if outputInfo['errno'] in errno_msg:
                    msg = errno_msg[respon['errno']]
                outputInfo['msg'] = msg

        return {'errno': 0, 'list': outputInfoList}

    '''
    description: 递归扫描目录下的文件
    param {*} dirInfo 单条目录数据, 需包含path
    return {*} fileInfoList 文件数据列表
    '''

    def scanFile(self, path, page):
        fileInfoList = []
        respon = s.get(sharelist_url.format(dir=quote(
            path), logid=logid, shareid=self.shareid, uk=self.share_uk, page=page), cookies=self.cookie).text
        respon = json.loads(respon)
        if not respon['errno']:
            if not len(respon['list']):
                return fileInfoList
            else:
                for file in respon['list']:
                    if file['isdir']:
                        fileInfoList += self.scanFile(parseFilePath(file), 1)
                    else:
                        fileInfoList += [{'md5': file['md5'].lower(),
                                         'size': file['size'], 'path': parseFilePath(file), 'fs_id': file['fs_id']}]
                fileInfoList += self.scanFile(path, page+1)
        else:
            fileInfoList.append({'path': path, 'errno': respon['errno']})
        return fileInfoList

    '''
    description: 从分享链接递归读取文件列表数据
    param {*} info 接口参数数据dic
    return {List} 文件数据列表, 包含md5, size, path, fs_id
    '''

    def getFileList(self):
        fileInfoList = []
        respon = s.get(self.url, cookies=self.cookie).text
        fileList = p_fileList.findall(respon)
        if len(fileList):
            fileList = json.loads(f'[{{{fileList[0]}}}]')
        else:
            return {'errno': 115}
        for file in fileList:
            if file['isdir']:
                fileInfoList += self.scanFile(parseFilePath(file), 1)
            else:
                fileInfoList += [{'md5': file['md5'].lower(),
                                 'size': file['size'], 'path': parseFilePath(file), 'fs_id': file['fs_id']}]
        return {'errno': 0, 'data': fileInfoList}

    '''
    description: 验证链接, 获取randsk(密钥)和share_uk,shareid
    param {str} url 分享链接
    param {str} pwd 提取码
    return {*} info 接口参数数据dic
    '''

    def verify(self):
        result = p_surl.findall(self.url)
        if len(result):
            self.surl = result[0][1]
        else:
            return {'errno': 114}
        respon = s.get(self.url, cookies=self.cookie).text
        if '百度网盘-链接不存在' in respon:
            return {'errno': 1919}
        _share_uk = p_share_uk.findall(respon)
        _shareid = p_shareid.findall(respon)
        _bdstoken = p_bdstoken.findall(respon)
        if len(_share_uk) and len(_shareid):
            self.share_uk = int(_share_uk[0])
            self.shareid = int(_shareid[0])
        else:
            return {'errno': 514}
        if len(_bdstoken):
            self.bdstoken = _bdstoken[0]
        else:
            return {'errno': 810}
        respon = s.post(verify_url.format(surl=self.surl, bdstoken=self.bdstoken), headers={
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': ua_web, 'Referer': self.url}, data={'pwd': self.pwd, 'vcode': '', 'vcode_str': ''}).text
        respon = json.loads(respon)
        if not respon['errno']:
            return {'errno': 0, 'randsk': respon['randsk']}
        else:
            return {'errno': respon['errno']}

    '''
    description: 从dlink(文件下载直链)获取文件md5
    param {*} fileInfo 单条文件数据, 需包含md5, size, path, file_id
    return {*} 修正md5后的输出文件数据
    '''

    def getMd5FromDlink(self, fileInfo):
        dlink: str
        sign: str
        timestamp: int
        respon = s.get(tpl_url.format(surl='1'+self.surl,
                       logid=logid), cookies=self.cookie).text
        respon = json.loads(respon)
        if not respon['errno']:
            sign = respon['data']['sign']
            timestamp = respon['data']['timestamp']
        else:
            return {'path': fileInfo['path'], 'errno': respon['errno']}
        data = {
            'extra': self.extra,
            'logid': logid,
            'fid_list': json.dumps([fileInfo['fs_id']]),
            'primaryid': self.shareid,
            'uk': self.share_uk,
            'product': "share",
            'encrypt': 0,
        }
        respon = s.post(sharedownload_url.format(
            sign=sign, timestamp=timestamp), cookies=self.cookie, data=data).text
        respon = json.loads(respon)
        if not respon['errno']:
            if 'list' in respon and len(respon['list']):
                dlink = respon['list'][0]['dlink']
            else:
                return {'path': fileInfo['path'], 'errno': 116}
        else:
            return {'path': fileInfo['path'], 'errno': respon['errno']}
        respon = s.get(dlink, headers={'Range': 'bytes=0-1',
                                       "User-Agent": ua_dl})
        if issue_domain in respon.url:
            return {'path': fileInfo['path'], 'errno': 119}
        responHeader = str(respon.headers)
        md5 = p_md5.findall(responHeader)
        if len(md5):
            fileInfo['md5'] = md5[0].lower()
        else:
            return {'path': fileInfo['path'], 'errno': 996}
        return {'path': fileInfo['path'], 'bdlink': f"{fileInfo['md5']}#{fileInfo['size']}#{fileInfo['path']}", 'errno': 0}

    '''
    description: 验证秒传信息的有效性
    param {*} fileInfo 单条文件数据, 需包含md5, size
    return {'errno': int} 验证结果 errno=0为验证通过
    '''

    def checkMd5(self, fileInfo):
        if not fileInfo['md5']:
            return {'errno': 404}
        data = {'block_list': json.dumps([fileInfo['md5']]),
                'size': fileInfo['size'], 'path': fileInfo['md5'], 'isdir': 0, 'autoinit': 1}
        respon = s.post(
            precreate_url+f'&bdstoken={self.bdstoken}', cookies=baidu_cookies_dict, data=data).text
        respon = json.loads(respon)
        if not respon['errno']:
            if not len(respon['block_list']):
                return {'errno': 0}
            else:
                return {'errno': 404}
        else:
            return {'errno': respon['errno']}


if __name__ == '__main__':
    readCookie()
    respon = bdpanHelper(
        'https://pan.baidu.com/s/xxx', 'xxxx').getBdlink()  # 模块测试
    if not respon['errno']:
        print(respon)
    else:
        msg = default_msg
        if respon['errno'] in errno_msg:
            msg = errno_msg[respon['errno']]
        print(f"错误码: {respon['errno']}, 提示: {msg}")
