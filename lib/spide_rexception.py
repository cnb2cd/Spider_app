class spiderexception(Exception):
    def __init__(self,m,*args):
        self.args = args
        str='exception messgae is :';
        for my_info in args:
           str= str+my_info+","
        str=str+"Trace message is{}:"+m
        # log.err(str)


        # finename='a.txt'
        # with open(finename,'w') as w:
        #     w.write(str)
        #     w.close()





