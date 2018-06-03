# -*- coding:UTF-8 -*-
"""基本Slave类,主要用来做包的接收和发送

对Slave通用的功能进行封装
!!!!!! 警告
目前一个slave实例只接受一种Tag
"""

from SlaveBase  import SlaveBase, S2S, C2S
from util.gameLog   import gameLog
from protocol import *
from util.roomCollection import roomCollection
from util import dataInterface
from gameCfg import GameCfg
import stackless
from util.packUtils import genGamePackUtil
from gameManager import GameManager 
from SessionID import SessionID

def findRoom(func):
    def _findRoom(self, pack, **kwargs):
        roomID = pack.Fetch("ROOMID")
        room = roomCollection.getRoom(roomID)
        if room is None:
            gameLog.info("not find room [%d] in collection" %int(roomID))
            return ErrorCode.ERR_FAIL, -1 
        else: 
            kwargs["room"] = room
            return func(self, pack, **kwargs)
    return _findRoom

class BaseGameSlave(SlaveBase):
    def __init__(self):
        super(BaseGameSlave, self).__init__()
        self._tags = self._getTag()
        super(BaseGameSlave, self)._initialize()
        self.PackClass = genGamePackUtil(GamePackKey)
        self._gameTag = self._tags[0]
        self._gameManager = None
        self._handleGameManager()
        dataInterface.globalSlave = self
        self._sid_uid_table = {}
        
    def _getTag(self):
        return [ GameCfg.gameTagCfg,TagType.TAG_STATUS ]

    def _handleGameManager(self):
        self._gameManager = GameManager.getInstance()
        self._gameManager._initialize(self)

    def _getManager(self, itemID):
        return self._gameManager

    def sendToServer(self, tagType, packType, data, module):
        return self.SetSlaveMsg(packType, tagType, data, module)

    def gameLogC2S(self, uid, action, roomID, err, data):
        gameLog.info("c2s:   uid:%d action:%s, roomID:%d, ret is err:%d, data:%s"\
                      %(uid, action, roomID, err, str(data)))

    def gameLogS2S(self, cmd, body, err, data={}):
        gameLog.info("s2s:   cmd:%s body:%s ,ret err: %d, data:%s" %(cmd, str(body), err, str(data)) )

    def ProcessRegResult(self,msg):
        super(BaseGameSlave, self).ProcessRegResult(msg)
        import gameTest

    ##################### c2s ##################

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_CREATE_ROOM)
    def createRoom(self, pack):
        body = pack.BODY
        err, roomInfo = self._gameManager.createRoom(body)
        self.gameLogC2S(body["creatorID"], "createRoom", -1, err, roomInfo)
        return err, roomInfo
        #{'cards': [26, 53, 67, 94, 42, 82, 69, 96, 18, 83, 32, 84, 6, 19, 33, 98, 85, 34, 22, 74, 62, 10, 76, 38, 25, 90, 103], 'banker': 1}
        #roomInfo#{'baseRoomInfo': {'status': 1, 'roomID': 95}}
