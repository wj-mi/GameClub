# coding: utf-8

from base.defaultCfg import DefaultCfg 


class GameCfg(DefaultCfg):
    gameName = "majiangWuhan"
    gameType = 2
    gameTagCfg = 0xF1
    gameProtocol = "MajiangWuhanProtocol"

    updateRecordSP = "majiang_wuhan_update_record"
    

    cfg_PlayerBetTime_MS = 15 * 1000        # 允许玩家出牌的时间
    cfg_PlayerActionTime_MS = 10 * 1000      # 
    playerCardNum = 13                      # 每个玩家的初始手牌数
    cfg_SendEachCardShowTime_MS = 2 * 1000  # 给每个玩家发牌的时间
    cfg_ShowPlayerBetTime_MS = 1 * 1000     # 展示玩家出牌的时间(包括不出)
    cfg_ShowAccountTime_MS = 3 * 1000       #  结算的时间

    isDebug = False 
    codeBegin = 200000
    codeEnd = 300000
    # 
    createCost = { 8:{2:2, 3:3, 4:3}, 12:{2:2, 3:3, 4:4}, 16:{2:4, 3:6, 4:6}, 5000:{2:4, 3:6, 4:6}  }


    canEachGive = [12]
