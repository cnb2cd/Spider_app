import  requests
class HttpRequst:
    def __init__(self):
        self.session=requests.session()

    @classmethod
    def httpGets(self,url,**kwargs):
        print (**kwargs)
        if type=='get':
            r=self.session.get(url,**kwargs)
            text=r.text
            status=r.status_code
            cookie=r.cookies
        elif type=='post':
            r =self.session.post(url,**kwargs)
            text = r.text
            status = r.status_code
            cookie = r.cookies


    def http(self,url,**kwargs):
       self.httpGets(self,url,**kwargs)
h=HttpRequst()
header={'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
               'Accept - Encoding':'gzip, deflate',
               'Accept-Language':'zh-Hans-CN, zh-Hans; q=0.5',
               'Connection':'Keep-Alive',
               'Host':'zhannei.baidu.com',
               'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
h.http("https://api.github.com/events",headers=header)













