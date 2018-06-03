# coding: utf-8

from BaseGameProtocol import *


class __NonamePackType(GamePackType):
	C2S_ENTER_ROOM = 0x341

GamePackType = __NonamePackType()