#roomInfo

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_ENTER_ROOM)
    def enterRoom(self, pack, **kwargs):
        uid, sid, index = pack.Fetch("UID", "SID", "BODY")
        str_sid = str(SessionID(sid))
        t_uid = self._sid_uid_table.get( str_sid,None ) #dataInterface.get_user_uid_by_sid(str(SessionID(sid)))

        gameLog.error("---------------------------------------------------------client send %s    %s  check %s " %(str_sid,str(uid), str(t_uid)))
        if t_uid is not None and uid != t_uid:
            gameLog.error("-------------------------------------------------fuck you %d" %(uid))
            return ErrorCode.ERR_FAIL, None
        room = None
        for roomID in self._gameManager._rooms:
            tmpRoom = self._gameManager._rooms[roomID]
            if tmpRoom.index == index:
                room = tmpRoom
        if room is None:    
            return ErrorCode.ERR_FAIL, None
        #room = kwargs["room"]
	self._sid_uid_table[str_sid] = uid
        err, data = room.c2s_enterRoom(uid, sid, None)

        self.gameLogC2S(uid, "enterRoom", index, err, data)
        return err, data 


    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_SEND_AUDIO)
    @findRoom
    def sendAudio(self, pack, **kwargs):
        uid, roomID, info = pack.Fetch("UID", "ROOMID", "BODY")
        room = kwargs["room"]
        err, data = room.sendAudio(uid, info)
        #self.gameLogC2S(info["uid"], "sendAudio", roomID, err, data)
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_READY)
    @findRoom
    def playerReady(self, pack, **kwargs):
        uid, roomID, opt =  pack.Fetch("UID", "ROOMID", "BODY")
        room = kwargs["room"]
        err, data = room.playerReady(uid, opt)
        self.gameLogC2S(uid, "playerReady", roomID, err, data)
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_USER_GPS)
    @findRoom
    def getPlayerGPS(self, pack, **kwargs):
        uid, roomID = pack.Fetch("UID", "ROOMID")
        room = kwargs["room"]
        err, data = room.getPlayerGPS()
        self.gameLogC2S(uid, "getPlayerGPS", roomID, err, data)
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_USER_GPS_TWO)
    @findRoom
    def getPlayerGPSTwo(self, pack, **kwargs):
        uid, roomID = pack.Fetch("UID", "ROOMID")
        room = kwargs["room"]
        err, data = room.getPlayerGPS()
        self.gameLogC2S(uid, "getPlayerGPS", roomID, err, data)
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_USER_GPS_THREE)
    @findRoom
    def getPlayerGPSThree(self, pack, **kwargs):
        uid, roomID = pack.Fetch("UID", "ROOMID")
        room = kwargs["room"]
        err, data = room.getPlayerGPS()
        self.gameLogC2S(uid, "getPlayerGPS", roomID, err, data)
        return err, data


    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_USER_DISSOLVE)
    @findRoom
    def playerChooseDissolve(self, pack, **kwargs):
        uid, roomID,choose = pack.Fetch("UID", "ROOMID", "BODY")
        room = kwargs["room"]
        err, data = room.chooseDissolve(uid, choose)
        self.gameLogC2S(uid, "playerDissolve", roomID, err, data)
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_LEAVE_ROOM)
    @findRoom
    def playerLeaveRoom(self, pack, **kwargs):
        uid, roomID = pack.Fetch("UID", "ROOMID")
        room = kwargs["room"]
        err, data = room.playerLeaveRoom(uid)
        self.gameLogC2S(uid, "playerLeaveRoom", roomID, err, data)
        return err, data

    #@C2S(GameCfg.gameTagCfg, GamePackType.C2S_LEAVE_ROOM)
    #@findRoom
    #def addRoomLife(self, pack):
        #uid, roomID = 
    #    pass
    #     data = self._gameManager.

    '''
    @S2S(GamePackType.S2S_USER_LOGIN_LOGOUT)
    def userLoginLogout(self, pack):
        body = pack.BODY
        rid, status = body[0], body[1]
        #gameLog.info("user %d login_logout %d" %(rid, status))
        self._gameManager.userLoginLogout(rid, status)
        return TagType.TAG_ACCOUNT, ErrorCode.ERR_OK, {}
    '''
    @S2S(GamePackType.S2S_GET_PLAYER_IN_ROOM)
    def S2S_getPlayerInRoom(self, pack):
        uid = pack.BODY
        data = self._gameManager.checkHadInRoom(uid)
        #self.gameLogS2S(uid, "s2s_playerHadInRoom", -1, ErrorCode.ERR_OK, data)
        return TagType.TAG_ACCOUNT, ErrorCode.ERR_OK, data
    

    # @S2S(GamePackType.S2S_INDEX_IN_SERVER)
    # def indexInServer(self, pack):
    #     index = pack.BODY
    #     gameLog.info("get index [%d]  in_server" %(index,))
    #     body = self._gameManager.indexInServer(index)
    #     return TagType.TAG_NONAME, ErrorCode.ERR_OK, body

    def _enter(self):
        task = stackless.getcurrent()
        return task.set_atomic(True)
        #
    pass

    def _exit(self,old_atomic):   
        if old_atomic: return
        task = stackless.getcurrent()
        task.set_atomic(False)

    def login(self, sid, rid):
	old_atomic = self._enter()
        str_sid = str(sid)
        gameLog.error("-------------------------------------------------login %s     %s" %( str(rid),str_sid) )
        old_rid = self._sid_uid_table.get( str_sid,None )
        if old_rid and old_rid != rid:
	    gameLog.error("--------------------------- rid ...")
            self._gameManager.userLoginLogout(old_rid, 1)
        #
        self._sid_uid_table[str_sid] = rid
        self._gameManager.userLoginLogout(rid, 0)
        self._exit(old_atomic)
        #

    def logout(self, sid):
	old_atomic = self._enter()
        str_sid = str(sid)
        rid = self._sid_uid_table.pop(str_sid,None)
        gameLog.error("-------------------------------------------------logout %s     %s" %( str(rid),str_sid) )
        data = dataInterface.get_user_uid_by_sid(str_sid)
	dataInterface.logout_update_online_info(rid, str_sid)
        gameLog.error("---------------------------------check db -----------logout %s  " %(str(data),) )
        #
        if rid and data and data == rid:
	#if rid:
            self._gameManager.userLoginLogout(rid, 1)
        self._exit(old_atomic)
        #
