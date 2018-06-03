# coding:utf-8

"""玩家基类

进入某个游戏的某个房间,就会实例化一个玩家对象
数据更新策略：
    生成玩家对象的时候会获取一次玩家昵称。
    用户主动点击玩家头像的时候，会强制更新一次
    每局结束的时候，生成的上局回顾的时候会使用旧的数据
"""
from util.dataInterface import getUserInfo
from protocol import *
import copy
import math


class BasePlayer(object):
    STATUS_NO_ROOM     = -1 # 玩家没有进入房间
    STATUS_WAIT_READY  = 0  # 玩家坐下但未准备
    STATUS_READY       = 1  # 
    STATUS_OTHER_BASE  = 10 # 各个不同的游戏玩家状态请从STATUS_OTHER_BASE向上加
    def __init__(self, uid):
        self._uid = uid
        self._sid = None
        self._seatNo = -1
        self._status = -1
        self._cards = []
        self._timer = None
        self._roomID = -1
        self._chip = 0    # winChip in room
        self._allChip = 0 # allChip in game
        self._avatar = ""
        self._nickname = ""
        self._gender = 0
        self._isOnline = 0   # 0 online 1 out
        self._getUserInfoFromDB()

    def _getUserInfoFromDB(self):
        err, data = getUserInfo(self._uid)
        if err == ErrorCode.ERR_OK:
            self._avatar = data["avatar"]
            self._nickname = data["nickname"]
            self._gender = int(data["gender"])

    def reInit(self):
        self._chip = 0
        self._allChip = 0

    @property 
    def uid(self):  return self._uid

    @property 
    def isOnline(self): return self._isOnline
    def setOnline(self, online): self._isOnline = online

    @property
    def sid(self):  return self._sid
    def setSid(self, sid):  self._sid = sid
    def clearSid(self): self._sid = None

    @property 
    def nickname(self): return self._nickname
    def setNickname(self, nickname):    self._nickname = nickname

    @property 
    def isSit(self): return self._seatNo != -1

    @property 
    def timer(self):    return self._timer
    def setTimer(self, timer):  self._timer = timer

    @property 
    def seatNo(self):   return self._seatNo
    def setSeatNo(self, seatNo):    self._seatNo = seatNo

    @property 
    def status(self):   return self._status 
    def setStatus(self, status):    
        self._status = status

    @property 
    def avatar(self): return self._avatar

    @property 
    def cards(self):    return self._cards
    def addCards(self, cards):  self._cards = cards
    def clearCards(self):   self._cards = []

    @property 
    def roomID(self): return self._roomID
    def setRoomID(self, roomID): self._roomID = roomID

    @property 
    def chip(self): return self._chip

    def updateChip(self, chip):
        self._allChip += chip
        self._chip += chip

    def enterRoom(self, roomID):
        """玩家进入房间
        """
        self.setRoomID(roomID) #  _roomID = roomID
        #self._chip = 0
        self._allChip = 0

    def standup(self):
        """玩家站起
        """
        pass

    def initRound(self, round):
        pass 

    def roomAccount(self):
        """计算整个房间的输赢
        """
        return {"chip":self._chip, "allChip": self._allChip, "avatar":self._avatar, "uid":self._uid, "nickname": self._nickname}

    def sitdown(self, seatNo, status):
        self.setSeatNo(seatNo)
        self.setStatus(status)

    def isGaming(self):
        """玩家是否正在进行游戏
        """
        pass 

    def clearRound(self):
        """清空玩家的上把游戏数据
        """
        self.clearCards()
        self.setStatus(PlayerStatus.STATUS_WAIT_READY)
 
    def getBaseSnapshot(self):
        snapshot = {}
        snapshot['uid'] = self._uid
        snapshot['nickname'] = self._nickname
        snapshot['chip'] = self._chip
        snapshot["allChip"] = self._allChip
        snapshot["seatnum"] = self._seatNo
        snapshot["avatar"] = self._avatar
        snapshot["gender"] = self._gender
        snapshot["status"] = self._status
        return snapshot

    def getPlayingSnapshot(self):
        return {}
