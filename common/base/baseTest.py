# coding: utf-8

"""测试模块
"""

import Singleton
from gameManager import GameManager
from util.roomCollection import roomCollection



###########################333
# test
# 
import copy
class BaseTest(object):
        def __init__(self):
                self._testUID = [ 9001,9002,9003 ]
                # 
                self._gameManager = GameManager.getInstance()
                self._gameManager.createRoom(self._getCreateArgs()) 
                self._roomID = self._gameManager._rooms.keys()[0]
                self._gameItem = self._gameManager._rooms[self._roomID]
                self._room = roomCollection.getRoom(self._roomID)

        @property 
        def testUID(self):
                return copy.copy(self._testUID) 

        def getManager(self):
                return self._gameManager

        def getItem(self):
                return self._gameItem

        def _getCreateArgs(self):
                pass 

        def _getTestUIDs(self, uid):
                ids = []
                if uid == -1:
                        ids = self._testUID
                elif type(uid) == type(1):
                        ids = [uid]
                elif type(uid) == type([]):
                        ids = uid
                return ids 

        def testEnterRoom(self):
                for uid in self._testUID:
                        self._room.c2s_enterRoom(uid, None, None)

        def testReady(self):
                for uid in self._testUID:
                        self._room.playerReady(uid)

        def testStartRoom(self):
                self._room.startRoom(117)

        def testClickSeat(self, uid=-1):
                ids = self._getTestUIDs(uid)
                for index, uid in enumerate(ids):
                        self._room.clickSeat(uid, index)

        def testBuyIn(self, uid=-1):
                ids = self._getTestUIDs(uid)
                for index, uid in enumerate(ids):
                        self._room.buyin(uid, 200, "123456")

        def testDissolve(self):
                self._gameManager.dissolveItem([self._roomID])