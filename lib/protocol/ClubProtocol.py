# coding: utf-8

from BaseGameProtocol import *


class __ClubPackType(GamePackType):
    ## S2S
    __S2S_BASE = GamePackType._GAME_S2S_BASE

    ## C2S
    __C2S_BASE = GamePackType._GAME_C2S_BASE + 1000  # 1756
    C2S_SEARCH_CLUB = __C2S_BASE + 1
    C2S_APPLY_ENTER_CLUB = __C2S_BASE + 2
    C2S_MANAGER_CLUB_MEMBER = __C2S_BASE + 3
    C2S_GET_CLUB_TABLE = __C2S_BASE + 4
    C2S_CHANGE_CREATE_SET = __C2S_BASE + 5
    C2S_GET_ROOM_CARD_RECORD = __C2S_BASE + 6
    ## S2C
    __S2C_BASE = GamePackType._GAME_S2C_BASE  # 2756
    

GamePackType = __AccountPackType()
