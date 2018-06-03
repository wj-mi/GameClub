# coding:utf-8

from util.packUtils import genGamePackUtil
from util.gameLog import gameLog
from SlaveBase  import SlaveBase, S2S, C2S
from gameCfg import GameCfg
from protocol import *
from clubManager import ClubManager


def findClub(func):
    def _findClub(self, pack, **kwargs):
        clubID = pack.Fetch("CID")
        club = self._clubManager.getClubObj(clubID)
        if club is None:
            gameLog.info("not find club [%d] in collection" %int(clubID))
            return ErrorCode.ERR_FAIL, -1 
        else: 
            kwargs["club"] = club
            return func(self, pack, **kwargs)
    return _findClub

class GameSlave(SlaveBase):
    def __init__(self):
        super(GameSlave, self).__init__()
        self._tags = [ GameCfg.gameTagCfg, TagType.TAG_STATUS ]
        super(GameSlave, self)._initialize()
        self.PackClass = genGamePackUtil(PackKey)
        self._gameTag = self._tags[0]
        self._clubManager = ClubManager.getInstance()
        self._clubManager.setSlave(self)

    def sendToServer(self, tagType, packType, data, module):
        return self.SetSlaveMsg(packType, tagType, data, module)

    #########################

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_SEARCH_CLUB)
    def searchClub(self, pack):
        """根据俱乐部ID搜索俱乐部
        会得到简单的俱乐部的信息
        """
        index = pack.BODY
        club = self._clubManager.getClubByIndex(index)
        if club is None:
            return ErrorCode.ERR_FAIL, {}
        err, data = club.getClubInfoSimple()
        gameLog.info("player get club info ret is %d %s" %(err, str(data)))
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_APPLY_ENTER_CLUB)
    @findClub                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               USER_INFO_DETAIL)
    def applyEnterClub(self, pack, **kwargs):
        """玩家申请加入俱乐部
        要求:所有有效的申请，必须计入数据库
        """
        club = kwargs["club"]
        uid = pack.Fetch("UID")
        err, data = club.applyEnterClub(uid)
        gameLog.info("user %d applyEnterClub, ret is %d %s" %(uid, err, str(data)))
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_MANAGER_CLUB_MEMBER)
    @findClub
    def managerClubMember(self, pack, **kwargs):
        """管理俱乐部成员
        # 升/降级， 同意/拒绝申请， 踢人
        """
        club = kwargs["club"]
        info = pack.BODY
        oprUID, targetUID, opr = pack.UID, info["targetUID"], info["opr"]
        err, data = club.managerClubMember(uid, targetUID, opr)
        gameLog.info("player %d managerClubMember %s ret is %d %s" %(oprUID, str(info), err, str(data)))
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_CLUB_TABLE)
    @findClub
    def getClubTable(self, pack, **kwargs):
        club = kwargs["club"]
        err, data = club.getClubTable()
        gameLog.info("[%d] getClubTable ret is %d %s" %(club.clubID, err, str(data)))
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_CHANGE_CREATE_SET)
    @findClub
    def changeCreateSet(self, pack, **kwargs):
        club = kwargs["club"]
        uid, info = pack.UID, pack.BODY
        err, data = club.changeCreateSet(uid, info)
        gameLog.info("[%d] change club [%d] create set %s , ret is %d %s" %(uid, club.clubID, str(info), err, str(data)))
        return err, data

    @C2S(GameCfg.gameTagCfg, GamePackType.C2S_GET_ROOM_CARD_RECORD)
    @findClub
    def getRoomCardRecord(self, pack, **kwargs):
        club = kwargs["club"]
        recordType = pack.BODY
        err, data = club.getRoomCardRecord(recordType)
        gameLog.info("get club [%d] roomCardRecord [%d] ret is %d %s" %(club.clubID, recordType, err, str(data)))
        return err, data

