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

    @basePack(GamePackType.S2C_PLAYER_CHOOSE_FIGHT) 
    def sendPlayerChooseFight(self, uid, time, **kwargs):
        """发送让某个玩家对是否硬牌进行选择
        """
        pack = kwargs["pack"]
        pack.BODY = [uid, time]
        self._gameLogPack("sendPlayerChooseFight", pack)
        self._sendToRoom(pack)

    @basePack(GamePackType.S2C_PLAYER_FIGHT)
    def sendPlayerFight(self, uid, choose, **kwargs):
        """发送让某个玩家对是否硬牌做出的选择
        """
        pack = kwargs["pack"]
        pack.BODY = {"uid":uid, "choose":choose}
        self._gameLogPack("senPlayerFight", pack)
        self._sendToRoom(pack)

    @basePack(GamePackType.S2C_SEND_PUBLICCARD)
    def sendPublicCard(self, card, **kwargs):
        """发送选中的公共牌
        """
        pack = kwargs["pack"]
        pack.BODY = card
        self._gameLogPack("sendPublicCard", pack)
        self._sendToRoom(pack)
        
    @basePack(GamePackType.S2C_SEND_NEW_BET)
    def sendNewBet(self, uid, time, **kwargs):
        """发送新的玩家正在出牌
        """
        pack = kwargs["pack"]
        pack.BODY = {"uid":uid, "time":time}
        self._gameLogPack("sendNewBet", pack)
        self._sendToRoom(pack)

    @basePack(GamePackType.S2C_SEND_PLAYER_BET)
    def sendPlayerBet(self, info, **kwargs):
        """玩家对出牌做了选择
        """
        pack = kwargs["pack"]
        pack.BODY = info
        self._gameLogPack("sendPlayerBet", pack)
        self._sendToRoom(pack)

    @basePack(GamePackType.S2C_SEND_SHOW_RELATION)
    def sendShowRelation(self, uid, **kwargs):
        """因出牌而确定的关系
        """
        pack = kwargs["pack"]
        pack.BODY = uid
        self._gameLogPack("sendShowRelation", pack)
        self._sendToRoom(pack)

    @basePack(GamePackType.S2C_BET_END_ACCOUNT)
    def sendBetEndAccount(self, uid, cards, score, **kwargs):
        """发送一轮出牌结束统计信息
        """
        pack = kwargs["pack"]
        pack.BODY = {"uid":uid, "cards":cards, "score":score}
        self._gameLogPack("sendBetEndAccount", pack)
        self._sendToRoom(pack)

    @basePack(GamePackType.S2C_SEND_SELF_FRIEND_CARDS)
    def sendSelfFrientCards(self, player, friend, friendCards, **kwargs):
        """发送队友的牌
        """
        pack = kwargs["pack"]
        pack.BODY = {"frindUID": friend.uid, "cards": friendCards}
        self._gameLogPack("sendSelfFriendCards", pack)
        self.sendToClient(player.sid, pack)