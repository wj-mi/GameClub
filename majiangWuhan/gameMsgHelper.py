# coding: utf-8
from base.baseMsgHelper import BaseMsgHelper, basePack
from SessionID import SessionID
from protocol import *
from util.gameLog import gameLog


class GameMsgHelper(BaseMsgHelper):
    def __init__(self, slave, room):
        BaseMsgHelper.__init__(self, slave, room)

    @basePack(GamePackType.S2C_START_ROUND) 
    def sendStartRound(self, player, info, **kwargs):
        pack = kwargs['pack']
        pack.BODY = info 
        self._gameLogPack("startRound", pack)
        #sendToClient(self, sid, pack)
        self.sendToClient(player.sid, pack)

    @basePack(GamePackType.S2C_SEND_NEW_BET)
    def sendNewBet(self, player, uid, time, getCard, card, rest,**kwargs):
        """发送新的玩家正在出牌
        """
        pack = kwargs["pack"]
        pack.BODY = {"uid":uid, "time":time, "getCard":getCard, "card":card, "rest":rest}
        #self._gameLogPack("sendNewBet", pack)
        self.sendToClient(player.sid, pack)

    @basePack(GamePackType.S2C_SEND_PLAYER_BET)
    def sendPlayerBet(self, info, **kwargs):
        """玩家对出牌做了选择
        """
        pack = kwargs["pack"]
        pack.BODY = info
        self._gameLogPack("sendPlayerBet", pack)
        self._sendToRoom(pack)

    @basePack(GamePackType.S2C_CAN_CHOOSE_ACT)
    def sendPlayerCanChoose(self, player, info, time,**kwargs):
        pack = kwargs["pack"]
        info["time"] = time
        pack.BODY = {"info": info}
        self._gameLogPack("sendPlayerCanChoose", pack)
        self.sendToClient(player.sid, pack)

    @basePack(GamePackType.S2C_CHOOSE_ACT)
    def _sendPlayerChooseAct(self, info, **kwargs):
        pack = kwargs["pack"]
        pack.BODY = info
        self._gameLogPack("sendPlayerChooseAct", pack)
        self._sendToRoom(pack)

    @basePack(GamePackType.S2C_HAD_PLAYER_CHOOSE_ACTION)
    def sendHadPlayerChooseAction(self, time, **kwargs):
        pack = kwargs["pack"]
        pack.BODY = {"time":time}
        self._gameLogPack("sendHadPlayerChooseAction", pack)
        self._sendToRoom(pack)

    @basePack(GamePackType.S2C_START_LESS_GAME)
    def sendStartLessPlayerGame(self, owner, readyNum, **kwargs):
        pack = kwargs["pack"]
        pack.BODY = readyNum
        self._gameLogPack("sendStartLessPlayerGame", pack)
        self._sendToRoom(pack)

    @basePack(GamePackType.S2C_CHOOSE_FORCE_START)
    def sendPlayerForceStart(self, info, **kwargs):
        pack = kwargs["pack"]
        pack.BODY = info
        self._gameLogPack("sendPlayerForceStart", pack)
        self._sendToRoom(pack)


    @basePack(PackType.PT_RESULT)
    def sendChangeSeatno(self, player, data, **kwargs):
        pack = kwargs["pack"]
        pack.BODY = data
        pack.ERROR = 0
        pack.REQUEST = GamePackType.C2S_ENTER_ROOM
        self._gameLogPack("sendChangeSeatno", pack)
        self.sendToClient(player.sid, pack)

    @basePack(GamePackType.S2C_HIDE_FORCE_START)
    def sendHideForceStart(self, **kwargs):
        pack = kwargs["pack"]
        pack.BODY = {}
        self._gameLogPack("sendHideForceStart", pack)
        self._sendToRoom(pack)

    @basePack(11111)
    def sendTestMsg(self, actionInfo, **kwargs):
        pack = kwargs["pack"]
        info = {}
        for player in actionInfo:
            info[player.uid] = actionInfo[player]
        pack.BODY = {"info": info}
        self._gameLogPack("sendTestMsg", pack)
        gameLog.error("sendTestMsg  %s" %(str(info),))
        self._sendToRoom(pack)
