# -*- coding: UTF-8 -*-


from util.gameLog import gameLog
import Singleton
import gameDataInterface
from protocol import *
from SessionID import SessionID
from datetime import datetime, timedelta
import time
import simplejson as json

class AccountManager(Singleton.Singleton):
    def __init__(self,**kwargs):
        super(AccountManager,self).__init__()
        #self._accounts = {}     # 保存玩家SID到UID的映射
        self._slave = None
        #
    
    def setSlave(self, slave):  self._slave = slave

    @staticmethod
    def getInstance():  return Singleton.getInstance(AccountManager)

    def getUserInfo(self, pack):
        """ 获取个人信息
        """
        sid = SessionID(pack.SID)
        receiveUID = pack.UID
        #uid = self._accounts.get(sid.SID, None)
        uid = gameDataInterface.get_user_uid_by_sid(str(sid))
        if uid is None:
            gameLog.info("get user info [%s] but not find" %str(receiveUID))
            return ErrorCode.ERR_FAIL, None
        err, info = gameDataInterface.getUserInfo(uid)
        #dagongErr, dagongData = self._slave.sendToServer(TagType.TAG_DAGONG, GamePackType.S2S_GET_PLAYER_IN_ROOM, {}, 1)
        #majiangErr, majiangData = self._slave.sendToServer(TagType.TAG_MAJIANG, GamePackType.S2S_GET_PLAYER_IN_ROOM, {}, 1)
        #info["roomInfo"] = 
        return err, info 

    def userLogin(self, sid, rid):
        gameLog.info("user [%d] login" %(rid,))
        #self._accounts[sid.SID] = rid
        self._slave.sendToServer(TagType.TAG_DAGONG, GamePackType.S2S_USER_LOGIN_LOGOUT, [rid, 0], 0)
        self._slave.sendToServer(TagType.TAG_MAJIANG, GamePackType.S2S_USER_LOGIN_LOGOUT, [rid, 0], 0)
        self._slave.sendToServer(TagType.TAG_SHISANZHANG, GamePackType.S2S_USER_LOGIN_LOGOUT, [rid, 0], 0)


    def userLost(self, sid):
	gameLog.info("sid %s logout" %(str(sid),))
        #rid = self._accounts.pop(sid.SID, None)
        rid = gameDataInterface.get_user_uid_by_sid(str(sid))
        gameLog.info("user [%s] logout" %(str(rid),))
        if rid is not None:
	    #gameDataInterface.logout_update_online_info(rid, str(sid)) 
            self._slave.sendToServer(TagType.TAG_DAGONG, GamePackType.S2S_USER_LOGIN_LOGOUT, [rid, 1], 0)
            self._slave.sendToServer(TagType.TAG_MAJIANG, GamePackType.S2S_USER_LOGIN_LOGOUT, [rid, 1], 0)
            self._slave.sendToServer(TagType.TAG_SHISANZHANG, GamePackType.S2S_USER_LOGIN_LOGOUT, [rid, 1], 0)


    def getUserInfoDetail(self, uid):
        err, data = gameDataInterface.getUserInfoDetail(uid)
        return err, data

    def getTopPlayer(self):
        nowTime, todayBegin, weekBegin, monthBegin = gameDataInterface.getStartTime()
        err, data = gameDataInterface.getTopPlayer(todayBegin, weekBegin, monthBegin)
        #data = json.dumps(data)
        return err, data


    def playerToday(self, uid):
        err, data = gameDataInterface.getPlayerActiveTime(uid)
        gameLog.info("player [%d] play today, ret is [%d]" %(uid, err))
        if err == ErrorCode.ERR_OK:
            #
            newLastTime = int(time.time())
            newContinue = 1
            #
            if data is None:
                lastTime = -1
            else:
                lastTime = data["last_active_time"]
                continueTime = data["continue_time"]
            if lastTime is None or lastTime == -1:
                pass
            else:
                dateLastTime = datetime.fromtimestamp(lastTime)
                nowDate = datetime.fromtimestamp(newLastTime)
                if dateLastTime.day == nowDate.day and dateLastTime.year == nowDate.year and dateLastTime.month == nowDate.month:
                    return ErrorCode.ERR_FAIL, None
                newContinue  = continueTime + 1
            giveCard = 0
            if newContinue >= 7:
                err, rewardInfo = gameDataInterface.getSigninReward(3)
                rewardType, rewardNum = 0, rewardInfo["Value"]
                giveCard = int(rewardNum)
                gameDataInterface.updatePlayerRoomCard(uid, giveCard, int(time.time()), 1, -1, -1)
                newContinue = 0
            sendInfo = {"roomCard": giveCard, "day": newContinue}
            gameDataInterface.updatePlayerActiveTime(uid, newLastTime, newContinue)
            return ErrorCode.ERR_OK, sendInfo
        else:
            return err, None
                #

    def getSignupInfo(self, uid):
        err, data = gameDataInterface.getPlayerActiveTime(uid)
        info = {}
        if err == ErrorCode.ERR_OK:
            lastTime = data["last_active_time"]
            if lastTime != -1:
                dateLastTime = datetime.fromtimestamp(lastTime)
                nowDate = datetime.fromtimestamp(int(time.time()))
                info["today"] = 1 if dateLastTime.day == nowDate.day and dateLastTime.year == nowDate.year and dateLastTime.month == nowDate.month else 0
            else:
                info['today'] = 0
            info["day"] = 0 if data is None else data["continue_time"]
        err, data = gameDataInterface.getSigninReward(3)
        if err == ErrorCode.ERR_OK:
            info["num"] = int(data["Value"]) 
        else:
            info["num"] = 0
        return err, info

    def getAllRecord(self, uid, count):
        err, data = gameDataInterface.getHadJoinRoom(uid)
        if err != ErrorCode.ERR_OK or data is None or len(data) == 0:
            return ErrorCode.ERR_OK, []
        roomIDs = eval(data)
        info = []
        for roomInfo in roomIDs[count:count+5]:
            roomID, roomType = roomInfo[0], roomInfo[1]
            err, data = gameDataInterface.getRoomAccount(roomID, roomType)
            if err == ErrorCode.ERR_OK:
                data["account"] = eval(data['account'])
                data["type"] = roomType
                info.append(data)
        return ErrorCode.ERR_OK, info        

    def updateGPS(self, uid, GPS_X, GPS_Y):
        gameDataInterface.updateGPS(uid, GPS_X, GPS_Y)
        return ErrorCode.ERR_OK, {}

    def getRoundAccount(self, roomType, roomID):
        err, data = gameDataInterface.getRoundAccount(roomType, roomID)
        for item in data:
            item["account"] = eval(item["account"])
        #data = eval(str(data))
        #data = [ eval(item) for item in data ]
        return err, data

    def getRoundHistory(self, roomType, roomID, roomRound):
        err, data = gameDataInterface.getRoundHistory(roomType, roomID, roomRound)
        return err, {"type": roomType, "data": data}
        

    def shareApp(self, uid):
        msg = "分享成功"
        #
        err, data = gameDataInterface.getPlayerShareTime(uid)
        if err == ErrorCode.ERR_OK:
            #
            newLastTime = int(time.time())
            #
            if data is None:
                lastTime = -1
            else:
                lastTime = data["last_share_time"]
            if not (lastTime is None or lastTime == -1):
                dateLastTime = datetime.fromtimestamp(lastTime)
                nowDate = datetime.fromtimestamp(newLastTime)
                if dateLastTime.day == nowDate.day and dateLastTime.year == nowDate.year and dateLastTime.month == nowDate.month:
                    return err, {"content":msg}
            err, rewardInfo = gameDataInterface.getShareReward(2)
            if err == ErrorCode.ERR_OK:
                rewardType, rewardNum = 0, int(rewardInfo["Value"])
                gameDataInterface.updatePlayerRoomCard(uid, rewardNum, int(time.time()), 2, -1, -1)
                gameDataInterface.updatePlayerShareTime(uid, newLastTime)
                msg += "恭喜您获得%d张房卡" %(rewardNum,)
        sendMsg = {"content": msg}
        return err, sendMsg

    def saveOrder(self, uid, orderID, money):
        err = gameDataInterface.saveOrder(uid, orderID, money)
        return err, {}

