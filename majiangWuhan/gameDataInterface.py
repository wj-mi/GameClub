# coding: utf-8
from util.dataInterface import *
import simplejson as json

@hadGetData("create_majiang_wuhan_room")
def createMajiangWuhan(*args, **kwargs):
    err, data = ErrorCode.ERR_OK, kwargs['ret'][0]['room_id']
    return err, data

@hadGetData("majiang_wuhan_close_room")
def closeRoom(*args, **kwargs):
    pass 




