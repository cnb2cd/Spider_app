# --*-- coding:utf-8 --*--
"""
@author pxm
@time  2018/10/11 19:10
@desc email send
"""
import logging
log=logging.getLogger()
class spiderexception(Exception):
    def __init__(self,m,*args):
        self.args = args
        str='exception messgae is :';
        for my_info in args:
           str= str+my_info+","
        str=str+"Trace message is{}:"+m
        log.error(str)


        # finename='a.txt'
        # with open(finename,'w') as w:
        #     w.write(str)
        #     w.close()





