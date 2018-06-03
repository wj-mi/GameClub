# coding: utf-8

"""武汉麻将玩家类
"""
from base.basePlayer import *
from protocol import *
import copy



class GamePlayer(BasePlayer):
    def __init__(self, uid):
        super(GamePlayer, self).__init__(uid)
        self._hadBetCard = []
        self._pengCard = []
        self._gangCard = []
        self._chiCard = []
        self._gangCardInfo = []
        #
        self._mingangCount = 0  
        self._angangCount = 0
        self._dianpaoCount = 0
        self._zimoCount = 0
        self._huCount = 0
        self._allScore = 0
 
    @property 
    def pengCard(self): return self._pengCard

    @property 
    def gangCard(self): return self._gangCard

    @property 
    def chiCard(self): return self._chiCard    

    @property 
    def justPengCard(self): return [ item[3] for item in self._pengCard ]

    @property 
    def justGangCard(self): return [ item[3] for item in self._gangCard ] 

    @property 
    def justChiCard(self): return [ [item[4], item[5],item[6] ] for item in self._chiCard ] 


    @property 
    def hadBetCard(self):   return self._hadBetCard

    @property 
    def gangCardInfo(self): return self._gangCardInfo
    def addGangCardInfo(self, info):    
        if info[2] == 3 or info[2] == 12:   #  3明杠 4放炮胡 6过,12边杠，13暗杠 14自摸
            self._mingangCount += 1
        else:
            self._angangCount += 1
        return self._gangCardInfo.append(info)
        
    def addDianPaoCount(self):
        self._dianpaoCount += 1

    def addZimoCount(self):
        self._zimoCount += 1

    def addHuCount(self):
        self._huCount += 1

    def getOneCard(self, card):
        self._cards.append(card)

    def playerBetCard(self, card, addToTable=False):
        if card in self._cards:
            self._cards.remove(card)
            if addToTable:
                self._hadBetCard.append(card)

    def removeHadBetCard(self, card):
        if card in self._hadBetCard:
            self._hadBetCard.remove(card)

    def addPengCard(self, card):
        self._pengCard.append(card)

    def addGangCard(self, card):
        self._gangCard.append(card)

    def addChiCard(self, card):
        self._chiCard.append(card)

    def changePengToGang(self, card):
        index = None
        for item in self._pengCard:
            if card == item[3]:
                print "------------- changePengtogang   ", index
                index = item
                break    
        if index != None:
            self._pengCard.remove(index)
            self.addGangCard(index) #.append(card)
            self.addGangCardInfo(index)
            print "------------------  changePengtogang ", self._pengCard, "    ", self._gangCard


    def changeGangToPeng(self, card):
        index = None
        for item in self._gangCard:
            if card == item[3]:
                index = item
                break    
        if index != None:
            self._gangCard.remove(index)
            self._gangCardInfo.remove(index)
            self._pengCard.append(index)
        # if card in self._gangCard:
        #     self._gangCard.remove(card)
        #     self._gangCardInfo = [ info for info in self._gangCardInfo if info[1] != card]
        #     self._pengCard.append(card)

    def initRound(self, round):
        super(GamePlayer, self).initRound(round)
        self.setStatus(PlayerStatus.STATUS_NORMAL)
        self._hadBetCard = []
        self._pengCard = []
        self._gangCard = []
        self._chiCard = []
        self._gangCardInfo = []

    def roomAccount(self):
        """计算整个房间的输赢
        """
        info = super(GamePlayer, self).roomAccount()
        info["mingangcount"] = self._mingangCount
        info["angangcount"] = self._angangCount
        info["dianpaocount"] = self._dianpaoCount
        info["zimocount"] = self._zimoCount
        info["hucount"] = self._huCount
        return info