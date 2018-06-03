# coding: utf-8
from protocol import *
from DBHelper import *

from util.gameLog import gameLog
import simplejson as json

globalDB = DBHelper.getInstance().GetDefaultDB()
globalSlave = None

def hadGetData(cmd, mulValue=False, valueNum=-1):
    """必须依赖数据接口返回的数据方法，必须使用该装饰器来排除数据借口请求失败的情况

    mulValue表示结果有多个值, valueNum表示结果的个数
    """
    def _wrapper(func):
        def _hadGetData(*args, **kwargs):
            try:
                if mulValue == False:
                    ret = globalDB.Call(cmd, args)
                else:
                    ret = globalDB.CallMulRet(cmd, args, valueNum)
            except Exception, e:
		print "------->:", e
                #gameLog.debug("SQL QUERY %s(%s) ERROR [%s:%s]" % (cmd, str(args), sys.exc_info()[0], sys.exc_info()[1]))
                return ErrorCode.ERR_FAIL, None
            if ret is None:
                #gameLog.debug("SQL QUERY %s(%s) ret is None" % (cmd, str(args)))
                return ErrorCode.ERR_FAIL, None
            else:
                kwargs["ret"] = ret
                return func(*args, **kwargs)
        return _hadGetData
    return _wrapper

@hadGetData("user_login_in")
def userLogin(wx_id, nickname, gender, avatar, **kwargs):
    err, data = ErrorCode.ERR_OK, kwargs["ret"][0]
    return err, data


@hadGetData("user_login_update_online")
def login_update_online_info(*args, **kwargs):
    pass 

@hadGetData("user_logout_update_online")
def logout_update_online_info(*args, **kwargs):
    pass 


@hadGetData("update_user_agent")
def update_user_agent(*args, **kwargs):
    pass

def clearOnlineInfo():
    globalDB.Call("clear_online_info", ())


@hadGetData("get_sid_info")
def getSIDInfo(*args, **kwargs):
    err, data = ErrorCode.ERR_OK, kwargs["ret"][0]
    return err, data

