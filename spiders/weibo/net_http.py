# --*-- coding:utf-8 --*--
"""
@author wht
@time  2018/9/4 下午8:11
@desc 网络请求包
"""
import base64
import requests
requests.packages.urllib3.disable_warnings()


def send_http_json(url, method="get", is_json=True, **kwargs):
    """
    request 请求数据
    :param url:
    :param method:
    :param is_json:  True 返回的是json  False 返回string
    :param kwargs:
    :return: 网络请求结果
    """
    ret_data = None
    try:

        rep = requests.request(url=url, method=method, **kwargs)
        code = rep.status_code
        print(url, code)
        if code == 200:
            if is_json:
                ret_data = rep.json()
            else:
                ret_data = rep.text
        else:
            return ret_data

    except TimeoutError as e:
        print(e)
    return ret_data


def send_http_get_rep(url, method="get", **kwargs):
    """
    获取 rep
    :param url:
    :param method:
    :param kwargs:
    :return:
    """
    try:

        rep = requests.request(url=url, method=method, **kwargs)
        return rep
    except TimeoutError as e:
        print(e)


def send_http(url, method="get", **kwargs):
    """
    获取 rep
    :param url:
    :param method:
    :param kwargs:
    :return:
    """
    code = -1
    rep_text = None
    try:
        rep = requests.request(url=url, method=method, **kwargs)
        code = rep.status_code
        rep_text = rep.text
    except TimeoutError as e:
        print(e)
    except Exception as e:
        print(e)
    return code, rep_text


def session_send_http(session, url, method="get", **kwargs):
    """
    使用session 访问数据
    :param session:
    :param url:
    :param method:
    :param kwargs:
    :return:
    """
    status_code = -1
    r_txt = None
    # "UHBBQRN3BGXCJQES	Z1PVPB6NVY1LICVX"
    #  UHBBQRN3BGXCJQES
    kwargs["proxies"] = {"http": "http://UHBBQRN3BGXCJQES:Z1PVPB6NVY1LICVX@httpproxy.c2567.com:9010"}
    kwargs["timeout"] = (10.0, 10.0)
    try:
        print(url)
        res = session.request(url=url, method=method, **kwargs)

        status_code = res.status_code
        r_txt = res.text
    except Exception as e:
        print(e)
    return status_code, r_txt


def session_send_http_no_proxy(session, url, method="get", **kwargs):
    """
    使用session 访问数据
    :param session:
    :param url:
    :param method:
    :param kwargs:
    :return:
    """
    status_code = -1
    r_txt = None
    # "UHBBQRN3BGXCJQES	Z1PVPB6NVY1LICVX"
    #  UHBBQRN3BGXCJQES
    # kwargs["proxies"] = {"http": "http://UHBBQRN3BGXCJQES:Z1PVPB6NVY1LICVX@httpproxy.c2567.com:9010"}
    kwargs["timeout"] = (10.0, 10.0)
    try:
        print(url)
        res = session.request(url=url, method=method, **kwargs)
        status_code = res.status_code
        r_txt = res.text
    except Exception as e:
        print(e)
    return status_code, r_txt


def session_send_http_ip_default(session, url, method="get", **kwargs):
    """
    使用session 访问数据
    :param session:
    :param url:
    :param method:
    :param kwargs:
    :return:
    """
    status_code = -1
    r_txt = None
    # "UHBBQRN3BGXCJQES	Z1PVPB6NVY1LICVX"
    #  UHBBQRN3BGXCJQES
    kwargs["proxies"] = {"http": "http://httpproxy.c2567.com:9010"}
    headers = kwargs['headers']
    proxy_client = "EUIZHURIDEMLJFW2"
    proxy_password = "5W7EHBCR6RGWUCY3"
    dd = base64.b64encode((proxy_client+"-sesion-300:"+proxy_password).encode("utf-8")).decode('utf-8')
    headers['proxy-authorization'] = "Basic " + dd
    kwargs["timeout"] = (10.0, 10.0)
    try:
        print(url)
        res = session.request(url=url, method=method, **kwargs)
        status_code = res.status_code
        r_txt = res.text
    except Exception as e:
        print(e)
    return status_code, r_txt


def session_send_http_ip_default_proxy(session, url, method="get", **kwargs):
    """
    使用session 访问数据
    :param session:
    :param url:
    :param method:
    :param kwargs:
    :return:
    """
    status_code = -1
    r_txt = None
    # "UHBBQRN3BGXCJQES	Z1PVPB6NVY1LICVX"
    #  UHBBQRN3BGXCJQES
    # 175.165.207.112:4274
    # http://182.38.78.63:4213
    kwargs["proxies"] = {"http": "http://175.165.207.112:4274"}
    kwargs["timeout"] = (10.0, 10.0)
    try:
        print(url)
        res = session.request(url=url, method=method, **kwargs)
        status_code = res.status_code
        r_txt = res.text
    except Exception as e:
        print(e)
    return status_code, r_txt

