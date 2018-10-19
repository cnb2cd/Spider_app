# --*-- coding:utf-8 --*--

import json
import requests
import time


class YDMHttp:

    apiurl = 'http://api.yundama.com/api.php'
    username = ''
    password = ''
    appid = ''
    appkey = ''

    def __init__(self, username="tigerobo", password="tigerobo2017", appid=1, appkey="22cc5376925e9387a23cf797cb9ba745"):
        self.username = username  
        self.password = password
        self.appid = str(appid)
        self.appkey = appkey

    def request(self, fields, files=[]):
        response = post_url(self.apiurl, fields, files)
        response = json.loads(response)
        return response
    
    def balance(self):
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if response:
            if response['ret'] and response['ret'] < 0:
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001
    
    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if response:
            if response['ret'] and response['ret'] < 0:
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        file = {'file': filename}
        response = self.request(data, file)
        if response:
            if response['ret'] and response['ret'] < 0:
                return response['ret']
            else:
                return response['cid']
        else:
            return -9001

    def result(self, cid):
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid)}
        response = self.request(data)
        return response and response['text'] or ''

    def decode(self, filename, codetype, timeout):
        cid = self.upload(filename, codetype, timeout)
        if cid > 0:
            for i in range(0, timeout):
                result = self.result(cid)
                if result != '':
                    return cid, result
                else:
                    time.sleep(1)
            return -3003, ''
        else:
            return cid, ''

    def report(self, cid):
        data = {'method': 'report', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid), 'flag': '0'}
        response = self.request(data)
        if response:
            return response['ret']
        else:
            return -9001


def post_url(url, fields, files=[]):
    for key in files:
        files[key] = open(files[key], 'rb');
    res = requests.post(url, files=files, data=fields)
    return res.text


class YdmReturnCode:
    SUC_RET = 1000
    UNKNOWN_REASON = 1001
    NO_MONEY = 1002
    REQ_TIME_OUT = 1003


def get_yzm_code(file_name):
    ret_code = YdmReturnCode.UNKNOWN_REASON
    ret_result = None
    code_type = 1005
    timeout = 60
    ydm = YDMHttp()
    try:
        balance = ydm.balance()
        print(balance)
        if 0 < balance < 12:
            return YdmReturnCode.NO_MONEY, ret_result

        cid, result = ydm.decode(file_name, code_type, timeout)
        if cid == -3003:
            return YdmReturnCode.REQ_TIME_OUT, ret_result

        ret_code = YdmReturnCode.SUC_RET if result else ret_code
        ret_result = result
    except TimeoutError:
        ret_code = YdmReturnCode.REQ_TIME_OUT
    return ret_code, ret_result






