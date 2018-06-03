# coding:utf-8

from util.packUtils import genGamePackUtil
from util.gameLog import gameLog
from SlaveBase  import SlaveBase, S2S, C2S
from gameCfg import GameCfg
from protocol import *
from accountManager import AccountManager



class GameSlave(SlaveBase):
    def __init__(self):
        super(GameSlave, self).__init__()
        self._tags = [ GameCfg.gameTagCfg, TagType.TAG_STATUS ]
        super(GameSlave, self)._initialize()
        self.PackClass = genGamePackUtil(PackKey)
        self._gameTag = self._tags[0]
        self._accountManager = AccountManager.getInstance()
        self._accountManager.setSlave(self)

    def sendToServer(self, tagType, packType, data, module):
        return self.SetSlaveMsg(packType, tagType, data, module)

    #########################

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_USER_INFO)
    def getUserInfo(self, pack):
        err, data = self._accountManager.getUserInfo(pack)
        gameLog.info("player get user info ret is %d %s" %(err, str(data)))
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_USER_INFO_DETAIL)
    def getUserInfoDetail(self, pack):
        uid = pack.BODY
        err, data = self._accountManager.getUserInfoDetail(uid)
        gameLog.info("get user %d info detail, ret is %d %s" %(uid, err, str(data)))
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_TOP_PLAYER)
    def getTopPlayer(self, pack):
        err, data = self._accountManager.getTopPlayer()
        gameLog.info("get top player, ret is %s" %(data,))
        return err, data 

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_PLAY_TODAY)
    def playToday(self, pack):
        uid = pack.UID
        err, data = self._accountManager.playerToday(uid)
        gameLog.info("playToday, ret is %s" %(data,))
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_SIGNUP_INFO)
    def  getSignupInfo(self, pack):
        uid = pack.UID
        err, data = self._accountManager.getSignupInfo(uid)
        gameLog.info("getSignupInfo, ret is %s" %(data,))
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_ALL_RECORD)
    def getAllRecord(self, pack):
        uid = pack.UID 
        count = pack.BODY["count"]
        err, data = self._accountManager.getAllRecord(uid, count)
        gameLog.info("user %d get all record, ret is %s" %(uid, data))
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_ROUND_ACCOUNT)
    def getRoundAccount(self, pack):
        body = pack.BODY
        roomID, roomType = body["roomID"], body["type"]
        err, data = self._accountManager.getRoundAccount(roomType, roomID)
        gameLog.info("getRoundAccount roomType [%d] roomID [%d] data[%s]" %(roomType, roomID, str(data)))
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_ROUND_HISTORY)
    def getRoundAccount(self, pack):
        body = pack.BODY
        roomID, roomRound, roomType = body["roomID"], body["round"], body["type"]
        err, data = self._accountManager.getRoundHistory(roomType, roomID, roomRound)
        gameLog.info("getRoundHistory roomType [%d] roomID [%d] roundID [%d]" %(roomType, roomID, roomRound))
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_UPDATE_GPS)
    def updateGPS(self, pack):
        body = pack.BODY
        uid, GPS_X, GPS_Y = body["uid"], body["gps_x"], body["gps_y"]
        err, data = self._accountManager.updateGPS(uid, GPS_X, GPS_Y)
        #gameLog.info("updateGPS update GPS")
        return err, data


    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_SHARE_APP)
    def shareApp(self, pack):
        uid = pack.UID
        #uid, shareType = body["uid"], body["shareType"]
        err, data = self._accountManager.shareApp(uid)
        gameLog.info(str("[%d] shareApp ret %s" %(uid, str(data))))
        return err, data


    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_USER_HAD_IN_ROOM)
    def playerHadInRoom(self, pack):
        uid = pack.Fetch("BODY")
        dagongErr, dagongData = self.sendToServer(TagType.TAG_DAGONG, GamePackType.S2S_GET_PLAYER_IN_ROOM, uid, 1)
        majiangErr, majiangData = self.sendToServer(TagType.TAG_MAJIANG, GamePackType.S2S_GET_PLAYER_IN_ROOM, uid, 1)
        shisanzhangErr, shisanzhangData = self.sendToServer(TagType.TAG_SHISANZHANG, GamePackType.S2S_GET_PLAYER_IN_ROOM, uid, 1)
        if dagongErr != ErrorCode.ERR_OK:
            dagongData = -1
        if majiangErr != ErrorCode.ERR_OK:
            majiangData = -1
        if shisanzhangErr != ErrorCode.ERR_OK:
            shisanzhangData = -1
        index = -1
        for tmp in [dagongData, majiangData, shisanzhangData]:
            if tmp != -1:
                index = tmp
                break
        #index =  #dagongData if dagongData != -1 else majiangData
        #gameLogC2S(uid, "playerHadInRoom", -1, ErrorCode.ERR_OK, data)
        return ErrorCode.ERR_OK, {"roominfo": index}

    # @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_USER_GPS)
    # def getUserInfoDetail(self, pack):
    #     uid = pack.BODY
    #     err, data = self._accountManager.getUserGPS(uid)
    #     gameLog.info("get user %d GPS, ret is %d %s" %(uid, err, str(data)))
    #     return err, data

    # @S2S(PackType.PT_NOTIFY)
    # def OnS2SNotify(self, pack):
    #     print "+++++++++++++++++ S2s NOTIFY"
    #     tp = pack.TYPE 
    #     if tp == NotifyType.NT_CLIENT_LOST:
    #         self._accountManager.userLost(pack)
    #     elif tp == NotifyType.NT_CLIENT_COME:
    #         self._accountManager.userLogin(pack)

    def login(self, sid, rid):
        self._accountManager.userLogin(sid, rid)

    def logout(self, sid):
        self._accountManager.userLost(sid)

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_SAVE_ORDER)
    def saveOrder(self, pack):
        data = pack.BODY
        uid, orderID, money = data["uid"], data["orderID"], data["money"]
        err, data = self._accountManager.saveOrder(uid, orderID, money)
        gameLog.info("saveOrder save [%d] order[%s] num[%d], ret [%s]" %(uid, orderID, int(money), str(data)))
        return err, data


