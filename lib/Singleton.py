#!/usr/local/bin/python2.5
import threading
import sys

class Singleton(object):
    class SException(Exception):
        def __init__(self,arg):
            Exception.__init__(self)
            self.arg = arg
            
    def __init__(self):
        pass
            
    def __new__(self, *args, **kwargs):
        name = '_Sigleton|%s|_'%self.__name__
        inst = sys.modules.get(name)
        if inst is not None:    raise Singleton.SException(inst)
        else:   
            inst = object.__new__(self, args, kwargs)
            sys.modules[name] = inst
        return inst
   
def getInstance(x=Singleton):
    try:
        inst = x()
    except Singleton.SException,s:
        inst = s.arg
    return inst   
    

