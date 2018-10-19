# --*-- coding:utf-8 --*--

import base64
from requests.sessions import Session
from urllib.parse import quote
import binascii
import logging
import re
import json
import time
import random
import rsa
from .ydm import YdmReturnCode, get_yzm_code


logger = logging.getLogger("log")


class WeiboLogin:

    HTTP_HEADER = {
        "Referer": "https://weibo.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68"
                      ".0.3440.106 Safari/537.36"
    }

    PRE_LOGIN_BACK_STR = "sinaSSOController.preloginCallBack"
    DO_CROSS_CALL_BACK = "sinaSSOController.doCrossDomainCallBack"
    FINAL_BACK_STR = "sinaSSOController.feedBackUrlCallBack"

    PRE_LOGIN_URL = "https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback="+PRE_LOGIN_BACK_STR+"&su={" \
                    "}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)"
    LOGIN_URL = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)"
    YZM_PIC_URL = "https://login.sina.com.cn/cgi/pin.php?r=54854350&s=0&p={}"

    DW_LOGIN_INVALID_PASSWORD = 1001
    DW_LOGIN_NO_RIGHT_VERIFY_CODE = 1002
    DW_LOGIN_NEED_VERIFY_CODE = 1003
    DW_LOGIN_SUC = 1000
    DW_LOGIN_UNKNOW = 1004

    NEED_VERIFY_CODE_LOGIN = 1
    NOT_NEED_VERIFY_CODE_LOGIN = 0

    def __init__(self, account, password):
        self.account = account
        self.password = password
        self.su = base64.b64encode(self.account.encode("utf-8")).decode("utf-8")
        self.session = Session()
        self.server_param = {}
        self.login_rep_str = None
        self.ret_code = -1
        self.cookies = None
        self.yzm_pic_name = None
        self.yzm_code = None

    def prepare_login_get_server_param(self):
        """
        准备登陆 获取系统参数
        :return:
        """
        quo_su = quote(self.su)
        pre_login_url = self.PRE_LOGIN_URL.format(quo_su)
        rep_code, rep = request_data(self.session, url=pre_login_url, headers=self.HTTP_HEADER)
        if rep_code != 200:
            return False
        rep_text = rep.text
        server_param = re_find(self.PRE_LOGIN_BACK_STR+"\((.*?)\)", rep_text)
        if not server_param:
            logger.info("没有匹配到微博服务器返回的系统参数的数据:"+str(rep_text))
            return False
        self.server_param = json.loads(server_param)
        suc = True
        return suc

    def get_encrypt_password(self):
        """
        获取密码加密 rsa2加密
        :return:
        """
        password = self.password
        server_time = self.server_param.get("servertime")
        nonce = self.server_param.get('nonce')
        pubkey = self.server_param.get("pubkey")
        pk = int(pubkey, 16)
        key = rsa.PublicKey(pk, 65537)
        message = str(server_time)+"\t"+str(nonce)+"\n"+str(password)
        pass_wd = rsa.encrypt(message.encode("utf-8"), key)
        pass_wd = binascii.b2a_hex(pass_wd).decode("utf-8")
        return pass_wd

    def login_no_pic(self):
        """
        :return:
        """
        url = self.LOGIN_URL
        server_time = self.server_param.get("servertime")
        nonce = self.server_param.get('nonce')
        rsakv = self.server_param.get("rsakv")
        sp = self.get_encrypt_password()

        data = {
            'encoding': 'UTF-8',
            'entry': 'weibo',
            'from': '',
            'gateway': '1',
            'nonce': nonce,
            'pagerefer': "",
            'prelt': 138,
            'pwencode': 'rsa2',
            "returntype": "META",
            'rsakv': rsakv,
            'savestate': '7',
            'servertime': server_time,
            'service': 'miniblog',
            'sp': sp,
            'sr': '1440*900',
            'su': self.su,
            'useticket': '1',
            'vsnf': '1',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            "qrcode_flag": False
        }

        self.HTTP_HEADER["Content-Type"] = "application/x-www-form-urlencoded"
        rep_code, rep = request_data(self.session, url=url, data=data, headers=self.HTTP_HEADER, method="post")
        if rep_code != 200:
            return False

        text = rep.content.decode("GBK")
        ret_suc = True
        self.login_rep_str = text # 便于后面使用
        return ret_suc

    def login_has_pic(self, yzm_code):
        """
         :return:
         """
        url = self.LOGIN_URL
        server_time = self.server_param.get("servertime")
        nonce = self.server_param.get('nonce')
        rsakv = self.server_param.get("rsakv")
        pcid = self.server_param.get("pcid")
        sp = self.get_encrypt_password()

        data = {
            'door': yzm_code,
            'encoding': 'UTF-8',
            'entry': 'weibo',
            'from': '',
            'gateway': '1',
            'nonce': nonce,
            'pagerefer': "",
            'pcid': pcid,
            'prelt': 49,
            'pwencode': 'rsa2',
            'qrcode_flag': False,
            'returntype': 'META',
            'rsakv': rsakv,
            'savestate': 7,
            'servertime': server_time,
            'service': 'miniblog',
            'sp': sp,
            'sr': '1440*900',
            'su':  self.su,
            'url': "https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            'useticket': 1,
            'vsnf': 1
        }

        self.HTTP_HEADER["Content-Type"] = "application/x-www-form-urlencoded"
        rep_code, rep = request_data(self.session, url=url, method="post", headers=self.HTTP_HEADER, data=data)
        if rep_code != 200:
            return False

        text = rep.content.decode("GBK")
        ret_suc = True
        self.login_rep_str = text # 将返回的数据保存便于后面使用
        return ret_suc

    def get_verify_code_by_ydm(self):
        """
        1.获取验证码图片
        2.云打码平台打码
        3.返回验证码
        :return:
        """
        pc_id = self.server_param.get("pcid")
        if not pc_id:
            logger.info("没有获取到pcid")
            return
        yzm_url = self.YZM_PIC_URL.format(pc_id)
        rep_code, rep = request_data(self.session, url=yzm_url, headers=self.HTTP_HEADER)
        if rep_code != 200:
            return

        yzm_pic_name = get_pic_name()
        self.yzm_pic_name = yzm_pic_name
        path_yzm_pic_name = "login/pic/"+yzm_pic_name

        with open(path_yzm_pic_name, "wb") as file:
            file.write(rep.content)

        time.sleep(1)  # 等图片写进系统盘里

        status, yzm_code = get_yzm_code(path_yzm_pic_name)  # 根据图片从云打码平台获取数据
        if status == YdmReturnCode.SUC_RET:
            return yzm_code
        elif status == YdmReturnCode.NO_MONEY:
            # todo 发送email
            pass

    def dw_login_text(self):

        next_url = None
        login_loop = self.login_rep_str
        if 'retcode=101' in login_loop:
            logger.error('invalid password for {}, please ensure your account and password'.format(self.account))
            return self.DW_LOGIN_INVALID_PASSWORD, next_url

        if 'retcode=2070' in login_loop:
            logger.error('invalid verification code')
            return self.DW_LOGIN_NO_RIGHT_VERIFY_CODE, next_url

        if 'retcode=4049' in login_loop:
            logger.warning('account {} need verification for login'.format(self.account))
            return self.DW_LOGIN_NEED_VERIFY_CODE, next_url

        pat = r'location\.replace\([\'"](.*?)[\'"]\)'
        next_url = re_find(pat, login_loop)
        ret_code = self.DW_LOGIN_SUC if next_url else self.DW_LOGIN_UNKNOW
        return ret_code, next_url

    def continue_login(self, next_url):

        del self.HTTP_HEADER["Content-Type"]
        self.HTTP_HEADER["Referer"] = self.LOGIN_URL
        rep_code, rep = request_data(self.session,url=next_url, headers=self.HTTP_HEADER)
        if rep_code != 200:
            return

        rep_text = rep.content.decode("gbk")
        pat = r'location\.replace\([\'"](.*?)[\'"]\)'
        final_url = re_find(pat, rep_text)
        if not final_url:
            logger.info("没有获取到最终登陆的链接"+str(rep_text))
            return

        rep_code, rep = request_data(self.session, url=final_url, headers=self.HTTP_HEADER)
        if rep_code != 200:
            return
        page_data = rep.text
        pa = self.FINAL_BACK_STR+"\((.*?)\)"
        re_data = re_find(pa, page_data)
        if not re_data:
            logger.info("没有匹配的数据:"+str(page_data))

        user_info = json.loads(re_data)
        req_result = user_info.get("result")
        if not req_result:
            logger.info("登陆后的参数获取:"+str(user_info))
            return False

        user_info = user_info.get("userinfo")
        uid = user_info.get("uniqueid")
        access_url = "https://www.weibo.com/u/"+str(uid)
        rep_code, rep = request_data(self.session, url= access_url, headers=self.HTTP_HEADER)
        if rep_code != 200:
            return
        text = rep.text
        re_p = "\['oid'\]='(\d+)';"
        data = re_find(re_p, text)
        return data == uid

    def get_cookies(self):
        cookie_str = ""
        cookies = self.session.cookies.get_dict()
        keys = cookies.keys()
        for key in keys:
            cookie = cookies.get(key)
            cookie_val = str(cookie)
            cookie_str += str(key) + "=" + str(cookie_val)+";"
        cookie_str = cookie_str+"wb_view_log=1440*9002;" if cookie_str else cookie_str
        return cookie_str

    def login_action(self):
        """
        1.预先登陆
        2.根据登陆的信息进行信息判断是不是需要验证吗
            2.1 需要验证码
                2.1.1 云打码回去验证码
            2.2 不需要验证
        3.继续登陆
        4判断登陆是否成功
        :return:
        """
        login_suc = False
        suc = self.prepare_login_get_server_param()
        if not suc:
            return

        need_verify_code = self.server_param.get("showpin")
        if need_verify_code == self.NEED_VERIFY_CODE_LOGIN:
            yzm_code = self.get_verify_code_by_ydm()
            if not yzm_code:
                logger.info("没有获取到验证码就返回了:")
                return
            self.yzm_code = yzm_code
            suc = self.login_has_pic(yzm_code)
            if not suc:
                logger.info("登陆post请求失败:")
                return

        elif need_verify_code == self.NOT_NEED_VERIFY_CODE_LOGIN:
            suc = self.login_no_pic()
            if not suc:
                return

        else:
            logger.info("系统返回的关于要不要验证码的参数不明确:"+str(need_verify_code))
            return

        code, next_url = self.dw_login_text()
        if code == self.DW_LOGIN_SUC:
            login_suc = self.continue_login(next_url)
        elif code == self.DW_LOGIN_NEED_VERIFY_CODE:
            pass
        elif code == self.DW_LOGIN_INVALID_PASSWORD:
            logger.error(self.account+":"+self.password+":账号或者密码错误")
        elif code == self.DW_LOGIN_NO_RIGHT_VERIFY_CODE:
            logger.error(str(self.yzm_pic_name)+":"+str(self.yzm_code))
        return login_suc


def re_find(re_pattern_str, string):
    """
    正则匹配数据
    :param re_pattern_str: 正则表达式
    :param string: 匹配的文本
    :return:
    """
    find_result = None
    try:
        find_data_list = re.findall(re_pattern_str, string)
        find_result = find_data_list[0] if find_data_list else None
    except ValueError:
        print(re_pattern_str)
    return find_result


def get_pic_name():
    """
    产生图片的名字 时间戳+随机数（因为图片格式时png 所以以png 结尾）
    :return:
    """
    yzm_pic_name = str(int(time.time()))+str(random.randint(1, 100000))+".png"
    return yzm_pic_name


def request_data(session, url, method="get", headers=None, data=None):
    """

    :param session:  会话
    :param url:  url
    :param method: 请求方式
    :param headers:    请求头部信息
    :param data:  post 请求的 实体信息
    :return:  ret_code response_code ret_rep
    """
    rep_code = -1
    ret_rep = None
    try:
        rep = session.request(url=url, method=method, headers=headers, data=data)
        rep_code = rep.status_code
        ret_rep = rep
    except Exception as e:
        print(e)
    logger.info(url+":"+str(rep_code))
    return rep_code, ret_rep





