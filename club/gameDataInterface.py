from util.dataInterface import *

@hadGetData("get_dagong_user_info_detail", True, 3)
def getUserInfoDetail(*args, **kwargs):
    baseInfo, record, onlineInfo = kwargs["ret"][0], kwargs["ret"][1], kwargs["ret"][2]
    if baseInfo is None:
        return ErrorCode.ERR_FAIL, None
    else:
        info = baseInfo[0]
        info["zhanji"] = record[0]["all_join"] if record != None else 0
        info["ip"] = onlineInfo[0]["IP"] if onlineInfo != None else ""
        #info["gps"] = [ int(onlineInfo[0]["GPS_X"]), int(onlineInfo[0]["GPS_Y"]) ] if onlineInfo != None else [-1,-1]
        return ErrorCode.ERR_OK, info


@hadGetData("get_top_player")
def getTopPlayer(*args, **kwargs):
    ret = kwargs["ret"]
    return ErrorCode.ERR_OK, ret

def get_user_uid_by_sid(sid):
    res = globalDB.Call('get_user_uid_by_sid',(sid,))
    if not res:
        return None
    else:
        return res[0]['uid']

@hadGetData("get_active_time")
def getPlayerActiveTime(uid, **kwargs):
    ret = kwargs["ret"][0]
    return ErrorCode.ERR_OK, ret

@hadGetData("set_active_time")
def updatePlayerActiveTime(*args, **kwargs):
    pass 

@hadGetData("get_all_club")
def getAllClub(self, **kwargs):
    ret = kwargs["ret"][0]

@hadGetData("get_round_account")
def getRoundAccount(*args, **kwargs):
    ret = kwargs["ret"]
    return ErrorCode.ERR_OK, ret

@hadGetData("get_round_history")
def getRoundHistory(*args, **kwargs):
    ret = kwargs["ret"][0]
    return ErrorCode.ERR_OK, ret


@hadGetData("get_reward")
def getSigninReward(*args, **kwargs):
    ret = kwargs["ret"][0]
    return ErrorCode.ERR_OK, ret

@hadGetData("get_reward")
def getShareReward(*args, **kwargs):
    ret = kwargs["ret"][0]
    return ErrorCode.ERR_OK, ret

# @hadGetData("update_gps")
# def updateGPS(*args, **kwargs):
#     pass

def updateGPS(*args, **kwargs):
    globalDB.Call("update_gps", args)

@hadGetData("get_hall_notic")
def getHallNotic(*args, **kwargs):
    ret = kwargs["ret"][0]
    return ErrorCode.ERR_OK, ret

@hadGetData("get_last_share_time")
def getPlayerShareTime(*args, **kwargs):
    ret = kwargs["ret"][0]
    return ErrorCode.ERR_OK, ret

def updatePlayerShareTime(*args, **kwargs):
    globalDB.Call("set_share_time", args)


def clearOnlineInfo():
    globalDB.Call("clear_online_info", ())

def saveOrder(uid, orderID, money):
    globalDB.Call('save_order', (uid,orderID, money))
    return ErrorCode.ERR_OK

@hadGetData("user_logout_update_online")
def logout_update_online_info(*args, **kwargs):
    pass 
