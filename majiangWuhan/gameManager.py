# coding:utf-8

"""打拱的管理
"""
import Singleton
from base.baseManager import *
from protocol import *
from gameCfg import GameCfg
from gameDataInterface import *
import time



class GameManagerNoSingleton(BaseManager):
    def __init__(self):
        BaseManager.__init__(self)

    ################## 内部接口 ###################

    def _writeDB(self, data):
        #if GameCfg.isDebug:
        #    return 0, 0
        # 
        err, roomID = createMajiangWuhan(
            data["creatorID"],
            int(time.time()),
            data["index"],
            data["playerNum"],
            data["roundNum"],
            data["locationLimit"],
            

        )
        return err, roomID

    ################## 外部接口 #################

    def signUp(self, itemID, uid, args):
        """玩家报名

        牛牛游戏不需要玩家进行报名
        """
        pass


class GameManager(GameManagerNoSingleton, Singleton.Singleton):
    @staticmethod
    def getInstance():  return Singleton.getInstance(GameManager)