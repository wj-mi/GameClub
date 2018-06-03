# coding:utf-8

from util.packUtils import genGamePackUtil
from SlaveBase  import SlaveBase, S2S, C2S
from gameCfg import GameCfg

from protocol import *



class GameSlave(SlaveBase):
    def __init__(self):
        super(GameSlave, self).__init__()
        self._tags = [ GameCfg.gameTagCfg ]
        super(GameSlave, self)._initialize()
        self.PackClass = genGamePackUtil(PackKey)
        self._gameTag = self._tags[0]

    @C2S(GameCfg.gameTagCfg, 66666)
    def heartBet(self, pack):
        return 0, 0