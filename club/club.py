# -*- coding:utf-8 -*-

import time
import gameDataInterface

from utils.generate_uuid import compress_uuid

from utils.gameError import GameException, new_cur


class GameClub(object):
    def __init__(self, args):
        """俱乐部对象
        """
        self._clubID = args["id"]
        self._name = args["name"]
        self._index = args["index"]   # 八位的俱乐部标识
        self._gameType = args["gameType"] # 可以开始的游戏类型
        # self._roomCard = args["roomCard"]  # 房卡，可能后台改变，暂时不维护
        # 
        self._createRoomArgs = args["createRoomArgs"]  # 创建房间的参数
        #
        self._handleInitClub()

    def _handleInitClub(self):
        """初始化俱乐部
        拉取俱乐部的成员
        创建3个新的房间(如果原来的)
        """
        pass 

    def applyEnterClub(self, uid):
        """玩家申请加入俱乐部
        """
        pass 

    def managerClubMember(self, uid, targetUID, opr):
        """
        """
        pass

    def getClubTable(self):
        """
        """
        pass

    def changeCreateSet(self, uid, info):
        """
        """
        pass

    def getRoomCardRecord(self, recordType):
        """
        """
        pass