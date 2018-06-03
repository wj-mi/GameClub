#coding:utf-8

from gameCfg import GameCfg
from base.baseTest import *

class GameTest(BaseTest):
	def __init__(self):
		super(GameTest, self).__init__()

	def _getCreateArgs(self):
		return   {
			"roomType": 1,
			"creatorID": 9001,
			"roundNum": 4,
			"playerNum": 4,
			"locationLimit":0,
			"eachGive":0
		}



if GameCfg.isDebug:
	testIns = GameTest()
	testIns.testEnterRoom()
	#testIns.testInterRoom()
	#testIns.testReady()
	#users = testIns.testUID
	#testIns.testClickSeat(users)
	#testIns.testBuyIn(users)
	#testIns.testStartRoom()



