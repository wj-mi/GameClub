# coding:utf-8

from base.baseGameSlave import *

class GameSlave(BaseGameSlave):
    def __init__(self):
        BaseGameSlave.__init__(self)


    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_OPT)
    @findRoom
    def playerBet(self, pack, **kwargs):
        uid, roomID, info =  pack.Fetch("UID", "ROOMID", "BODY")
        room = kwargs["room"]
        err, data = room.playerBet(uid, info)
        self.gameLogC2S(uid, "playerBet", roomID, err, data)
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_CHOOSE_ACT)
    @findRoom
    def playerChooseAct(self, pack, **kwargs):
        uid, roomID, info = pack.Fetch("UID", "ROOMID", "BODY")
        room = kwargs["room"]
        err, data = room.playerChooseAct(uid, info)
        self.gameLogC2S(uid, "playerChooseAct", roomID, err, data)
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_FORCE_START)
    @findRoom
    def playerForceStart(self, pack, **kwargs):
        uid, roomID, info = pack.Fetch("UID", "ROOMID", "BODY")
        room = kwargs["room"]
        num, choose = info.get("num", 0), info["choose"]
        err, data = room.playerForceStart(uid, num, choose)
        self.gameLogC2S(uid, "playerForceStart", roomID, err, data)
        return err, data