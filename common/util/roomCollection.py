# coding: utf-8
"""房间集合

保留房间的引用,方便迅速的找到房间。玩家在房间内的操作，都要首先检查玩家是否在房间内
"""
import Singleton


class RoomCollection(Singleton.Singleton):
    def __init__(self):
        self._rooms = {}

    @staticmethod
    def getInstance():  return Singleton.getInstance(RoomCollection)

    def addRoom(self, roomID, room):
        self._rooms[roomID] = room 

    def delRoom(self, roomID):
        self._rooms.pop(roomID, None)

    def getRoom(self, roomID):
        return self._rooms.get(roomID, None)

roomCollection = RoomCollection.getInstance()