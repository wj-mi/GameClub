# coding:utf-8

# 有人可以吃碰杠胡的时候，要给这些玩家停留一定的时间，不会展示有哪些玩家可以对它进行操作


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
from cardHelper import *
from gameDealer import GameDealer 
import simplejson as json



class GameRoom(BaseRoom):
    def __init__(self, args):
        BaseRoom.__init__(self, args)
        self._dealer = GameDealer();
        self._maxSeat       = args["playerNum"]
        self._playerThinkTime   = GameCfg.cfg_PlayerBetTime_MS  
        self._timer     = None     # timer
        self._bankerSeat = -1
        self._laizi = -1
        self._banker = None
        self._curPlayer  = -1      # -1 未初始化 None没有玩家, Player玩家
        self._hupaiPlayer = None
        self._oldHupaiPlayer = None 
        self._hupaiType = None     # [[自摸,参数], 胡牌类型pai, 清一色]
                                   # [[0自摸1点炮,谁点的炮], 1 7大对 2 普通, 0 普通 1 清一色]
        self._curBetCard = None
        self._hupaiInfo = None
        self._canHuPlayer = []     # 本轮可以胡牌的玩家，用于做让牌用
        self._recordHistory = {}   # 用于做牌局回放
        self._recordProcess = []
        self._playerChooseMap = {   # 1吃 2碰 3明杠 4放炮胡 6过,12边杠，13暗杠 14自摸
            2: self._playerChoosePeng,
            3: self._playerChooseGang,
            1: self._playerChooseChi,
            4: self._playerChooseHu,
            6: self._playerChoosePass
        }
        self._playerCanChooseMap = {   # 1吃 2碰 3明杠 4放炮胡 6过,7mo 8chu 12边杠，13暗杠 14自摸
            2: self._playerCanChoosePeng,
            3: self._playerCanChooseGang,
            1: self._playerCanChooseChi,
            4: self._playerCanChooseHu,
            6: self._playerCanChoosePass
        }
        self._recordPlayerAction = {}
        self._lastPlayerChoose = None
        self._isHandleBet = False
        #
        self._curChooseAction = None
        self._canStartBet = False
        self._isQiangGang = 0
        self._whyBet = 0
        #
        self._firstChooseForce = None
        self._forceStartChooseTimer = None
        self._chooseForceStart = []
        #self._qiangGangChannel = stackless.channel()
        self._giveChipInfo = {   
            1: {    
                  1: {
                        1: {"fan": 4, "dianpao": 0},  # 大胡自摸用癞子
                        0: {"fan": 8, "dianpao": 0}   # 大胡自摸没用癞子
                     }, # 大胡自摸
                  0: {
                        1: {"fan": 3, "dianpao": 1},  # 大胡点炮用癞子
                        0: {"fan": 6, "dianpao": 2}   # 大胡点炮没用癞子
                     } # 大胡点炮
                },  # 大胡
            0: {    
                  1: {
                        1: {"fan": 3, "dianpao": 0},  # 小胡自摸用癞子
                        0: {"fan": 6, "dianpao": 0}   # 小胡自摸没用癞子
                     }, # 小胡自摸
                  0: {
                        1: {"fan": 1, "dianpao": 1},  # 小胡点炮用癞子
                        0: {"fan": 2, "dianpao": 2}   # 小胡点炮没用癞子
                     } # 小胡点炮
                }  # 小胡

            }

        # 
        self._testUID = []
        for uid in self._testUID:
            self.c2s_enterRoom(uid, None, None)

    def _startRound(self):
        #
        # sleep 1s
        old_atom = self._enter()
        self._canStartBet = False
        #
        self._firstChooseForce = None 
        self._chooseForceStart = [] 
        self._timerManager.delTimer(self._forceStartChooseTimer)
        #
        #self._waitTime(1000)
        #
        super(GameRoom, self)._startRound()
        # initPlayer
        self._initPlayer()
        #
        self._status = GameRoomStatus.STATUS_PLAYING
        # fixed banker
        self._fixedBanker()
        # 
        self._dealer.reinit()    # 重新洗牌
        # fixed laizi
        self._fixedLaizi()
        # sendCards
        self._sendCards()
        self._exit(old_atom)
        # sendmsg
        recordStartInfo = { "banker":self._bankerSeat, "roomnum": self._pwd, "curRound": self._round, "laizi": self._laizi, "roomID": self._roomID, \
                            "status": self._status, "curRound": self._round, "allRound": self._roomMaxRound, "rest": len(self._dealer.notUseCards), \
                            "betInfo": {}, "payType": self._eachGive }

        recordPlayerInfo = {}
        baseInfo = { "banker":self._bankerSeat, "bankerId": self._banker.uid ,"curRound": self._round, "laizi": self._laizi}
        for player in self._curRoundPlayer:
            baseInfo["cards"] = player.cards
            tmpInfo = {"status": player.status, "isOnline":player.isOnline, "seatnum":player.seatNo, "allChip": player.chip, "uid":player.uid, "gender":0, "chip":player.chip, "gang":[], "peng":[], "deskcard":[], "avatar":player.avatar, \
                       "nickname": player.nickname , "chi": [], "card":player.cards[:]}
            tmpInfo["banker"] = 1 if player.uid == self._creatorID else 0
            tmpInfo["zhuang"] = 1 if (self._banker and player.uid == self._banker.uid) else 0
            recordPlayerInfo[player.uid] = tmpInfo
            self._msgHelper.sendStartRound(player, baseInfo)
        recordStartInfo["playerInfo"] = recordPlayerInfo
        self._recordHistory["roomInfo"] = recordStartInfo
        #
        #self._waitTime(2000)
        # start
        self._startBet()
        # 

    def _changeSeat(self, player, newSeat):
        #
        return 0
        if player.seatNo == newSeat:
            return 0
        oldStatus = player.status
        self._playerInRoom.standup(player)
        player.sitdown(newSeat, oldStatus)
        self._playerInRoom.sitdown(player, newSeat)
        return 1
        #self._playerInRoom.sitdow

    def _initPlayer(self):
        players = self._playerInRoom.getSeatStatusPlayer(PlayerStatus.STATUS_READY, True)
        #
        if len(players) == 2 or len(players) == 3:
            if len(players) == 2:
                useSeat = [0,2]
            else:
                useSeat = [0,1,3]
            changeNum = 0
            for index, player in enumerate(players):
                changeNum += self._changeSeat(player, useSeat[index])
            if changeNum > 0:
                for player in players:
                    err, data = self.c2s_enterRoom(player.uid, player.sid, None)
                    data['baseRoomInfo']["status"] = 1
                    self._msgHelper.sendChangeSeatno(player, data)
        #
        for player in players:
            player.initRound(self._round)  
            self._curRoundPlayer.append(player)

    def _fixedBanker(self):
        if self._oldHupaiPlayer == None:
            players = self._curRoundPlayer
            playerIndexs = [ player.seatNo for player in players ]
            if self._bankerSeat == -1:     # 如果没有确定,则产生一个随机值
                self._bankerSeat = self._playerInRoom.getPlayerByUID(self._creatorID).seatNo
            else:
                pass 
            player = self._playerInRoom.getPlayerBySeatNo(self._bankerSeat)
            self._banker = player
            self._curPlayer = player
        else:
            self._bankerSeat = self._oldHupaiPlayer.seatNo
            self._banker = self._oldHupaiPlayer
            self._curPlayer = self._banker

    # def _standup(self, player):
    #     """玩家站起
    #     """
    #     self._playerInRoom.standup(player)
    #     gameLog.info("%s %d, player %d  standup " %(self.__class__.__name__, self._roomID, player.uid))
    #     player.standup()
    #     #self._msgHelper.playerStandupMsg(player.uid)



    @hadInRoom    
    def playerReady(self, uid, opt=1,**kwargs):
        """玩家准备/取消准备
        """
        old_atom = self._enter
        player = kwargs["player"]
        if self._status != GameRoomStatus.STATUS_PLAYING:
            self._msgHelper.sendPlayerReady(uid, opt)
        if opt == 1:
            #self.userLoginLogout(uid, 0)
            if player.status == PlayerStatus.STATUS_WAIT_READY:
                player.setStatus(PlayerStatus.STATUS_READY)
                self._judgeNeedSendStartLessPlayerGame(True)
            #
            #

        else:
            player.setStatus(PlayerStatus.STATUS_WAIT_READY)
            self._msgHelper.sendStartLessPlayerGame(self._playerInRoom.getPlayerByUID(self._creatorID), -1)
            self._timerManager.delTimer(self._forceStartChooseTimer)
            self._msgHelper.sendHideForceStart()
            self._firstChooseForce = None
            self._chooseForceStart = []
            self._timerManager.delTimer(self._forceStartChooseTimer)
        return ErrorCode.ERR_OK, None

    def _judgeNeedSendStartLessPlayerGame(self, judgeStartRound=False):
        readyPlayerNum = len(self._playerInRoom.getSeatStatusPlayer(PlayerStatus.STATUS_READY))
        seatPlayerNum = len(self._playerInRoom.getPlayerInSeat())
        if readyPlayerNum != seatPlayerNum:
            pass
        else:
            if readyPlayerNum < self._maxPlayer and readyPlayerNum >= 2:
                self._msgHelper.sendStartLessPlayerGame(self._playerInRoom.getPlayerByUID(self._creatorID), readyPlayerNum)
            else:
                if judgeStartRound:
                    self._judgeStartRound()

    def _canStartRound(self, args={}):
        """判断是否可以开始游戏
        """
        num = len(self._playerInRoom.getSeatStatusPlayer(PlayerStatus.STATUS_READY))
        gameLog.info("room %d had ready player num: %d , need args %s" %(self._roomID, num, str(args)))
        maxPlayer = args['num'] if args.get("force", False) else self._maxPlayer
        return False if num  < maxPlayer else True


    def _playerSitdownSuccess(self, player):
        self._chooseForceStart = []
        self._timerManager.delTimer(self._forceStartChooseTimer)
        if player.uid not in self._testUID:
            self._msgHelper.sendStartLessPlayerGame(self._playerInRoom.getPlayerByUID(self._creatorID), -1)
            self._timerManager.delTimer(self._forceStartChooseTimer)
            self._msgHelper.sendHideForceStart()



    def _playerLeaveSuccess(self, player):
        readyPlayerNum = len(self._playerInRoom.getSeatStatusPlayer(PlayerStatus.STATUS_READY))
        if readyPlayerNum < self._maxSeat:
            sendReadyPlayerNum = readyPlayerNum
            if sendReadyPlayerNum < 2:
                sendReadyPlayerNum = -1
            self._msgHelper.sendStartLessPlayerGame(self._playerInRoom.getPlayerByUID(self._creatorID), sendReadyPlayerNum)


    @staticmethod
    def ziMoSort(player1, player2):
        if player1._allChip > player2._allChip:
            return 1
        elif player1._allChip < player2._allChip:
            return -1
        return 0

    @hadInRoom
    def playerForceStart(self, uid, num, choose, **kwargs):
        #if uid != self._creatorID:
        #    return ErrorCode.ERR_FAIL, None
        old_atomic = self._enter()
        player = kwargs["player"]
        readyPlayer = self._playerInRoom.getSeatStatusPlayer(PlayerStatus.STATUS_READY)
        if len(self._playerInRoom.getPlayerInSeat())  != len(readyPlayer):
            self._exit(old_atomic)
            return ErrorCode.ERR_FAIL, None
        if choose == 0:   # giveup
            if len(self._chooseForceStart) == 0:
                self._exit(old_atomic)
                return ErrorCode.ERR_OK, None
            self._chooseForceStart = []
            self._timerManager.delTimer(self._forceStartChooseTimer)
            self._msgHelper.sendStartLessPlayerGame(self._playerInRoom.getPlayerByUID(self._creatorID), len(readyPlayer))
            self._timerManager.delTimer(self._forceStartChooseTimer)
            self._msgHelper.sendHideForceStart()
        else:
            needSend = False
            if len(self._chooseForceStart) == 0:
                self._chooseForceStart = []
                self._firstChooseForce = player
                self._forceStartChooseTimer = self._timerManager.addTimer(60000, self, "forceStartChooseTimeout", None)
                needSend = True
                for p in readyPlayer:
                    info = {"uid": p.uid, "choose": -1, "avatar": p.avatar, "nickname": p.nickname}
                    self._chooseForceStart.append(info)
            for item in self._chooseForceStart:
                if item["uid"] == player.uid:
                    item["choose"] = choose
            self._sendChooseForceStart()
            #
            readyNum = 0
            for item in self._chooseForceStart:
                if item["choose"] == 1:
                    readyNum += 1
            if readyNum == len(self._chooseForceStart):
                self._firstChooseForce = None
                self._chooseForceStart = []
                self._maxPlayer = readyNum
                self._creatorCost = GameCfg.createCost[self._roomMaxRound][readyNum]
                self._timerManager.delTimer(self._forceStartChooseTimer)
                self._judgeStartRound({"force":True, "num":readyNum})
        self._exit(old_atomic)
        return ErrorCode.ERR_OK, None

    def forceStartChooseTimeout(self, args=None):
        if len(self._chooseForceStart) == 0:
            return 
        for item in self._chooseForceStart:
            if item["choose"] != 1:
                self.playerForceStart(item["uid"], 1, 0)
                break

    def _sendChooseForceStart(self):
        self._msgHelper.sendPlayerForceStart({"firstChoose": {"nickname": self._firstChooseForce.nickname, "uid": self._firstChooseForce.uid}, "chooseInfo":self._chooseForceStart, "leftTime":  0 if self._forceStartChooseTimer is None else self._timerManager.getLeftTime(self._forceStartChooseTimer)})



    @staticmethod
    def laiziSort(card1, card2):
        if card1[0].count(card1[1]) > card2[0].count(card2[1]):
            return 1
        elif card1[0].count(card1[1]) < card2[0].count(card2[1]):
            return -1
        return 0

    def _sendCards(self):
        # 给每个玩家发牌并计算牌型
        allPlayers = self._curRoundPlayer[:]
        allPlayers.sort(GameRoom.ziMoSort)
        gameLog.error("player zimo sort [%s]" %(str([player._allChip for player in allPlayers])))
        needCarPlayer = None
        #if allPlayers[-1]._zimoCount - allPlayers[0]._zimoCount >= 2:
        #    needCarPlayer = allPlayers[0]
        #random.shuffle(allPlayers)
        tmpCards = []
        for index in range(len(allPlayers)):
            cards = [self._dealer.deal() for i in range (GameCfg.playerCardNum)]
            tmpCards.append(cards)
        sortCards = [ [item, self._laizi] for item in tmpCards ]
        sortCards.sort(GameRoom.laiziSort)
        tmpCards = [ item[0] for item in sortCards ]
        #gameLog.error("laiziSort %s" %(str([card.count(self._laizi) for card in tmpCards])))
        #
        if needCarPlayer is not None:
            needCarPlayer.addCards(tmpCards[-1])
            gameLog.info("car player [%d] current zimo [%d], give cards [%s], curLaiz [%d]" %(needCarPlayer.uid, needCarPlayer._zimoCount, str(tmpCards[-1]), tmpCards[-1].count(self._laizi)))
            allPlayers = allPlayers[1:]
            tmpCards = tmpCards[:-1]
        #
        for index, player in enumerate(allPlayers):
            #gameLog.error("player [%d] hu [%d], getCard laizi [%d]" %(player.uid, player._allChip, tmpCards[len(tmpCards)-1-index].count(self._laizi)))
            player.addCards(tmpCards[len(tmpCards)-1-index])


    #def _sendCards(self):
        # 给每个玩家发牌并计算牌型
    #    allPlayers = self._curRoundPlayer[:]
    #    random.shuffle(allPlayers)  
    #    for player in allPlayers:
    #        cards = [self._dealer.deal() for i in range (GameCfg.playerCardNum)]
            #cards.sort(sortCard)
    #        player.addCards(cards)

    def _fixedLaizi(self):
        self._laizi = self._dealer.getLaizi()

    def _startBet(self):
        """开始出牌
        """
        # 确定首个玩家
        self._curPlayer = self._playerInRoom.getPlayerBySeatNo(self._bankerSeat)
        self._whyBet = 0
        #self._roundBegin = self._curPlayer
        #isFirst = True
        needGetOneCard = True
        self._canStartBet = True
        self._isHandleBet = False
        while True:
            ret = self._waitOpr(needGetOneCard)
            if type(ret) != type([]):
                pass 
            else:
                nextPlayer, needGetOneCard = ret[0], ret[1]
                if nextPlayer is not None and not needGetOneCard:
                    self._whyBet = 1
                else:
                    self._whyBet = 0
                if self._checkRoundEnd(needGetOneCard):  #整个游戏结束
                    break
                if nextPlayer is None:
                    self._nextActivePlayer()
                else:
                    self._curPlayer = nextPlayer
            self._isHandleBet = False
        self._roundAccount()
            #if 
            #self._curPlayer.getOneCard(self._dealer.deal())


    def _nextActivePlayer(self):
        start = self._curPlayer.seatNo
        player = self._findNextActivePlayer(start)
        self._curPlayer = player
        return True

    def _findNextActivePlayer(self, begin):
        for i in range(self._maxSeat):
            seat = (begin+1+i)%self._maxSeat
            seatPlayer = self._playerInRoom.getPlayerBySeatNo(seat)
            if seatPlayer and seatPlayer in self._curRoundPlayer:
                return seatPlayer
        return None
        #    if self._playerInRoom.seatInfo[seat]
        #seat = (begin+1)%self._maxSeat
        #return self._playerInRoom.seatInfo[seat]

    def _waitOpr(self, needGetOneCard):
        """等待玩家出牌
        """
        if not needGetOneCard:
            if self._curPlayer in self._canHuPlayer:
                self._canHuPlayer.remove(self._curPlayer)
        else:
            card = self._dealer.deal()
            self._curPlayer.getOneCard(card)
            self._recordProcess.append([7,self._curPlayer.uid, self._curPlayer.uid, [card], card ])    # actiontype uid targetuid card
            self._sendNewBet(1, card, len(self._dealer.notUseCards))
        self._startThinkTimer()
        return self._channel.receive()

    def _sendNewBet(self, getCard=0, card=-1, rest=0):
        gameLog.info("send new bet player[%d] getCard[%d] card[%d]" % (self._curPlayer.uid, getCard, card))
        if self._curPlayer in self._canHuPlayer:
            self._canHuPlayer.remove(self._curPlayer)
        if card != -1:  card = card
        for player in self._curRoundPlayer:
            self._msgHelper.sendNewBet(player, self._curPlayer.uid, self._playerThinkTime, getCard, card if self._curPlayer.uid == player.uid else -1, rest)

    def _startThinkTimer(self):
        if self._curPlayer.uid in self._testUID:
            self._timer = self._timerManager.addTimer(5, self, "_thinkTimeOut", (self._curPlayer,))
        else:
            self._timer = self._timerManager.addTimer(self._playerThinkTime, self, "_thinkTimeOut", None)

    def _thinkTimeOut(self, args=None):
        self._playerThinkTimeOut()

    def _playerThinkTimeOut(self):
        """用户思考时间到期
        如果是第一个玩家，则出一张最小的，如果不是第一个玩家，则不出
        """ 
        player = self._curPlayer
        if player.uid in self._testUID:
            self._timerManager.delTimer(self._timer)
            card = self._findCanSendCard(player.cards)
            gameLog.info("roomID: %d player: %d think time out  [auto bet %d]"  % (self._roomID, player.uid, card))
            self._wrapPlayerBet(player, card)

    def _findCanSendCard(self, cards):
        for card in cards:
            if card != self._laizi:
                return card
        return cards[0]

    def _wrapPlayerBet(self, player, card):
        if card not in player.cards or card == self._laizi:
            self._isHandleBet = False
            return ErrorCode.ERR_FAIL, None
        self._timerManager.delTimer(self._timer)
        player.playerBetCard(card, True)
        self._curBetCard = card
        err = ErrorCode.ERR_OK
        self._recordProcess.append([8, self._curPlayer.uid, self._curPlayer.uid, [card], card ])
        self._sendPlayerBet(player, card)
        #self._isHandleBet = False
        self._checkPlayerAction(player, card)
        return err, {}

    def _checkPlayerAction(self, player, card, isQiangGang=False):
        sendAction = False
        sendCard = card
        actionInfo = {}
        for tmp in self._curRoundPlayer:
            if tmp != player:
                info = judgePlayerAction(tmp.cards, card, self._laizi, [tmp.justPengCard, tmp.justGangCard, tmp.justChiCard])
                if info:
                    actionInfo[tmp] = info
                    #sendAction = True
                    #self._msgHelper.sendPlayerCanChoose(player, info, sendCard)
        needRemove = []
        for tmpPlayer in actionInfo:
            if tmpPlayer.uid in self._testUID:
                needRemove.append(tmpPlayer)
        for itemRemove in needRemove:
            actionInfo.pop(itemRemove, None)
        # 强制处理，只能吃上一家的
        nextPlayer = self._findNextActivePlayer(self._curPlayer.seatNo)
        justChipPlayer = []
        for tmp in actionInfo:
            # rang player 
            info = actionInfo[tmp]
            if tmp in self._canHuPlayer and actionInfo[tmp]["hu"] == 1 and not (actionInfo[tmp]["huType"][0] == 1 or actionInfo[tmp]["huType"][1] != 0):
                  actionInfo[tmp]["hu"] = 0  
            #
            if nextPlayer != tmp:
                #info = actionInfo[tmp]
                info["chi"] = 0
            if info["peng"] == 0 and info["gang"] == 0 and info["chi"] == 0 and info["hu"] == 0:
                justChipPlayer.append(tmp)
        for tmp in justChipPlayer:
            actionInfo.pop(tmp, None)
        if not isQiangGang:
            if len(actionInfo) == 0: # sendAction:
                self._channel.send([None, True])
            else:
                #self._msgHelper.sendTestMsg(actionInfo)
                #gameLog.error("room %d action Info %s" %(self._roomID, str(actionInfo)))
                for tmp in actionInfo:
                    if actionInfo[tmp]["hu"] != 0:
                        if tmp not in self._canHuPlayer:
                            self._canHuPlayer.append(tmp)
                self._handlePlayerAction(actionInfo)
        else:
            qiangGangInfo = {}
            for tmp in actionInfo:
                tmpAction = actionInfo[tmp]
                if tmpAction["hu"] != 0:
                    tmpAction["chi"] = 0
                    tmpAction["peng"] = 0
                    tmpAction["gang"] = 0
                    if tmp not in self._canHuPlayer:
                        self._canHuPlayer.append(tmp)
                    qiangGangInfo[tmp] = tmpAction #{"gang":0, "chi":0, "peng":0, "hu": tmp["hu"]}
            return qiangGangInfo
    
    def _getHuType(self, huType, useLaizi, qing):
        """1软小胡，2硬小胡　3软大胡，4硬大胡
        """
        if isUseLazi:
            if qing == 1 or huType == 1:
                return 3
            else:
                return 1
        else:
            if qing == 1 or huType == 1:
                return 4
            else:
                return 2


    def _genSendActionMsg(self, allowAction):
        tmpl = {"peng":0, "gang":0, "chi":0, "hu":0}
        for action in allowAction:
            tmpl[action] = 1
        return tmpl


    def _handlePlayerAction(self, actionInfo):
        # 胡牌 > 碰牌 > 吃牌
        self._curChooseAction = actionInfo
        # 
        # isAllTest = True
        # for player in actionInfo:
        #     if not player.uid in self._testUID:
        #         isAllTest = False
        # #
        # if isAllTest:
        #    self._channel.send([None, True])
        #    return
        self._timer = self._timerManager.addTimer(GameCfg.cfg_PlayerActionTime_MS, self, "_playerChooseActionTimeout", None)
        for player in actionInfo:
            self._msgHelper.sendPlayerCanChoose(player, actionInfo[player], GameCfg.cfg_PlayerActionTime_MS)
        self._msgHelper.sendHadPlayerChooseAction(GameCfg.cfg_PlayerActionTime_MS)
        #self._timer = self._timerManager.addTimer(GameCfg.cfg_PlayerActionTime_MS, self, "_playerChooseActionTimeout", None)

    def _playerChooseActionTimeout(self, args=None):
        return

    # def _playerChooseAction(self, args=None):
    #     self._curChooseAction = None
    #     #
    #     player, actionInfo = self._judgeTimeoutGetPlayerAction()
    #     gameLog.info("choose action timeout, player[%d] info[%s]" %(player.uid if player != None else -1, str(actionInfo)))
    #     if player != None and actionInfo != None:
    #         self.playerChooseAct(player.uid, actionInfo, True)
    #     else:
    #         self._channel.send([None, True])

    def _judgeTimeoutGetPlayerAction(self):
        # judge Hu
        chooseHuPlayer = []
        for player in self._recordPlayerAction:
            if self._recordPlayerAction[player]["actiontype"] == 4:
                chooseHuPlayer.append(player)
        for i in range(4):
            seat = (self._curPlayer.seatNo + i)%self._maxSeat
            player = self._playerInRoom.getPlayerBySeatNo(seat)
            if player in chooseHuPlayer:
                return player, self._recordPlayerAction[player]
        # judge gang/peng
        for player in self._recordPlayerAction:
            action = self._recordPlayerAction[player]["actiontype"]
            if action == 2 or action == 3:
                return player, self._recordPlayerAction[player]
        # judge chi
        for player in self._recordPlayerAction:
            if self._recordPlayerAction[player]["actiontype"] == 1:
                return player, self._recordPlayerAction[player]
        return None, None

    def _sendPlayerBet(self, player, card):
        info = {}
        info["uid"] = player.uid
        info["card"] = card
        self._msgHelper.sendPlayerBet(info)

    def _checkRoundEnd(self, needGetOneCard):
        """有人胡牌或者已经没有牌了
        """
        if (len(self._dealer.notUseCards) == 0 and needGetOneCard) or self._hupaiPlayer is not None:
            return True
        return False

    def _roundAccount(self):
        self._canStartBet = False
        super(GameRoom, self)._roundAccount()
        gameLog.info("%s %d account round %d " %(self.__class__.__name__, self._roomID, self._round))
        self._timerManager.delTimer(self._timer)
        accountMsg = self._gameAccount()
        self._recordHistory["account"] = accountMsg
        self._roundAccountInfo = accountMsg
        self.setStatus(GameRoomStatus.STATUS_ACCOUNT)
        self._recordHistory["process"] = self._recordProcess
        gameDataInterface.recordHistory(GameCfg.gameType, self._roomID, self._round, json.dumps(self._recordHistory), str(self._genSaveRoundAccunt(accountMsg)), self._pwd, int(time.time()))
        self._msgHelper.roundAccount(accountMsg)
        #gameDataInterface.recordHistory(GameCfg.gameType, self._roomID, self._round, json.dumps(self._recordHistory), str(self._genSaveRoundAccunt(accountMsg)), self._pwd, int(time.time()))
        if self._round >= self._roomMaxRound:
            gameLog.info("%s %d room time out!" %(self.__class__.__name__, self._roomID))
            self._closeRoom()
            return
        else:
            self._afterAccount()




    def _gameAccount(self):
        playerInfo = []
        fanBei = 1
        dianPaoMoreGive = 0
        dianPao = None
        if self._hupaiPlayer is None:
            for player in self._curRoundPlayer:
                playerCards = player.cards
                playerCards.sort()
                gameDataInterface.updateGameRecord(player.uid, 1, 0 )
                chiPengGang = []
                chiPengGang.extend(player.chiCard)
                chiPengGang.extend(player.pengCard)
                chiPengGang.extend(player.gangCard)
                #info['chipenggangs'] = chiPengGang
                playerInfo.append({"hu": 0, "card":playerCards, "chipenggangs": chiPengGang, \
                                   "chip": 0 ,"avatar":player.avatar, "uid":player.uid, \
                                   "nickname": player.nickname, "pao": 0, "hutype": "", "banker": 0 if player.uid != self._creatorID else 1 })
        else:
            isDahu = self._hupaiInfo["cardType"][0] == 1 or self._hupaiInfo["cardType"][1] != 0  # 清一色或大对
            isZimo = self._hupaiInfo["zimo"]
            isUseLazi = self._hupaiInfo["cardType"][2]
            dianPao = None if isZimo else self._hupaiInfo["dianpao"]
            fanBei = self._giveChipInfo[isDahu][isZimo][isUseLazi]["fan"]
            dianPaoMoreGive = self._giveChipInfo[isDahu][isZimo][isUseLazi]["dianpao"]
            lostGive = 0
            for player in self._curRoundPlayer:
                curPlayerGive = 0
                curPlayerDianPao = 0
                if player != self._hupaiPlayer:
                    curPlayerGive += fanBei
                    if player == dianPao:
                        curPlayerDianPao = 1
                        curPlayerGive += dianPaoMoreGive
                    player.updateChip(-curPlayerGive)
                    lostGive += curPlayerGive
                    playerCards = player.cards
                    playerCards.sort()
                    gameDataInterface.updateGameRecord(player.uid, 1, 0)
                    chiPengGang = []
                    chiPengGang.extend(player.chiCard)
                    chiPengGang.extend(player.pengCard)
                    chiPengGang.extend(player.gangCard)
                    playerInfo.append({"hu": 0, "card":playerCards, "chipenggangs": chiPengGang, \
                                       "chip": -curPlayerGive ,"avatar":player.avatar, "uid":player.uid, \
                                       "nickname": player.nickname, "pao": curPlayerDianPao, "hutype": "", "banker": 0 if player.uid != self._creatorID else 1 })
            # 
            player = self._hupaiPlayer
            player.updateChip(lostGive)
            hutypeShow = "硬" if self._hupaiInfo["cardType"][2] == 0 else "软"
            if self._hupaiInfo["cardType"][0] == 1:
                hutypeShow += "七对"
                if self._hupaiInfo["cardType"][1] != 0:
                    hutypeShow += "清一色"
            elif self._hupaiInfo["cardType"][1] != 0:
                hutypeShow += "清一色"
            else:
                hutypeShow += "小胡"
            #hutypeShow += ("大胡" if self._hupaiInfo["cardType"][0] == 1 or self._hupaiInfo["cardType"][1] != 0 else "小胡")
            hutypeShow += (" 自摸" if self._hupaiInfo["zimo"] else " 接炮")
            playerCards = player.cards
            playerCards.sort()
            if self._hupaiInfo["zimo"]:
                playerCards.remove(self._hupaiCard)
                playerCards.sort()
                playerCards.append(self._hupaiCard)
            chiPengGang = []
            chiPengGang.extend(player.chiCard)
            chiPengGang.extend(player.pengCard)
            chiPengGang.extend(player.gangCard)
            winnerInfo = {"hu": self._hupaiCard, "card": playerCards, "chipenggangs": chiPengGang, \
                          "chip": lostGive ,"avatar":player.avatar, "uid":player.uid, \
                          "nickname": player.nickname, "pao": 0, "hutype": hutypeShow, "banker": 0 if player.uid != self._creatorID else 1 }
            playerInfo.insert(0, winnerInfo)
            gameDataInterface.updateGameRecord(player.uid, 1, 1)
        info = {}
        info["playerInfo"] = playerInfo
        return info


    def _clearRound(self):
        super(GameRoom, self)._clearRound()
        self._laizi = -1
        self._banker = None
        self._curPlayer  = -1      # -1 未初始化 None没有玩家, Player玩家
        self._hupaiPlayer = None
        self._hupaiCard = 0
        self._canHuPlayer = []
        self._curBetCard = None
        self._hupaiInfo = None
        self._canHuPlayer = []    
        self._canStartBet = False
        self._recordPlayerAction = {}
        self._recordProcess = []
        self._recordHistory = {}
        self._curChooseAction = None
        self._isQiangGang = 0
        #self._isHandleBet = False



    def _genSnapshot(self, selfPlayer):
        old_atom = self._enter()
        snapshot = {}
        # baseInfo
        snapshot["baseRoomInfo"] = {
            "roomID": self._roomID,
            "payType": self._eachGive,
            "status": self._getSnapshotStatus(),
            "curRound": self._round,
            "allRound": self._roomMaxRound,
            "laizi": self._laizi,
            "rest": len(self._dealer.notUseCards),
            "betInfo": self._genBetInfo(selfPlayer)
        }
        players = self._playerInRoom.seatInfo
        playerInfo = {}
        for player in players:
            if player:
                playerInfo[player.uid] = self._genPlayerSnapshot(player, player.getBaseSnapshot())
        playerInfo[selfPlayer.uid]["card"] = selfPlayer.cards
        snapshot["basePlayerInfo"] = playerInfo  
        snapshot["selfInfo"] = self._genSelfInfo(selfPlayer)
        gameLog.info("player %d snapshot is: %s" % (selfPlayer.uid, str(snapshot)))
        self._exit(old_atom)
        return snapshot

    def _genPlayerSnapshot(self, player, baseInfo):
        info = baseInfo
        info["banker"] = 1 if player.uid == self._creatorID else 0
        info["zhuang"] = 1 if (self._banker and player.uid == self._banker.uid) else 0
        info["isOnline"] = player.isOnline
        #info["chi"] = player.chiCard
        #info["peng"] = player.pengCard
        #info["gang"] = player.gangCardInfo
        info["chipeng"] = 0 if player != self._curPlayer else self._whyBet
        chiPengGang = []
        chiPengGang.extend(player.chiCard)
        chiPengGang.extend(player.pengCard)
        chiPengGang.extend(player.gangCard)
        info['chipenggangs'] = chiPengGang
        info["card"] = [0] * len(player.cards)
        info["deskcard"] = player.hadBetCard
        return info

    def _genSelfInfo(self, player):
        info = {}
        info["card"] = player.cards
        info["uid"] = player.uid
        return info

    def _genBetInfo(self, selfPlayer):
        info = {}
        info["uid"] = -1 if self._curPlayer == None or self._curPlayer == -1 else self._curPlayer.uid
        #info["targettoggle"] = 0 if self._curChooseAction == None else 1
        info["actiontype"] = 0 if self._curChooseAction == None else 1
        info["targetuid"] = selfPlayer.uid if info["actiontype"] == 7 and info["uid"] == selfPlayer.uid else -1
        info["card"] = 0 if self._curBetCard == None else self._curBetCard
        info["time"] = self._timerManager.getLeftTime(self._timer)
        info["selfAction"] = {"peng":0, "chi":0, "gang":0, "hu":0} if self._curChooseAction == None else self._curChooseAction.get(selfPlayer, {"peng":0, "chi":0, "gang":0, "hu":0})
        return info

    def _playerChoosePeng(self, player, card):
        card = card[0]
        ret = judgeCanGangOrPeng(player.cards, self._curBetCard)
        if ret == 1 or ret == 3:
            player.playerBetCard(card)
            player.playerBetCard(card)
            player.addPengCard([player.uid, self._curPlayer.uid, 2, card, card])
            self._curPlayer.removeHadBetCard(card)
            self._recordProcess.append([2, player.uid, self._curPlayer.uid, [self._curBetCard]*3, card ])
            return ErrorCode.ERR_OK, False, {"target":self._curPlayer.uid}
        return ErrorCode.ERR_FAIL, None, None

    def _playerCanChoosePeng(self, player, card):
        card = card[0]
        ret = judgeCanGangOrPeng(player.cards, self._curBetCard)
        if ret == 1 or ret == 3:
            return True
        return False

    def _judgeNeedSendDissolve(self, args=None):
        super(GameRoom, self)._judgeNeedSendDissolve(args)
        if self._status != GameRoomStatus.STATUS_PLAYING:
            self._judgeNeedSendStartLessPlayerGame()
        if len(self._chooseForceStart) != 0:
            #self._msgHelper.sendPlayChooseDissolve([self._chooseDissolve, self._timerManager.getLeftTime(self._chooseDissolveTimer)])
            self._sendChooseForceStart()


    def _playerChooseGang(self, player, card):
        card = card[0]
        if player.cards.count(card) == 4:
            player.playerBetCard(card)
            player.playerBetCard(card)
            player.playerBetCard(card)
            player.playerBetCard(card)
            player.addGangCard([player.uid, self._curPlayer.uid, 13, card, card])
            player.addGangCardInfo([player.uid, self._curPlayer.uid, 13, card, card])
            self._recordProcess.append([13, player.uid, self._curPlayer.uid, [card]*4, card ])
            return ErrorCode.ERR_OK, True, {"type":13, "target":self._curPlayer.uid}
        elif self._isCardInPeng(player.pengCard, card) and player == self._curPlayer and card in player.cards:  # had pengCard
            player.playerBetCard(card) #[player.uid, self._curPlayer.uid, 12, card, card])
            player.changePengToGang(card)
            player.addGangCardInfo([player.uid, self._curPlayer.uid, 12, card, card])
            self._recordProcess.append([12, player.uid, self._curPlayer.uid, [card]*4, card ])
            return ErrorCode.ERR_OK, True, {"type": 12, "target": player.uid }
        else:
            ret = judgeCanGangOrPeng(player.cards, card)
            if ret == 2 or ret == 3:
                player.playerBetCard(card)
                player.playerBetCard(card)
                player.playerBetCard(card)
                player.addGangCard([player.uid, self._curPlayer.uid, 3, card, card])
                player.addGangCardInfo([player.uid, self._curPlayer.uid, 3, card, card])
                self._curPlayer.removeHadBetCard(card)
                self._recordProcess.append([3, player.uid, self._curPlayer.uid, [card]*4, card ])
                return ErrorCode.ERR_OK, True, {"type":3, "target":self._curPlayer.uid}
        return ErrorCode.ERR_FAIL, None, None

    def _isCardInPeng(self, pengCard, card):
        for item in pengCard:
            if item[3] == card:
                return True
        return False

    def _playerCanChooseGang(self, player, card):
        card = card[0]
        if card == self._laizi and player.cards.count(card) < 4:
            return False
        if player.cards.count(card) == 4 or self._isCardInPeng(player.pengCard, card) or judgeCanGangOrPeng(player.cards, card) == 2 or judgeCanGangOrPeng(player.cards, card) == 3:
            #ret = judgeCanGangOrPeng(player.cards, card)
            #if ret == 2 or ret == 3:
            return True
        gameLog.info("player [%d] choose Gang [%d] but cannot" %(player.uid, card))
        return False

    def _playerChooseChi(self, player, cards):
        oldCards = cards[:]
        ret = judgeCanChi(player.cards, self._curBetCard)        
        if self._curBetCard in cards:   cards.remove(self._curBetCard)
        if len(ret) != 0 and ([cards[0], cards[1]] in ret or [cards[1], cards[0]] in ret):
            player.playerBetCard(cards[0])
            player.playerBetCard(cards[1])
            cards.append(self._curBetCard)
            player.addChiCard([player.uid, self._curPlayer.uid, 1, self._curBetCard, cards[0], cards[1], cards[2]])
            self._curPlayer.removeHadBetCard(self._curBetCard)
            self._recordProcess.append([1, player.uid, self._curPlayer.uid, oldCards, self._curBetCard])
            return ErrorCode.ERR_OK, False, {"target":self._curPlayer.uid}
        return ErrorCode.ERR_FAIL, None, None

    def _playerCanChooseChi(self, player, cards):
        if player == self._curPlayer:
            return False
        cards = cards[:]
        ret = judgeCanChi(player.cards, self._curBetCard)
        if self._curBetCard in cards:   cards.remove(self._curBetCard)
        if len(ret) != 0 and ([cards[0], cards[1]] in ret or [cards[1], cards[0]] in ret):
            return True
        gameLog.info("player [%d] cannot chi [%s], judge canChi is %s" %(player.uid, str(cards), str(ret)))
        return False


    def _playerChooseHu(self, player, cards):
        if self._curPlayer == player: 
            compareCards = player.cards[:]
            if cards[0] in compareCards:
                compareCards.remove(cards[0])
            else:
                cards = [compareCards[0]]
                compareCards.remove(compareCards[0])
            ret = judgeWanneng(compareCards, cards[0], self._laizi, [player.justPengCard, player.justGangCard, player.justChiCard], True)
        else:  
            cards = [self._curBetCard]
            ret = judgeWanneng(player.cards, cards[0], self._laizi, [player.justPengCard, player.justGangCard, player.justChiCard], False)
        if ret[0] == 0:
            gameLog.info("player [%d] cannot hu card [%d]" %(player.uid, cards))
            return ErrorCode.ERR_FAIL, False, None
        self._hupaiPlayer = player
        self._oldHupaiPlayer = player
        self._hupaiCard = cards[0]
        #
        if self._isQiangGang:
            self._curPlayer.changeGangToPeng(cards[0])
        #
        if self._curPlayer == player:  # zimo
            self._curPlayer.addZimoCount()
        else:
            self._curPlayer.addDianPaoCount()
            player.addHuCount()
        #  # [胡牌的类型,是否是清一色] 类型：0 不能胡 1 七对 2 3n+2  | 0 不是清一色 1 是清一色
        huTypeSend = 14 if self._curPlayer == player else 4
        self._hupaiInfo = {"dianpao": self._curPlayer if self._curPlayer != player else None, "zimo": 1 if self._curPlayer == player else 0, "cardType": ret }
        self._recordProcess.append([huTypeSend, player.uid, self._curPlayer.uid, [self._hupaiCard], self._hupaiCard ])
        return ErrorCode.ERR_OK, True, {"target":self._curPlayer.uid, "huTypeSend": huTypeSend}

    def _playerCanChooseHu(self, player, cards):
        if self._curPlayer == player:
            compareCards = player.cards[:]
            if cards[0] in compareCards:
                compareCards.remove(cards[0])
            else:
                cards = [compareCards[0]]
                compareCards.remove(compareCards[0])
            ret = judgeWanneng(compareCards, cards[0], self._laizi, [player.justPengCard, player.justGangCard, player.justChiCard], True)
        else:
            cards = [self._curBetCard]
            compareCards = player.cards
            ret = judgeWanneng(compareCards, cards[0], self._laizi, [player.justPengCard, player.justGangCard, player.justChiCard], False)
        #ret = judgeWanneng(compareCards, cards[0], self._laizi, [player.pengCard, player.gangCard, player.chiCard])
        gameLog.info("judge can choose hu ret %s" %(str(ret),))
        return False if ret[0] == 0 else True

    def _playerChoosePass(self, player, args=None):
        # self._curChooseAction.pop(player,None)
        return ErrorCode.ERR_OK, True, {"target": self._curPlayer.uid}

    def _playerCanChoosePass(self, player, args=None):
        return True

    def _sendPlayerChooseAct(self, player, actType, cards, args=None):
        info = {}
        info["uid"] = player.uid
        info["type"] = actType
        info["card"] = cards
        info["targetuid"] = args["target"] #player.uid
        info["time"] = self._playerThinkTime
        info["operaCard"] = -1 if self._curBetCard is None else self._curBetCard
        #
        if actType == 3:
            info["type"] = args["type"]
        self._msgHelper._sendPlayerChooseAct(info)


    def _judgeHadPlayerCanAction(self, action):
        for player in self._curChooseAction:
            if self._curChooseAction[player][action] == 1:
                return True
        return False

    def _judgeBeforePlayerHu(self, player):
        """他前边的玩家是否能胡牌
        """
        needJudgeSeat = []
        curSeat = self._curPlayer.seatNo
        playerSeat = player.seatNo
        for i in range(4):
            if (curSeat + i + 1)%4 != playerSeat:
                needJudgeSeat.append((curSeat+i+1)%4)
            else:
                break
        for seatNo in needJudgeSeat:
            tmp = self._playerInRoom.getPlayerBySeatNo(seatNo)
            if tmp in self._curChooseAction and self._curChooseAction[tmp]["hu"] == 1:
                return True
        return False

    def _canFinishAction(self, player, action):
        """玩家的某个行为是否可以结束动作
        条件: 没有人比自己更优先的动作了
        # 1吃 2碰 3明杠 4放炮胡 6过,12边杠，13暗杠 14自摸
        """
        if action == 1:
            if self._judgeHadPlayerCanAction("hu") or self._judgeHadPlayerCanAction("peng") or self._judgeHadPlayerCanAction("gang"):
                return False
        elif action == 2 or action == 3:
            if self._judgeHadPlayerCanAction("hu"):
                return False
        elif action == 4:
            if self._judgeBeforePlayerHu(player):
                return False
        elif action == 6:
            # self._curChooseAction.pop(player, None)
            if len(self._curChooseAction) != 0:
                return False
        return True



    @hadInRoom
    def playerChooseAct(self, uid, info, force=False, **kwargs):
        gameLog.info("player [%d] chooseAct [%s]" %(uid, str(info)))
        player = kwargs["player"]
        actType = info["actiontype"]
        err = ErrorCode.ERR_OK
        if not self._canStartBet:
            return ErrorCode.ERR_FAIL, {"actiontype": actType , "result": ErrorCode.ERR_FAIL}
        userActType = actType
        if not (        \
                player == self._curPlayer or actType == 6 or actType == 3 or force == True or \
                (self._curChooseAction != None and (player in self._curChooseAction))):
            gameLog.info("player [%d] cannot choose action " %(player.uid,))
            return ErrorCode.ERR_FAIL, {"actiontype": actType , "result": ErrorCode.ERR_FAIL}
        gameLog.info("player[%d] action[%d]" %(player.uid, actType))
        if actType == 4 and player == self._curPlayer and self._whyBet != 0:
            gameLog.info("actType == 4 result 1")
            return ErrorCode.ERR_FAIL, {"actiontype": actType , "result": ErrorCode.ERR_FAIL}
        if actType == 6 and  player == self._curPlayer and force == False:
            return ErrorCode.ERR_FAIL, {"actiontype": actType , "result": ErrorCode.ERR_FAIL}
        if self._curChooseAction == None and (actType == 1 or actType == 2):
            gameLog.info("self._curChooseAction result 2")
            return ErrorCode.ERR_FAIL, {"actiontype": actType , "result": ErrorCode.ERR_FAIL}
        cards = info.get("cards", [])
        if not self._playerCanChooseMap[actType](player, cards):
            gameLog.info("canchoosemap is none result 4")
            return ErrorCode.ERR_FAIL, {"actiontype": actType , "result": ErrorCode.ERR_FAIL}
        else:
            if player == self._curPlayer:
                force = True
            else:
                if self._curChooseAction is None:
                    gameLog.info("self._curChooseAction result 3")
                    return ErrorCode.ERR_FAIL, {"actiontype": actType , "result": ErrorCode.ERR_FAIL}
            if self._curChooseAction != None:
                self._curChooseAction.pop(player, None)
            # log last
            if self._lastPlayerChoose is None:
                self._lastPlayerChoose = [player, actType]
            else:
                if actType != 6:
                    self._lastPlayerChoose = [player, actType]
            if force == False and not self._canFinishAction(self._lastPlayerChoose[0], self._lastPlayerChoose[1]): #self._canFinishAction(player, actType):
                gameLog.info("record player [%d] action [%s]" %(player.uid, str(info)))
                self._recordPlayerAction[player] = info
                return ErrorCode.ERR_OK, {"actiontype": actType , "result": ErrorCode.ERR_OK}
            else:
                self._recordPlayerAction[player] = info
                gameLog.info("cur recored player action is %s" %(str(self._recordPlayerAction),))
                player, actionInfo = self._judgeTimeoutGetPlayerAction()
                gameLog.info("choose action timeout, player[%d] info[%s]" %(player.uid if player != None else -1, str(actionInfo)))
                self._curChooseAction = None
                self._recordPlayerAction = {}
                self._lastPlayerChoose = None
                self._timerManager.delTimer(self._timer)
                if player != None and actionInfo != None:
                    actType = actionInfo["actiontype"]
                    cards = actionInfo.get("cards", [])
                    err, needGetOneCard, args = self._playerChooseMap[actType](player, cards)
                    if err == ErrorCode.ERR_OK:
                        sendCards = cards
                        if actType == 2:    sendCards = sendCards*3
                        elif actType == 3:  
                            sendCards = sendCards*4
                            actType = args["type"]
                        elif actType == 4:  actType = args["huTypeSend"]
                        self._sendPlayerChooseAct(player, actType, sendCards, args)
                        # 抢杠
                        if actType != 12:
                            self._channel.send([player, needGetOneCard])
                        else:
                            qiangGangInfo = self._checkPlayerAction(player, cards[0], True)
                            if len(qiangGangInfo) == 0:
                                self._channel.send([player, needGetOneCard])
                            else:
                                #self._sendPlayerBet(player, cards[0])
                                self._curBetCard = cards[0]
                                self._isQiangGang = 1
                                self._msgHelper.sendTestMsg(qiangGangInfo)
                                self._handlePlayerAction(qiangGangInfo)
                        #self._curChooseAction = None
                        #self._recordPlayerAction = {}
                    else:
                        self._channel.send([None, True])
                else:
                    if self._isQiangGang:
                        self._isQiangGang = 0
                        self._channel.send([self._curPlayer, True])
                    else:
                        self._channel.send([None, True])
        return err, {"actiontype": userActType , "result": err}

    @hadInRoom
    def playerBet(self, uid, betInfo, **kwargs):
        """玩家出牌
        """
        err = ErrorCode.ERR_FAIL
        if not self._canStartBet or self._curChooseAction != None or self._curPlayer == -1 or self._curPlayer.uid != uid or not self._canStartBet:
            return err, {}
        player = kwargs["player"]
        card = betInfo["card"]
        gameLog.info("------player %d bet   [%d]" %(uid, card) )
        if self._isHandleBet:
            return err, {}
        self._isHandleBet = True
        return self._wrapPlayerBet(player, card)
