# coding: utf-8
from BaseGameProtocol import *

"""打拱的协议
"""
##
class DagongPackType(GamePackType):
    ## S2S
    __S2S_BASE = GamePackType._GAME_S2S_BASE
    S2S_CREATE_ITEM = 0x128
    S2S_ENTER_ITEM = 0x140     
    S2S_GET_TABLE_PLAYER_NUM = 0x290
    S2S_GAME_ACCOUNT = 0x157
    S2S_JOIN_CHANGE = 0x313
    ## C2S
    __C2S_BASE = GamePackType._GAME_C2S_BASE  # 1756
    C2S_ACTION = __C2S_BASE + 1
    # C2S_BUY_INSURTIME = __C2S_BASE + 6
    _OTHER_TEXAS_C2S_BASE = __C2S_BASE + 100
    ## S2C
    __S2C_BASE = GamePackType._GAME_S2C_BASE  # 2756
    S2C_SEND_SHOW_RELATION = __S2C_BASE + 1
    S2C_SEND_SELF_FRIEND_CARDS = __S2C_BASE + 2
    # S2C_BUY_INSURTIME = __S2C_BASE + 12
    _OTHER_TEXAS_S2C_BASE = __S2C_BASE + 100

GamePackType = DagongPackType()


##
class DagongPackKey(GamePackKey):
    pass 

GamePackKey = DagongPackKey()

##
class DagongClickReturnCode(GameClickReturnCode):
    TYPE_BET = 11
    pass 

GameClickReturnCode = DagongClickReturnCode()


##
class DagongErrorCode(GameErrorCode):
    pass 
GameErrorCode = DagongErrorCode()

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