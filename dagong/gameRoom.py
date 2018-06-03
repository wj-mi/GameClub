# coding:utf-8

from base.baseRoom import *
from util import gameLog
from util.parseCSV import csv2tuple
from gamePlayer import *
from cardHelper import *
import gameDataInterface 
from gameMsgHelper import GameMsgHelper
from protocol import *
import time
import random
import math
import stackless
import simplejson as json


CARD_2_SCORE = { 2:5, 7:10, 10:10 }

class GameRoom(BaseRoom):
    def __init__(self, args):
        BaseRoom.__init__(self, args)
        self._maxSeat       = args["playerNum"]
        self._playerThinkTime   = GameCfg.cfg_PlayerBetTime_MS         
        self._fightPlayerTime   = GameCfg.cfg_PlayerFightTime_MS
        self._timer     = None     # timer
        self._fightPlayer   = None
        self._bankerSeat = -1
        self._banker = None
        self._curPlayer  = -1      # -1 未初始化 None没有玩家, Player玩家
        self._publicCard = -1      # 没人硬牌的话，从庄家牌中选一个不是对的牌,有人硬牌的话，该字段无效
        self._otherPublicCard = -1 # 公共牌的另外一张
        self._hadShowFriend = False         # 是否已经亮明了身份
        self._betEnd = False
        self._curCardType = None
        self._curCardTypePlayer = None 
        self._recordHistory = {}   # 用于做牌局回放
        self._recordProcess = []
        self._curBetscoreCards = []   # 本轮出牌的过程中是分数的牌
        self._rankPlayers = []        # 玩家等级排名
        self._rate = 1                # 翻的倍数
        self._winner = []
        self._roundAccountInfo = None
        #self._roundBegin = None
        self._lastRoundBegin = None 
        self._relationMap = {}        # 每个人朋友和敌人的映射，在硬牌环节结束后就会确定
                                      # !!!! 只有在没人硬牌的时候有效

        #### 
        self._testUID = [ ]
        for uid in self._testUID:
            self.c2s_enterRoom(uid, None, None)


    def _startRound(self):
        # sleep 1s
        #self._waitTime(1000)
        #
        super(GameRoom, self)._startRound()
        # initPlayer
        self._initPlayer()
        # fixed banker
        self._fixedBanker()
        # sendCards
        self._sendCards()
        # sendmsg
        baseInfo = { "banker":self._bankerSeat, "curRound": self._round }
        recordPlayerInfo = {}
        for player in self._curRoundPlayer:
            baseInfo["cards"] = player.cards
            tmpInfo = {"status": player.status, "isOnline":player.isOnline, "seatnum":player.seatNo, "allChip": player.chip, "uid":player.uid, "gender":0, "chip":player.chip, "avatar":player.avatar, \
                       "nickname": player.nickname , "card":player.cards[:]}
            tmpInfo["banker"] = 1 if player.uid == self._creatorID else 0
            tmpInfo["zhuang"] = 1 if (self._banker and player.uid == self._banker.uid) else 0
            recordPlayerInfo[player.uid] = tmpInfo
            self._msgHelper.sendStartRound(player, baseInfo)
        # chooseFight
        for i in range(len(self._curRoundPlayer)):
            self._curPlayer = self._playerInRoom.getPlayerBySeatNo((self._bankerSeat+i)%len(self._curRoundPlayer))
            self._status = GameRoomStatus.STATUS_FIGHT
            self._msgHelper.sendPlayerChooseFight(self._curPlayer.uid, self._fightPlayerTime)
            self._timer = self._timerManager.addTimer(self._fightPlayerTime, self, "_playerGiveupFightTimeout", (self._curPlayer,))
            receive = self._channel.receive()
            if receive == True:
                break
        self._status = GameRoomStatus.STATUS_PLAYING
        # 如果没有人硬牌，则选择庄家的一张牌作为公共牌
        if self._fightPlayer is None:
            self._publicCard, self._otherPublicCard = self._choosePublicCard()
            self._msgHelper.sendPublicCard(self._publicCard)
        recordStartInfo = { "banker":self._bankerSeat, "roomnum": self._pwd, "curRound": self._round, "roomID": self._roomID, \
                    "status": self._status, "allRound": self._roomMaxRound, "fightPlayer": -1 if self._fightPlayer is None else self._fightPlayer.uid, \
                    "betInfo": {}, "payType": self._eachGive, "publicCard": self._publicCard }
        recordStartInfo["playerInfo"] = recordPlayerInfo
        self._recordHistory["roomInfo"] = recordStartInfo
        # 确定关系
        self._fixRelation()
        for player in self._curRoundPlayer:
            recordPlayerInfo[player.uid]["friendInfo"] = self._genFriendInfo(player)
            recordPlayerInfo[player.uid]["you"] = 0 if player not in self._rankPlayers else (self._rankPlayers.index(player) + 1)
            recordPlayerInfo[player.uid]["paiCount"] = len(player.cards)
            recordPlayerInfo[player.uid]["mingji"] = 1 if (self._hadShowFriend and player == self._findFriend(self._banker)) else 0
            recordPlayerInfo[player.uid]["yingpai"] = 1 if (self._fightPlayer and self._fightPlayer.uid == player.uid) else 0
            recordPlayerInfo[player.uid]["zhuafen"] = player.getScore()
        # 包牌和找朋友
        self._handleInitData()
        # start
        self._startBet()
        # 

    def _handleInitData(self):
        for player in self._curRoundPlayer:
            if player == self._fightPlayer:
                player.addBaopai()
            else:
                player.addFindFriend()

    def _fixRelation(self):
        """确定敌友关系
        """
        for player in self._curRoundPlayer:
            relationMap = { "friend": self.__findFriend(player) }
            relationMap["oppoment"] = self.__findOpponent(player)
            self._relationMap[player] = relationMap
        self.__showRelation()

    def __showRelation(self):
        """显示关系
        """
        info = {}
        for player in self._relationMap:
            info[player.uid] = {}
            info[player.uid]['friend'] = [ tmp.uid for tmp in self._relationMap[player]["friend"] ]
            info[player.uid]['oppoment'] = [ tmp.uid for tmp in self._relationMap[player]["oppoment"] ]
        gameLog.info("relationMap is %s" %(str(info)),)

    def __findFriend(self, player):
        if self._fightPlayer is not None:
            return [ tmp for tmp in self._curRoundPlayer if tmp != player and tmp != self._fightPlayer ]
        otherPublicCardPlayer = None
        for tmp in self._curRoundPlayer:
            if self._otherPublicCard in tmp.cards:
                otherPublicCardPlayer = tmp
        #print otherPublicCardPlayer
        #print set([tmp, player]), set([self._banker, otherPublicCardPlayer])
        #print set([tmp, player]) & set([self._banker, otherPublicCardPlayer])
        return [ tmp for tmp in self._curRoundPlayer if tmp != player   \
                 and ( set([tmp, player]) == set([self._banker, otherPublicCardPlayer]) or \
                       len(set([tmp, player]) & set([self._banker, otherPublicCardPlayer])) == 0) \
                ]

    def __findOpponent(self, player):
        friend = self.__findFriend(player)
        return [ tmp for tmp in self._curRoundPlayer if tmp != player and (tmp not in friend) ]

    def _initPlayer(self):
        players = self._playerInRoom.getSeatStatusPlayer(PlayerStatus.STATUS_READY, True)
        for player in players:
            player.initRound(self._round)  
            self._curRoundPlayer.append(player)

    def _fixedBanker(self):
        players = self._curRoundPlayer
        playerIndexs = [ player.seatNo for player in players ]
        if self._bankerSeat == -1:     # 如果没有确定D位则产生一个随机值
            self._bankerSeat = self._playerInRoom.getPlayerByUID(self._creatorID).seatNo
        else:
            pass
            #tmp = -1
            #for player in playerIndexs:
            #    if player > self._bankerSeat:
            #        tmp = player
            #        break
            #if tmp == -1:
            #    tmp = playerIndexs[0]
            #self._bankerSeat = tmp
        player = self._playerInRoom.getPlayerBySeatNo(self._bankerSeat)
        self._banker = player
        self._curPlayer = player

    def _sendCards(self):
        self._dealer.reinit()    # 重新洗牌
        # 给每个玩家发牌并计算牌型
        for player in self._curRoundPlayer:
            cards = [self._dealer.deal() for i in range (GameCfg.playerCardNum)]
            cards.sort(sortCard)
            player.addCards(cards)


    def _playerChooseFight(self, player):
        self._fightPlayer = player
        self._msgHelper.sendPlayerFight(player.uid, 1)
        self._channel.send(True)

    def _playerGiveupFightTimeout(self, player):
        return

    def _playerGiveupFight(self, player):
        """硬牌超时,视为自动弃牌
        """
        if player.uid != self._curPlayer.uid:
            return
        self._msgHelper.sendPlayerFight(player.uid, 0)
        self._channel.send(False)

    def _choosePublicCard(self):
        """选择一张没有重复的牌
        """
        cards = self._playerInRoom.getPlayerBySeatNo(self._bankerSeat).cards[:]
        random.shuffle(cards)
        for card in cards:
            if card < 104:
                otherSameCard = card + 52 if card < 52 else card - 52 
            else:
                otherSameCard = card - 1 if card%2 == 1 else card + 1
            if otherSameCard not in cards:
                return card, otherSameCard

    def _startBet(self):
        """开始出牌
        """
        # 确定首个玩家
        self._curPlayer = self._playerInRoom.getPlayerBySeatNo(self._bankerSeat) if self._fightPlayer is None else self._fightPlayer
        #self._roundBegin = self._curPlayer
        while True:
            self._waitOpr()
            isNewRound = False
            if self._checkRoundEnd():  #整个游戏结束
                break
            if self._checkBetEnd():    #一轮的出牌结束
                self._lastRoundBegin = self._curCardTypePlayer 
                # self._roundBegin = None 
                isNewRound = True
                self._betEndAccount()
                for player in self._curRoundPlayer:
                    if len(player.cards) == 0:
                        player.setStatus(PlayerStatus.STATUS_FINISH)
            self._nextActivePlayer(-1, isNewRound)
        self._roundAccount()

    def _waitOpr(self):
        """等待玩家出牌
        """
        self._sendNewBet()
        self._startThinkTimer()
        self._channel.receive()

    def _sendNewBet(self):
        self._msgHelper.sendNewBet(self._curPlayer.uid, self._playerThinkTime)

    def _startThinkTimer(self):
        if self._curPlayer.uid in self._testUID:
            self._timer = self._timerManager.addTimer(500, self, "_testPlayerBet", (self._curPlayer,))
        else:
            self._timer = self._timerManager.addTimer(self._playerThinkTime, self, "_thinkTimeOut", None)

    def _testPlayerBet(self, player):
        #self._playerBet(player, player.cards[:])
        #self._channel.send("playerBet")
        self._playerThinkTimeOut()

    def _thinkTimeOut(self, args=None):
        return
        self._playerThinkTimeOut()

    def _playerThinkTimeOut(self):
        """用户思考时间到期
        如果是第一个玩家，则出一张最小的，如果不是第一个玩家，则不出
        """
        player = self._curPlayer
        self._timerManager.delTimer(self._timer)
        if self._curCardTypePlayer is None:
            gameLog.info("roomID: %d player: %d think time out  [auto bet one]" \
                          % (self._roomID, player.uid))
            ret = self._playerBet(player, [player.cards[0]])
        else:
            gameLog.info("roomID: %d player: %d think time out  [auto giveup]" \
                          % (self._roomID, player.uid))
            ret = self._playerGiveup(player)
        if ret == ErrorCode.ERR_OK:
            self._channel.send("timeout")

    def _betEndAccount(self):
        """一轮打牌结束，进行统计
        """
        self._curCardTypePlayer.playerAddScoreCards(self._curBetscoreCards)
        self._recordProcess.append([self._curCardTypePlayer.uid, 2, self._curCardTypePlayer.getScore(), [], 0])
        self._msgHelper.sendBetEndAccount(self._curCardTypePlayer.uid, self._curCardTypePlayer.scoreCards, self._curCardTypePlayer.getScore())
        self._curBetscoreCards = []
        self._curCardType = None
        self._curCardTypePlayer = None

    
    def _calScore(self, cards):
        total = 0
        for card in cards:
            total += CARD_2_SCORE[card%13]
        return total

    def _roundEndAccount(self):
        """一个回合结束，计算每个人加/扣的钱
        """
        pass  

    def _checkRoundEnd(self):
        """检查一个回合是否结束
        """
        if len(self._rankPlayers) == 0:
            return False
        # 有人硬牌的情况
        if self._fightPlayer is not None:
            self._rate = 4
            if self._rankPlayers[0].uid == self._fightPlayer.uid:   # 硬派的玩家赢
                self._winner.append(self._fightPlayer)
            else:       # 非硬牌玩家赢
                self._winner = [ player for player in self._curRoundPlayer if player.uid != self._fightPlayer.uid ]
            return True
        else:
            if len(self._rankPlayers) >= 2:
                # 1,2游为朋友，肯定结束
                if self._rankPlayers[0] == self._findFriend(self._rankPlayers[1]):
                    self._winner = [self._rankPlayers[0], self._rankPlayers[1]]
                    oppoScore = self._getOpponentScore(self._rankPlayers[0])
                    self._rate = 4 if oppoScore == 0 else 2
                    return True
                else:
                    # 优先判断有人满分情况
                    if self._getFriendAllScore(self._rankPlayers[0]) >= 100 and self._getOpponentScore(self._rankPlayers[0]) > 0:
                        self._winner = [self._rankPlayers[0], self._findFriend(self._rankPlayers[0])]
                        return True
                    elif self._rankPlayers[1].getScore() >= 105 and self._getOpponentScore(self._rankPlayers[1]) > 0:
                        self._winner = [self._rankPlayers[1], self._findFriend(self._rankPlayers[1])]
                        return True
                    # 只能等产生了3游才能进行判断
                    if len(self._rankPlayers) > 2:
                        if self._getFriendAllScore(self._rankPlayers[0]) >= 100 and self._getOpponentScore(self._rankPlayers[0]) == 0:
                            self._winner = [self._rankPlayers[0], self._findFriend(self._rankPlayers[0])]
                            if not (self._rankPlayers[1] == self._findFriend(self._rankPlayers[2])):
                                self._rate = 2
                            return True
                        elif self._rankPlayers[1].getScore() >= 105 and self._getOpponentScore(self._rankPlayers[1]) == 0:
                            self._winner = [self._rankPlayers[1], self._findFriend(self._rankPlayers[1])]
                            if not (self._rankPlayers[0] == self._findFriend(self._rankPlayers[2])):
                                self._rate = 2
                            return True
                        elif self._rankPlayers[0] == self._findFriend(self._rankPlayers[2]):
                            self._winner = [self._rankPlayers[0], self._findFriend(self._rankPlayers[0])]
                            if self._getOpponentScore(self._rankPlayers[0]) == 0:
                                self._rate = 2
                            return True
                        elif self._rankPlayers[1] == self._findFriend(self._rankPlayers[2]):
                            #if self._getFriendAllScore(self._rankPlayers[0]) < 100:
                            self._winner = [self._rankPlayers[1], self._findFriend(self._rankPlayers[1])]
                            return True
        return False

    def _getOpponentScore(self, player):
        opponents = self._findOpponent(player)
        oppoScore = 0
        for item in opponents:
            oppoScore += item.getScore()
        return oppoScore

    def _getFriendAllScore(self, player):
        friend = self._findFriend(player)
        return friend.getScore() + player.getScore()
        
   #      else:
   #          #if (self._rankPlayers[0].getScore() + self._findFriend(self._rankPlayers[0]).getScore()) >= 100:
   #          #    self._winner = [ self._rankPlayers[0], self._findFriend(self._rankPlayers[0]) ]
   #          #    return True
   #          if len(self._rankPlayers) >= 2: # 
   #              firstFriend = self._findFriend(self._rankPlayers[0])
   #              if (self._rankPlayers[0].getScore() + firstFriend.getScore()) >= 100 and firstFriend != self._rankPlayers[1]:
   #                  opponents = self._findOpponent(self._rankPlayers[0])
   #                  oppoScore = 0
   #                  for opponent in opponents:
   #                      oppoScore += opponent.getScore()
   #                  if oppoScore > 0:
   #                      self._rate = 1 
   #                      self._winner = [ self._rankPlayers[0], self._findFriend(self._rankPlayers[0]) ]
   #                      return True
   #              if self._findFriend(self._rankPlayers[0]).uid == self._rankPlayers[1].uid: # 1,2为一组
   #                  opponents = self._findOpponent(self._rankPlayers[0])
   #                  oppoScore = 0
   #                  for opponent in opponents:
   #                      oppoScore += opponent.getScore()
   #                  self._rate = 4 if oppoScore == 0 else 2
   #                  self._winner = [ self._rankPlayers[0], self._rankPlayers[1] ]
   #                  return True
   #              else:
   #                  if self._rankPlayers[1].getScore() >= 105:
   #                      opponents = self._findOpponent(self._rankPlayers[1])
   #                      oppoScore = 0
   #                      for opponent in opponents:
   #                          oppoScore += opponent.getScore()
   #                      if oppoScore > 0:
   #                          self._winner = [ self._rankPlayers[1], self._findFriend(self._rankPlayers[1]) ]
   #                          return True
                        # else:
                        #     if len(self._rankPlayers) > 2 and self._rankPlayers[1] == self._findFriend(self._rankPlayers[2]):
   #                              self._winner = [ self._rankPlayers[1], self._findFriend(self._rankPlayers[1]) ]
                        #         self._rate = 2
                        #         return True
   #                  if len(self._rankPlayers) > 2:
   #                      if self._rankPlayers[0].uid == self._findFriend(self._rankPlayers[2]).uid:
   #                          self._winner = [ self._rankPlayers[0], self._rankPlayers[2] ]
   #                          opponents = self._findOpponent(self._rankPlayers[0])
   #                          oppoScore = 0
   #                          for opponent in opponents:
   #                              oppoScore += opponent.getScore()
   #                          self._rate = 2 if oppoScore == 0 else 1
   #                          return True
   #                      else:
   #                          allScoreFirstAndFourth = self._rankPlayers[0].getScore() + self._findFriend(self._rankPlayers[0]).getScore()
   #                          if allScoreFirstAndFourth == 0:
   #                              self._winner = [self._rankPlayers[1], self._rankPlayers[2]]
   #                              self._rate = 2
   #                              return True
   #                          elif allScoreFirstAndFourth >= 100:
   #                              self._winner = [self._rankPlayers[0], self._findFriend(self._rankPlayers[0])]
   #                              return True
   #                          else:
   #                              self._winner = [self._rankPlayers[1], self._rankPlayers[2]]
   #                              return True
   #      return False  

    def _findFriend(self, player):
        return self._relationMap[player]["friend"][0]

    def _findOpponent(self, player):
        return self._relationMap[player]["oppoment"]


    def _checkBetEnd(self):
        """检查一轮出牌是否可以结束了
        下一个出牌玩家是最大牌型的所有者
        """
        #nextSeatno = self._findNextActivePlayer(self._curPlayer.seatNo, False)
        #return True if (nextSeatno != -1 and self._curCardTypePlayer != None and self._curCardTypePlayer.seatNo == nextSeatno) else False
        findNextSeat = self._curPlayer.seatNo
        for i in range(self._maxSeat):
            nextSeatno = self._findNextActivePlayer(findNextSeat, False)
            if (nextSeatno != -1 and self._curCardTypePlayer != None and self._curCardTypePlayer.seatNo == nextSeatno):
                return True  # zhe ge kending yao jieshu 
            else:
                player = self._playerInRoom.getPlayerBySeatNo(nextSeatno)
                if player is None:
                    continue
                if len(player.cards) == 0 and self._curCardTypePlayer.seatNo != nextSeatno:
                    findNextSeat = nextSeatno
                    continue
                else:
                    return False


    def _nextActivePlayer(self, begin=-1, isNewRound=False):
        if begin == -1:
            start = self._curPlayer.seatNo
        else:   # 暂时没有用到
            start = begin 
        # 
        seatNo = self._findNextActivePlayer(start, True, isNewRound)
        seatInfo = self._playerInRoom.seatInfo
        if seatNo >= 0 and seatNo < self._maxSeat:     # 合法的位置
            self._curPlayer = seatInfo[seatNo]
            return True 
        return False

    def _findNextActivePlayer(self, begin, mustActive=True, isNewRound=False):
        for i in range(0,self._maxSeat-1):
            tmp = (begin+1+i)%self._maxSeat
            seatInfo = self._playerInRoom.seatInfo
            player = seatInfo[tmp]
            if not mustActive:
                if player and player.status == PlayerStatus.STATUS_NORMAL:
                    return tmp
            else:   # 必须找到下一家可以出牌的玩家
                if self._hadShowFriend and self._lastRoundBegin != None and len(self._lastRoundBegin.cards) == 0 and isNewRound: # self._roundBegin == None:  # 已经鸣鸡，并且当前玩家出牌完成，下一轮开始的时候，则会从友家开始
                    if player and player.status == PlayerStatus.STATUS_NORMAL and player == self._findFriend(self._lastRoundBegin) and len(player.cards) > 0:
                        #if self._roundBegin is None:
                        #    self._roundBegin = player
                        return tmp
                else:
                    if player and player.status == PlayerStatus.STATUS_NORMAL and len(player.cards) > 0:
                        #if self._roundBegin is None:
                        #    self._roundBegin = player
                        return tmp
        return -1

    def _playerGiveup(self, player):
        """玩家不出
        """
        self._timerManager.delTimer(self._timer)
        self._sendPlayerChooseBet(player, {"type":ActType.ACT_GIVEUP})
        return ErrorCode.ERR_OK

    def _playerBet(self, player, cards):
        """玩家出牌
        """
        if type(cards) == type({}):
            cards = cards.keys()
        cardType = judgeCardType(cards)
        # 无效的牌型或者比上一家的牌小
        isTest = False  
        if not isTest and (cardType[0] == -1 or (self._curCardType is not None and not compareCard(cardType, self._curCardType) > 0) \
           or len(set(cards) & set(player.hadBetCards)) > 0):
            return GameErrorCode.ACTION_NOT_ALLOW
        # 删除定时器
        self._timerManager.delTimer(self._timer)
        player.playerBetCards(cards)
        self._curCardType = cardType
        self._curCardTypePlayer = player
        scoreCards = [card for card in cards if card in SCORECARDS]
        self._curBetscoreCards.extend(scoreCards)   # 找到有分的牌
        self._curCardTypeSeatno = player.seatNo
        rank = -1
        if len(player.cards) == 0:
            self._rankPlayers.append(player)
            rank = len(self._rankPlayers)
        self._sendPlayerChooseBet(player, {"type":ActType.ACT_BET, "info":cardType, "scoreCard":self._curBetscoreCards, "curNum":len(player.cards), "rank":rank})
        #self._recordProcess.append([player.uid, 1, self._curBetscoreCards, cards, rank])
        #
        if cardType[0] > 15:
            self._playerXipai(player)
        if cardType[0] in [10,11,12]:
            cur = player.addTmpXipai()
            if cur == 1:
                self._playerXipai(player)
                player.clearTmpXipai()
        #
        if len(player.cards) == 0:
            # 发送队友的牌
            if self._fightPlayer is None:
                friend = self._findFriend(player)
                friendCards = friend.cards if friend else []
                if friend:
                    self._msgHelper.sendSelfFrientCards(player, friend, friendCards)
        # 如果是表明身份的牌，要下发身份
        if self._otherPublicCard in cards:
            self._msgHelper.sendShowRelation(player.uid)
            self._hadShowFriend = True
        return ErrorCode.ERR_OK

    def _playerXipai(self, player):
        chipInfo = {}
        player.addXipai()
        player.updateChip(3)
        player.updateCurRoundXipaiWin(3)
        #chipInfo[player.uid] = player.chip
        for tmpPlayer in self._curRoundPlayer:
            if player != tmpPlayer:
                tmpPlayer.updateChip(-1)
                tmpPlayer.updateCurRoundXipaiWin(-1)
            chipInfo[tmpPlayer.uid] = player.chip
        self._msgHelper.sendUpdateChip(chipInfo)

    def _sendPlayerChooseBet(self, player, info):
        #
        needSendInfo = [player.uid, info["type"]]
        #
        if info["type"] == ActType.ACT_BET:
            cards = info["info"][2]
            cards.sort(sortCard)
            needSendInfo.append(cards)
            needSendInfo.append(info["info"][0])
            needSendInfo.append(info["rank"])
            allScore = self._calScore(info["scoreCard"])
            needSendInfo.append(allScore)
            record = [player.uid, info["type"], allScore, cards, info["rank"]]
        else:
            record = [player.uid, info["type"], 0, [], 0]
        self._msgHelper.sendPlayerBet(needSendInfo)
        self._recordProcess.append(record)
        #self._waitTime(GameCfg.cfg_ShowPlayerBetTime_MS)

    def _roundAccount(self):
        super(GameRoom, self)._roundAccount()
        gameLog.info("%s %d account round %d " %(self.__class__.__name__, self._roomID, self._round))
        self._timerManager.delTimer(self._timer)
        accountMsg = self._gameAccount()
        self._roundAccountInfo = accountMsg
        self.setStatus(GameRoomStatus.STATUS_ACCOUNT)
        self._msgHelper.roundAccount(accountMsg)
        self._recordHistory["process"] = self._recordProcess
        gameDataInterface.recordHistory(GameCfg.gameType, self._roomID, self._round, json.dumps(self._recordHistory), str(self._genSaveRoundAccunt(accountMsg)), self._pwd, int(time.time()))
        if self._round >= self._roomMaxRound:
            gameLog.info("%s %d room time out!" %(self.__class__.__name__, self._roomID))
            self._closeRoom()
            return
        else:
            #self._timer = self._timerManager.addTimer(GameCfg.cfg_ShowAccountTime_MS, self, "_afterAccount", None)
            self._afterAccount()

    def _gameAccount(self):
        playerInfo = []
        winNum = len(self._winner)
        lostNum = len(self._curRoundPlayer) - len(self._winner)
        if self._fightPlayer is None or winNum == 1:
            winChip = self._rate * lostNum / winNum
            lostChip = winChip * winNum / lostNum
        else:
            winChip = self._rate 
            lostChip = self._rate * winNum
        for player in self._curRoundPlayer:
            updateChip = winChip if player in self._winner else -lostChip
            player.updateChip(updateChip)
            allChip = updateChip + player.curRoundXipaiWin
            playerInfo.append({"nickname": player.nickname, "chip": allChip, "curRoundChip":updateChip, "xipai": player.curRoundXipaiWin ,"avatar":player.avatar, "uid":player.uid, "rank": self._getPlayerRank(player), "score": player.getScore()})
            gameDataInterface.updateGameRecord(player.uid, 1, 1 if player in self._winner else 0 )
        info = {}
        info["playerInfo"] = playerInfo
        info["baseScore"] = 1
        return info

    def _getPlayerRank(self, player):
        return -1 if player not in self._rankPlayers else (self._rankPlayers.index(player ) + 1)

    def _clearRound(self):
        super(GameRoom, self)._clearRound()
        self._fightPlayer   = None
        self._bankerSeat = self._rankPlayers[0].seatNo 
        self._banker = None
        self._curPlayer  = -1      
        self._publicCard = -1      
        #self._roundBegin = None 
        self._lastRoundBegin = None 
        self._otherPublicCard = -1 
        self._hadShowFriend = False        
        self._betEnd = False
        self._curCardType = None
        self._curCardTypePlayer = None 
        self._curBetscoreCards = []   
        self._rankPlayers = []       
        self._rate = 1           
        self._relationMap = {}
        self._winner = []
        self._roundAccountInfo = None
        self._recordProcess = []

    def _getAccountTime(self):
        """计算用户能在结算阶段停留的时间
        """
        return GameCfg.cfg_ShowAccountTime_MS

    def _genSnapshot(self, selfPlayer):
        """玩家进入房间时候，生成房间快照给玩家来展现房间当前的状态
        """
        snapshot = {}
        # baseInfo
        snapshot["baseRoomInfo"] = {
            "roomID": self._roomID,
            "payType": self._eachGive,
            "status": self._getSnapshotStatus(),
            "curRound": self._round,
            "allRound": self._roomMaxRound,
            "scoreCard":self._curBetscoreCards,
            "jiaopai": self._publicCard,
            "betInfo": self._genBetInfo()
        }
        players = self._playerInRoom.seatInfo
        playerInfo = {}
        for player in players:
            if player:
                playerInfo[player.uid] = self._genPlayerSnapshot(player, player.getBaseSnapshot(), selfPlayer)
            # playerInfo.append(player.getBaseSnapshot() if player is not None else {})
            #if player is not None:
            #    playerInfo.append(player.getBaseSnapshot() if player is not None else None)
        snapshot["basePlayerInfo"] = playerInfo  
        # status 
        #if self._status == GameRoomStatus.STATUS_PLAYING:
        #    playingInfo = {}
        #    players = self._curRoundPlayer
        #    for player in players:
        #        playingInfo[player.uid] = player.getPlayingSnapshot()
        #    snapshot["playingInfo"] = playingInfo
        #    snapshot["selfPlayingInfo"] = selfPlayer.getSelfPlayingInfo()
        #elif self._status == GameRoomStatus.STATUS_ACCOUNT:
        #    snapshot["account"] = self._roundAccountInfo
        snapshot["selfInfo"] = self._genSelfInfo(selfPlayer)
        snapshot["friendInfo"] = self._genFriendInfo(selfPlayer)
        gameLog.info("player %d snapshot is: %s" % (selfPlayer.uid, str(snapshot)))
        return snapshot

    def _genPlayerSnapshot(self, player, baseInfo, selfPlayer):
        info = baseInfo
        info["banker"] = 1 if player.uid == self._creatorID else 0
        info["zhuang"] = 1 if (self._banker and player.uid == self._banker.uid) else 0
        info["you"] = 0 if player not in self._rankPlayers else (self._rankPlayers.index(player) + 1)
        info["paiCount"] = len(player.cards)
        info["mingji"] = 1 if (self._hadShowFriend and player == self._findFriend(self._banker)) else 0
        info["yingpai"] = 1 if (self._fightPlayer and self._fightPlayer.uid == player.uid) else 0
        info["zhuafen"] = player.getScore()
        info["isOnline"] = player.isOnline
        info["card"] = [] if player != selfPlayer else player.cards
        info["friendInfo"] = {} if player != selfPlayer else self._genFriendInfo(selfPlayer)
        return info

    def _genSelfInfo(self, player):
        info = {}
        info["card"] = player.cards
        info["uid"] = player.uid
        return info

    def _genFriendInfo(self, player):
        info = {}
        # 如果自己出完了牌，并且已经亮了鸡
        needShow = (not self._fightPlayer) and self._banker and len(player.cards) == 0
        info["hadShowFriendCard"] = 1 if needShow else 0
        info["card"] = []
        info['uid'] = -1
        if needShow:
            friend = self._findFriend(player)
            info["card"] = friend.cards
            info["uid"] = friend.uid
        return info

    def _genBetInfo(self):
        info = {}
        #
        status = 0  # 0 没有下注 1 在硬牌 2 在出牌
        if self._status == GameRoomStatus.STATUS_ACCOUNT: 
            status = 3
        curUID = -1
        leftTime = -1
        if self._status == GameRoomStatus.STATUS_FIGHT:
            status = 1
            curUID = -1 if self._curPlayer is None else self._curPlayer.uid
            leftTime = -1 if self._curPlayer is None else self._timerManager.getLeftTime(self._timer)
        elif self._status == GameRoomStatus.STATUS_PLAYING:
            status = 2
            #
            curCardType = self._curCardType
            curCardTypePlayer = self._curCardTypePlayer            
            #
            lastUID = -1 if curCardTypePlayer is None else curCardTypePlayer.uid
            lastCard = [] if curCardType is None else curCardType[2]
            curUID = -1 if self._curPlayer is None else self._curPlayer.uid
            leftTime = -1 if self._curPlayer is None else self._timerManager.getLeftTime(self._timer)
            info["lastUID"] = lastUID
            info["lastCard"] = lastCard
        info["status"] = status
        info["curUID"] = curUID
        info["leftTime"] = leftTime
        return info


