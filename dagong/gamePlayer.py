# coding: utf-8

"""打拱玩家类
"""
from base.basePlayer import *
from protocol import *
import copy

CARD_2_SCORE = { 2:5, 7:10, 10:10 }

class GamePlayer(BasePlayer):
    def __init__(self, uid):
        super(GamePlayer, self).__init__(uid)
        self._hadBetCards = []
        self._scoreCards = []
        self._xipai = 0   # 喜牌的次数
        self._curRoundXipaiWin = 0  # 洗牌的输赢
        self._baopai = 0  
        self._findFriend = 0
        self._tmpXipai = 0

    @property 
    def hadBetCards(self):  return self._hadBetCards

    @property 
    def scoreCards(self):   return self._scoreCards


    def getScore(self):
        total = 0
        for card in self._scoreCards:
            total += CARD_2_SCORE[card%13]
        return total

    @property 
    def curRoundXipaiWin(self): return self._curRoundXipaiWin

    def updateCurRoundXipaiWin(self, win):
        self._curRoundXipaiWin += win

    def addXipai(self):
        self._xipai += 1

    def addBaopai(self):
        self._baopai += 1

    def addFindFriend(self):
        self._findFriend += 1

    def addTmpXipai(self):
        self._tmpXipai += 0.5
        return self._tmpXipai

    def clearTmpXipai(self):    self._tmpXipai = 0

    def playerBetCards(self, cards):
        for card in cards:
            if  card in self._cards:
                self._cards.remove(card)
        self._hadBetCards.extend(cards)

    def playerAddScoreCards(self, cards):
        self._scoreCards.extend(cards)

    def initRound(self, round):
        super(GamePlayer, self).initRound(round)
        self.setStatus(PlayerStatus.STATUS_NORMAL)
        self._round       = round              
        self._cards       = []           
        self._hadBetCards = []       
        self._scoreCards = []
        self._curRoundXipaiWin = 0
        self._tmpXipai = 0

    def updateRoundChip(self, changeChip):  # !结算的使用，牌局中更新roundChip在updateChip 
        self._chip["roundChip"] += changeChip

    def isGaming(self):
        """玩家是否正在进行游戏
        """
        return True if (self._status == PlayerStatus.STATUS_NORMAL or self._status == PlayerStatus.STATUS_FOLD or self._status == PlayerStatus.STATUS_ALLIN) else False
    
    def isActive(self):
        """是否是活跃的
        """
        return True if self._status == PlayerStatus.STATUS_NORMAL else False

    def roomAccount(self):
        """计算整个房间的输赢
        """
        info = super(GamePlayer, self).roomAccount()
        info["xipai"] = self._xipai
        info["findFriend"] = self._findFriend
        info["baopai"] = self._baopai
        return info

    def _calServer(self, serverRate):
        pass


    def getRecoverData(self):
        data = super(GamePlayer, self).getRecoverData() #[ self.getCurHaveChip(), self.allBring, self.service ]  #{ "chip": self.getCurHaveChip(), "buyin": self.allBring, "server": }
        data.append(self._chip["insurPay"])
        data.append(self._chip["insurGive"])
        return data 

    def recoverData(self, data):
        super(GamePlayer, self).recoverData(data)
        self._chip["insurPay"] = data[3]
        self._chip["insurGive"] = data[4]


    def standup(self):
        """玩家站起
        """
        card = self._cards
        super(GamePlayer, self).standup()
        self._cards = card

    def getPlayingSnapshot(self):
        """
        得到在游戏中可以给其他玩家展示的数据
        """
        snapshot = {}
        snapshot["uid"] = self._uid
        #snapshot["card"] = self._cards
        snapshot["score"] = self._scoreCards
        return snapshot

    def getSelfPlayingInfo(self):
        """得到在游戏中[不]可以给其他玩家展示的数据
        """
        snapshot = {}
        snapshot["card"] = self._cards
        return snapshot
