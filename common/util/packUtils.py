#coding:utf-8

from protocol.GeneralPack import GeneralPack
from protocol import *


"""
def genGamePackUtil(packKey):
    class GamePack(GeneralPack):
        def __init__(self, data=None):
            GeneralPack.__init__(self, data, packKey)
    return GamePack 
"""

def genGamePackUtil(packKey):
    def GamePack(data=None):
        return GeneralPack(data,packKey)
    return GamePack