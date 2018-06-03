# coding: utf-8

from base.defaultCfg import DefaultCfg 


class GameCfg(DefaultCfg):
        gameName = "dagong"
        gameType = 1
        gameTagCfg = 0xF0
        gameProtocol = "DagongProtocol"

        updateRecordSP = "dagong_update_record"
        
        cfg_PlayerFightTime_MS = 5 * 1000       # 玩家硬牌的时间
        cfg_PlayerBetTime_MS = 10 * 1000        # 允许玩家出牌的时间
        playerCardNum = 27                                      # 每个玩家的初始手牌数
        #playerCardNum = 5                                      # 每个玩家的初始手牌数
        cfg_SendEachCardShowTime_MS = 2 * 1000  # 给每个玩家发牌的时间
        cfg_ShowPlayerBetTime_MS = 1 * 1000     # 展示玩家出牌的时间(包括不出)
        cfg_ShowAccountTime_MS = 3 * 1000       #  结算的时间

        isDebug = False
        codeBegin = 100000
        codeEnd = 200000

        createCost = { 4:{4:3}, 6:{4:4}, 8:{4:5}  }
        canEachGive = [6]

