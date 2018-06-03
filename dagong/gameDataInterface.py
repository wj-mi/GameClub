# coding: utf-8
from util.dataInterface import *
import simplejson as json

@hadGetData("create_dagong_room")
def createDagong(*args, **kwargs):
    err, data = ErrorCode.ERR_OK, kwargs['ret'][0]['room_id']
    return err, data

@hadGetData("dagong_close_room")
def closeRoom(*args, **kwargs):
    pass 