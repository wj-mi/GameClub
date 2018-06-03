#coding:utf-8
import struct
class SessionID:
    def __init__(self,raw_data=None,str_data=None):
        self.__data = raw_data
        self.__rid  = -1
        self.__cid  = -1
        self.__sid  = -1
        if isinstance(self.__data,str):
            self.__rid,self.__cid,self.__sid = struct.unpack("=3I",self.__data)
        if str_data:    self.__rid,self.__cid,self.__sid = [ int(i) for i in str_data.split(',') ]
            
    def __hash__(self):   
        if (self.__sid == -1) or (self.__sid == 0xFFFFFFFF):    raise "Invalid session-id:%s,%s,%s" %(self.__rid,self.__cid,self.__sid)
        return self.__sid & 0xFFFFFFFF
    def __cmp__(self,ot):   
        if self.__rid < ot.__rid or self.__cid < ot.__cid or self.__sid < ot.__sid :   return -1
        if self.__rid > ot.__rid or self.__cid > ot.__cid or self.__sid > ot.__sid :   return 1
        if all( (self.__rid == ot.__rid,self.__cid == ot.__cid,self.__sid == ot.__sid) ):   return 0
        return -1
        
    def fromStr(self,s):    self.__rid,self.__cid,self.__sid = [ int(i) for i in s.split(',') ]

    @property
    def RID(self):  return self.__rid & 0xFFFFFFFF
    @property
    def CID(self):  return self.__cid & 0xFFFFFFFF
    @property
    def SID(self):  return self.__sid & 0xFFFFFFFF
    
    @property
    def data(self):
        if not self.__data:
            self.__data = struct.pack("3I",self.__rid,self.__cid,self.__sid)
        return self.__data
    def __str__(self):  return "%ld,%ld,%ld" % (self.__rid & 0xFFFFFFFF,self.__cid & 0xFFFFFFFF,self.__sid & 0xFFFFFFFF)
    def __repr__(self): return "router-id:%ld,conn-id:%ld,sid:%ld" % (self.__rid & 0xFFFFFFFF,self.__cid & 0xFFFFFFFF,self.__sid & 0xFFFFFFFF)
        
            
