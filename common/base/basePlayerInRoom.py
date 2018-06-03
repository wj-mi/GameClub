# coding:utf-8
from util.gameLog import gameLog


class BasePlayerInRoom(object):
    def __init__(self, roomIns):
        self._room = roomIns
        self._seatInfo = [None] * roomIns.maxPlayer
        self._allPlayer = {}        # 当前在房间内的所有玩家
        self._historyPlayer = {}    # 曾经经过这个房间的所有玩家

    def __del__(self):
        self._seatInfo = None
        self._room = None
        gameLog.info("release playerInRoom")

    def reInit(self):
        allPlayer = self.getPlayerInSeat()
        self._allPlayer = {}
        self._historyPlayer = {}
        for tmp in allPlayer:
            self.enterRoom(tmp)

    @property 
    def allPlayer(self):    return self._allPlayer

    @property 
    def seatInfo(self): return self._seatInfo

    @property 
    def historyPlayer(self):    return self._historyPlayer

    ###################### 外部接口 ######################

    def playerInRoom(self, uid):
        return True if uid in self._historyPlayer.keys() else False

    def getSeatStatusPlayer(self, status, same=True):
        """得到在坐的某种状态的玩家
        same == True表示和status状态相同的, same == False表示和status状态不同的
        """
        return [player for player in self._seatInfo if player and ((same and player.status == status) or (not same and player.status != status))]

    def findNoUseSeatNo(self):
        for seatNo, seat in enumerate(self._seatInfo):
            if seat is None:
                return seatNo
        return -1

    def getAllNoneSeatIndex(self):
        return [ index for index in range(len(self._seatInfo)) if self._seatInfo[index] is None ]

    def getPlayerByUID(self, uid):  return self._allPlayer.get(uid, None)
    def getHistoryPlayerByUID(self, uid):   return self._historyPlayer.get(uid, None)

    def getPlayerBySeatNo(self, seatNo):
        if seatNo >= 0 and seatNo < len(self._seatInfo):
            return self._seatInfo[seatNo]
        return None

    def enterRoom(self, player):
        self._allPlayer[player.uid] = player
        self._historyPlayer[player.uid] = player

    def sitdown(self, player, seatNo):
        if not (seatNo >= 0 and seatNo < len(self._seatInfo) or self._seatInfo[seatNo] != None):
            gameLog.debug("seatNo %d is not allow" %seatNo)
            return
        self._seatInfo[seatNo] = player

    def standup(self, player):
        pass 

    def leaveRoom(self, player):
        seatNo = player.seatNo
        if seatNo != -1:
            self._seatInfo[seatNo] = None
        self._allPlayer.pop(player.uid, None)
        self._historyPlayer.pop(player.uid, None)
        pass 

    def getPlayerInSeat(self):
        """得到已经坐下的座玩家信息
        """
        return [ player for player in self._seatInfo if player is not None ]

    def getPlayerInGame(self):
        return [ player for player in self._seatInfo if player and player.isGaming() ]

    def getSitPlayerSnapshot(self):
        """得到在坐的玩家的快照，用来恢复现场
        """
        players = self.getPlayerInSeat()
        snapshot = {}
        for player in players:
            snapshot[player.seatNo] = player.genSnapshot()
        return snapshot

    def clearRound(self):
        pass 
