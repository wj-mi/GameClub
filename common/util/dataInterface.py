# coding:utf-8

"""数据接口

提供相应的参数,要求返回对应格式结果
目前仅为数据库,s2s
"""
from protocol import *
from DBHelper import *
from gameCfg  import GameCfg
from util.gameLog import gameLog
import simplejson as json
from datetime import *
import time

globalDB = DBHelper.getInstance().GetDefaultDB()
globalSlave = None

def hadGetData(cmd, mulValue=False, valueNum=-1):
    """必须依赖数据接口返回的数据方法，必须使用该装饰器来排除数据借口请求失败的情况

    mulValue表示结果有多个值, valueNum表示结果的个数
    """
    def _wrapper(func):
        def _hadGetData(*args, **kwargs):
            db = DBHelper.getInstance().GetDefaultDB()
            try:
                if mulValue == False:
                    ret = db.Call(cmd, args)
                else:
                    ret = db.CallMulRet(cmd, args, valueNum)
            except Exception, e:
                gameLog.debug("SQL QUERY %s(%s) ERROR [%s:%s]" % (cmd, str(args), sys.exc_info()[0], sys.exc_info()[1]))
                return ErrorCode.ERR_FAIL, []
            if ret is None:
                gameLog.debug("SQL QUERY %s(%s) ret is None" % (cmd, str(args)))
                return ErrorCode.ERR_FAIL, []
            else:
                kwargs["ret"] = ret
                return func(*args, **kwargs)
        return _hadGetData
    return _wrapper



@hadGetData("get_user_nickname")
def getUserNickname(uid, **kwargs):
    err, data = ErrorCode.ERR_OK, kwargs['ret'][0]['nickName']
    return err, data 


def getCode():
    """生成房间的邀请码
    """
    err, data = globalSlave.sendToServer(TagType.TAG_NONAME, 257, {"tag":GameCfg.gameTagCfg}, 1)
    return data 

def returnCode(code):
    """返还房间的邀请码
    """
    globalSlave.sendToServer(TagType.TAG_NONAME, 258, {"tag":GameCfg.gameTagCfg, "code":code}, 0)

@hadGetData("get_user_info", True, 2)
def getUserInfo(uid, **kwargs):
    if kwargs["ret"][0] is None:
        return ErrorCode.ERR_FAIL, None
    info = kwargs["ret"][0][0]
    online = kwargs["ret"][1]
    info["IP"] = online[0]["IP"] if online != None else ""
    return ErrorCode.ERR_OK, info


def _getStartTime():
    nowDate = datetime.fromtimestamp(int(time.time()))
    # today
    today = nowDate.replace(hour=0, minute=0, second=0)
    todayTimestap = int(time.mktime(today.timetuple()))
    # this week
    thisWeek = nowDate.replace(hour=0, minute=0, second=0)
    thisWeek = thisWeek - timedelta(days=thisWeek.weekday())
    thisWeekTimestap = int(time.mktime(thisWeek.timetuple()))
    # this moth
    thisMonth = nowDate.replace(hour=0, minute=0, second=0)
    thisMonth = thisMonth - timedelta(days=thisMonth.day-1)
    thisMonthTimestap = int(time.mktime(thisMonth.timetuple()))
    return int(time.time()), todayTimestap, thisWeekTimestap, thisMonthTimestap

getStartTime = _getStartTime

#@hadGetData(GameCfg.updateRecordSP)
def updateGameRecord(uid, all_join, is_win, **kwargs):
    nowTime, todayTime, weekTime, monthTime = _getStartTime()
    args = (uid, all_join, is_win, nowTime, todayTime, weekTime, monthTime)
    globalDB.Call(GameCfg.updateRecordSP, args)

@hadGetData("get_user_GPS")
def getUserGPS(uid, **kwargs):
    if kwargs["ret"][0] is None:
        return ErrorCode.ERR_FAIL, None
    ret = kwargs["ret"][0]
    return ErrorCode.ERR_OK, ret

@hadGetData("get_user_room_card")
def getPlayerRoomCard(uid, **kwargs):
    if kwargs["ret"][0] is None:
        return ErrorCode.ERR_FAIL, None
    ret = kwargs["ret"][0]["room_card"]
    return ErrorCode.ERR_OK, ret


@hadGetData("update_user_room_card")
def updatePlayerRoomCard(*args, **kwargs):
    pass 

@hadGetData("update_had_join_room")
def upadteHadJoinRoom(*args, **kwargs):
    pass 

@hadGetData("get_had_join_room")
def getHadJoinRoom(*args, **kwargs):
    if kwargs["ret"][0] is not None:
        data = kwargs["ret"][0]["had_join_room"]
    else:
        data = None
    return ErrorCode.ERR_OK, data


@hadGetData("get_room_account")
def getRoomAccount(roomID, roomType, **kwargs):
    return ErrorCode.ERR_OK, kwargs["ret"][0]


@hadGetData("record_history")
def recordHistory(roomType, roomID, roundID, info, account, index, time, **kwargs):
    pass


def get_user_uid_by_sid(sid):
    res = globalDB.Call('get_user_uid_by_sid',(sid,))
    if not res:
        return None
    else:
        return res[0]['uid']

@hadGetData("user_logout_update_online")
def logout_update_online_info(*args, **kwargs):
    pass 
