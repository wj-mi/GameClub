
from base.basePlayerInRoom import * 
from gamePlayer import *

class GamePlayerInRoom(BasePlayerInRoom):
    def __init__(self, args):
        super(GamePlayerInRoom, self).__init__(args)


    def standup(self, player):
        seatNo, uid = player.seatNo, player.uid
        if seatNo < 0:
            return
        self._seatInfo[seatNo] = None