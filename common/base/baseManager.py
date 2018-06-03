# coding:utf-8

"""管理类基类
"""


from util.gameLog import gameLog
from protocol import *
from gameRoom import *
import util.noRepeatNum as noRepeatNum
#import util.dataInterface as noRepeatNum

import gameDataInterface
import time
import Singleton
from gameCfg import GameCfg

class BaseManager(object):
    """ 这样做的目的是： 有的进程需要Manager不是单例
    """
    def __init__(self):
        self._slave = None
        self._rooms = {}

    def _initialize(self, slave):
        self._slave = slave

    def _writeDB(self, data):
        pass

    def _genRoom(self, data):
        return GameRoom(data)

    # 创建房间
    def createRoom(self, data):
        gameLog.info("%s createRoom args: %s" %(self.__class__.__name__, data))
        # check room_card
        err, createCost = self._checkRoomCard(data)
        if err != ErrorCode.ERR_OK:
            gameLog.error("create room no enough money")
            return GameErrorCode.ROOM_NO_ENOUGH_MONEY, None
        # 获取并设置6位的房间编号
        index = noRepeatNum.getCode()
        if not index:
            gameLog.error("cannot get no-repeatName")
            return ErrorCode.ERR_REPEAT_NAME, None
        data['index'] = index
        data["pwd"] = index
        data['createTime'] = int(time.time())
        data["createCost"] = createCost
        ## 写数据库
        ret, roomID = self._writeDB(data)
        if ret != ErrorCode.ERR_OK: 
            noRepeatNum.returnCode(index)
            gameLog.error("create room write DB error")
            return ret, None
        # 创建房间
        roomID = int(roomID)
        data['slave'] = self._slave
        data["manager"] = self
        data["roomID"] = roomID
        room = self._genRoom(data)
        #
        self._rooms[roomID] = room
        # 
        gameLog.info("%s createRoom %d success, index:%d" %(self.__class__.__name__, roomID, index))
        return ErrorCode.ERR_OK, {"roomid":roomID, "roomnum":index}  #(roomID, index)

    def _checkRoomCard(self, data):
        eachGive = data.get("eachGive", 0)
        createCost = GameCfg.createCost.get(data["roundNum"], None)
        needGive = createCost
        if needGive is None:
            return ErrorCode.ERR_FAIL, None
        if eachGive == 0:  # creatorGive
            needGive = needGive[4]       
            createCost = createCost[4]          
        else:       # eachGive
            needGive = needGive[4]
            createCost = createCost[4]
            if not data["roundNum"] in GameCfg.canEachGive:
                return ErrorCode.ERR_FAIL, None
            needGive = needGive / int(data["playerNum"])
        creatorID = data["creatorID"]
        err, data = gameDataInterface.getPlayerRoomCard(creatorID)
        if err != ErrorCode.ERR_OK or data < needGive:
            return ErrorCode.ERR_FAIL, None
        return ErrorCode.ERR_OK, createCost

    def roomClose(self, room, playerInfo):
        gameLog.info("room[%d] close, account is: %s" %(room.roomID, str(playerInfo)) )
        noRepeatNum.returnCode(room.index)
        self._rooms.pop(room.roomID, None)

    def checkHadInRoom(self, uid):
        for roomID in self._rooms:
            room = self._rooms[roomID]
            if room.isPlayerInRoom(uid):
                return room.index
        return -1


    def userLoginLogout(self, uid, status):
        for roomID in self._rooms:
            room = self._rooms[roomID]
            if room.isPlayerInRoom(uid):
                room.userLoginLogout(uid, status)
