# coding: utf-8

from BaseGameProtocol import *


class __AccountPackType(GamePackType):
    ## S2S
    __S2S_BASE = GamePackType._GAME_S2S_BASE

    ## C2S
    __C2S_BASE = GamePackType._GAME_C2S_BASE  # 1756
    C2S_GET_USER_INFO = __C2S_BASE + 1
    C2S_GET_USER_INFO_DETAIL = __C2S_BASE + 2 
    C2S_GET_TOP_PLAYER = __C2S_BASE + 3
    C2S_PLAY_TODAY = __C2S_BASE + 4
    C2S_GET_SIGNUP_INFO = __C2S_BASE + 5
    C2S_GET_ROUND_ACCOUNT = __C2S_BASE + 6
    C2S_GET_ROUND_HISTORY = __C2S_BASE + 7
    C2S_UPDATE_GPS = __C2S_BASE + 8
    C2S_SHARE_APP = __C2S_BASE + 9
    C2S_GET_HALL_NOTIC = __C2S_BASE + 10
    C2S_SAVE_ORDER = __C2S_BASE + 11
    ## S2C
    __S2C_BASE = GamePackType._GAME_S2C_BASE  # 2756
    

GamePackType = __AccountPackType()