############## public ####################


    @hadInRoom
    def playerOneFightOthers(self, uid, opt, **kwargs):
        """玩家硬牌 0 
        """
        player = kwargs["player"]
        if player.uid != self._curPlayer.uid or self._status != GameRoomStatus.STATUS_FIGHT:
            return ErrorCode.ERR_FAIL, {}
        self._timerManager.delTimer(self._timer)
        if opt == 0:
            self._playerChooseFight(player)
        else:
            self._playerGiveupFight(player)
        return ErrorCode.ERR_OK, {}

    @hadInRoom
    def playerBet(self, uid, betInfo, **kwargs):
        """玩家出牌
        """
        err = ErrorCode.ERR_FAIL
        if self._curPlayer.uid != uid:
            return err, {}
        player = kwargs["player"]
        betType, info = betInfo.get("type",0), betInfo.get("info",None)
        if betType == ActType.ACT_GIVEUP:
            if self._curCardTypePlayer is None: # 第一个玩家不能不出
                err = ErrorCode.ERR_FAIL
            else:
                err = self._playerGiveup(player)
        elif betType == ActType.ACT_BET:
            err = self._playerBet(player, info)
        if err == ErrorCode.ERR_OK:
            self._channel.send("playerBet")
        return err, {}

    @hadInRoom
    def playerNeedHint(self, uid, **kwargs):
        """玩家需要提示
        """
        player = kwargs["player"]
        ret, data = hintCard(self._curCardType, player.cards)
        return ret, data



##########################################################
"""
无论几个人
1+队友 >= 100 直接获胜

前两个是一组的
    1,2直接获胜
    对手有分 2倍
    对手没分 4倍

前两个不是一组的
    2 >=105     2+队友获胜
    如果有3
    1,3一组   
        对手有分 1倍
        对手没分 2倍
    1,3不是一组
        1+4 = 0        # 2,3获胜2倍
        100 > 1+4 > 0  # 2,3获胜1倍
                1+4 >= 100    # 1,4获胜1倍 
"""
