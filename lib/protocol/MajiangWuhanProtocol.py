# coding: utf-8
from BaseGameProtocol import *

"""Majiang的协议
"""
##
class MajiangWuhanPackType(GamePackType):
    ## S2S
    __S2S_BASE = GamePackType._GAME_S2S_BASE
    ## C2S
    __C2S_BASE = GamePackType._GAME_C2S_BASE  # 1756
    C2S_ACTION = __C2S_BASE + 1
    C2S_CHOOSE_ACT = __C2S_BASE + 100
    C2S_GET_ALL_RECORD = __C2S_BASE + 101
    C2S_FORCE_START = __C2S_BASE + 102

    ## S2C
    __S2C_BASE = GamePackType._GAME_S2C_BASE + 1000  # 3756
    S2C_CAN_CHOOSE_ACT = __S2C_BASE + 1
    S2C_CHOOSE_ACT = __S2C_BASE + 2
    S2C_ROUND_ACCOUNT  = __S2C_BASE + 5   # 3761
    S2C_HAD_PLAYER_CHOOSE_ACTION = __S2C_BASE + 6
    S2C_PLAYER_SITDOWN = __S2C_BASE + 7   # 3763
    S2C_LEAVE_ROOM = __S2C_BASE + 8   # 3764
    S2C_CLOSEROOM = __S2C_BASE + 9 
    S2C_START_LESS_GAME = __S2C_BASE + 10
    S2C_CHOOSE_FORCE_START = __S2C_BASE + 11
    S2C_HIDE_FORCE_START = __S2C_BASE + 12


GamePackType = MajiangWuhanPackType()


##
class MajiangWuhanPackKey(GamePackKey):
    pass 

GamePackKey = MajiangWuhanPackKey()

##
class MajiangWuhanClickReturnCode(GameClickReturnCode):
    TYPE_BET = 11
    pass 

GameClickReturnCode = MajiangWuhanClickReturnCode()


##
class MajiangWuhanErrorCode(GameErrorCode):
    pass 
GameErrorCode = MajiangWuhanErrorCode()

## 
class GameRoomStatus(GameRoomStatus):
    pass 
GameRoomStatus = GameRoomStatus()


class PlayerStatus(PlayerStatus):
    __STATUS_BASE = PlayerStatus.__STATUS_OTHER_BASE
    STATUS_NORMAL = __STATUS_BASE + 1
    STATUS_FINISH = __STATUS_BASE + 2
PlayerStatus = PlayerStatus()






class actionType:
    """集中在加注条上的操作
    """
    ACT_GIVEUP = 0
    ACT_BET = 1
ActType = actionType()
