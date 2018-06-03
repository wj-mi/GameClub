# coding:utf-8

from base.baseGameSlave import *

class GameSlave(BaseGameSlave):
    def __init__(self):
        BaseGameSlave.__init__(self)

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_ONEFIGHTOTHERS)
    @findRoom
    def playerOneFightOthers(self, pack, **kwargs):
        uid, roomID, opt =  pack.Fetch("UID", "ROOMID", "BODY")
        room = kwargs["room"]
        err, data = room.playerOneFightOthers(uid, opt)
        self.gameLogC2S(uid, "playerOneFightOthers", roomID, err, data)
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_OPT)
    @findRoom
    def playerBet(self, pack, **kwargs):
        uid, roomID, info =  pack.Fetch("UID", "ROOMID", "BODY")
        room = kwargs["room"]
        err, data = room.playerBet(uid, info)
        self.gameLogC2S(uid, "playerBet", roomID, err, data)
        return err, data


    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_NEED_HINT)
    @findRoom
    def playerNeedHint(self, **kwargs):
        uid, roomID =  pack.Fetch("UID", "ROOMID")
        room = kwargs["room"]
        err, data = room.playerNeedHint(uid)
        self.gameLogC2S(uid, "playerNeedHint", roomID, err, data)
        return err, data