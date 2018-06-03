#-*- coding: utf-8 -*-
#Author:Royce

import ConfigParser
class Config(object):
    __slots__ = ['_cfgFile','_section','_fileName']
    def __init__(self,fileName = None):
        self._cfgFile = None
        self._section = None
        self._fileName = None
        
        if fileName:
            self._cfgFile = ConfigParser.ConfigParser()
            if self._cfgFile.read(fileName) != [fileName]:
                raise "Read config file failed"
            self._fileName = fileName
     
    def close(self):
        self._cfgFile.close()
        self._cfgFile = None
        
    def __iter__(self):
        if not self._section:
            yield ()
        for item in self._cfgFile.items(self._section):
            yield item
    
    def __repr__(self):
        return "(%s [file:%s])" % (self.__class__.__name__,self._fileName) 
     
    def read(self,fileName):
        if self._cfgFile.read(fileName) != [fileName]:
            return False
        else:
            self._section = None
            self._fileName = fileName
            return True
    #
    def enter(self,section):
        if section not in self._cfgFile.sections():
            self._section = None
            return False
        else:
            self._section = section
            return True
        
    def __getattr__(self,name):
        try:
            return object.__getattr__(self, name)
        except AttributeError,ae:
            if not self._section:       return None
            try:
                return self._cfgFile.get(self._section,name)
            except ConfigParser.NoOptionError,noe:  return None
            
    def get(self,name): return self.__getattr__(name)
    
