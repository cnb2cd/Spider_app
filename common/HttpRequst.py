import  requests
class HttpRequst:
    def __init__(self):
        self.session=requests.session()

    @classmethod
    def httpGets(self,type,url,data,header):
        if type=='get':
            r=self.session.get(url,headers=header)
            text=r.text
            status=r.status_code
            cookie=r.cookies
        elif type=='post':
            r =self.session.post(url,data=data, headers=header)
            text = r.text
            status = r.status_code
            cookie = r.cookies

    def http(self,url,header):
       self.httpGets(self,url,'get',None,header)

    def http(self,url,type,data,header):
        if(data==None):
            parms={}
            self.httpGets(self,url,type,parms,header)
        else:
            self.httpGets(self,url,type,data,header)












