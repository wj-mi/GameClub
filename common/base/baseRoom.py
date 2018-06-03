# coding:utf-8

#
# 所有房间的基类
#

from gamePlayerInRoom import GamePlayerInRoom
from protocol import *
from util.gameLog import gameLog
from util.roomCollection import roomCollection
from util.timerManager import TimerManager
from gamePlayer import GamePlayer
from util.dealer import Dealer
from gameMsgHelper import GameMsgHelper
from gameCfg import GameCfg
import stackless
import gameDataInterface 
import time
from SessionID import SessionID

def hadInRoom(func):
    """检查玩家是否在房间内
    """
    def _wrapper(self, uid, *args, **kwargs):
        player = self._playerInRoom.getPlayerByUID(uid)
        if not player:
            return ErrorCode.ERR_FAIL, None
        else:
            kwargs["player"] = player
            return func(self, uid, *args, **kwargs)
    return _wrapper

def hadSit(func):
    def _wrapper(self, *args, **kwargs):
        player = kwargs["player"]
        if player.seatNo == -1:
            return GameErrorCode.SHOULD_SIT_BEFORE, None
        else:
            return func(self, *args, **kwargs)
    return _wrapper

def isOwner(func):
    def _wrapper(self, uid, *args, **kwargs):
        if uid != self._creatorID:
            return GameErrorCode.SHOULD_OWNER, None
        else:
            return func(self, uid, *args, **kwargs)
    return _wrapper


class BaseRoom(object):
    def __init__(self, createArgs):
        self._roomID = createArgs.get("roomID", createArgs.get("itemID", -1))
        self._pwd = createArgs.get("pwd")
        self._maxPlayer = createArgs.get("playerNum")
        self._roomMaxRound = createArgs.get("roundNum")
        self._locationLimit = createArgs["locationLimit"]
        self._creatorID = int(createArgs.get("creatorID", -1))
        self._slave  = createArgs.get("slave", None)
        self._round = 0
        self._timerManager = TimerManager()
        self._msgHelper = GameMsgHelper(self._slave, self)
        self._curRoundPlayer = None    
        self._dealer = Dealer()
        self._playerInRoom = GamePlayerInRoom(self)
        self._status = -1
        self.setStatus(GameRoomStatus.STATUS_WAITSTART)
        self._gameTask = None
        self._channel       = stackless.channel()          # 调度
        self._createArgs = createArgs
        self._isStart = False
        self._parent = createArgs["manager"] 
        self._roundAccountInfo = {}
        self._canChooseAddPlayer = []
        self._roomAccountPlayerInfo = []
        # dissolve
        self._isChoosingDissolve = False
        self._chooseDissolve = []
        self._chooseDissolveTimer = None
        self._firstDissolve = None
        self._hadPlayGame = False
        #
        self._creatorCost = createArgs["createCost"]
        self._eachGive = createArgs.get("eachGive", 0)
        roomCollection.addRoom(self._roomID, self)
        #
        self._testUID = []#[9001,9002]

    def __del__(self):
        gameLog.info("%s %d release" % (self.__class__.__name__, self._roomID))

    @property 
    def roomID(self):   return self._roomID

    @property 
    def round(self):    return self._round

    @property
    def status(self):   return self._status
    def setStatus(self, status):    self._status = status

    @property 
    def maxPlayer(self):    return self._maxPlayer

    @property 
    def index(self):    return self._pwd

    def _startRound(self):
        """开始一个新回合
        """
        self._isStart = True
        self._curRoundPlayer = []
        self._round += 1

    def _canStartRound(self, args={}):
        """判断是否可以开始游戏
        """
        num = len(self._playerInRoom.getSeatStatusPlayer(PlayerStatus.STATUS_READY))
        gameLog.info("room %d had ready player num: %d" %(self._roomID, num))
        return False if num  < self._maxPlayer else True


    def _sitdown(self, player, seatNo, status = PlayerStatus.STATUS_WAIT_READY, needJudge=True):
        """玩家坐下
        """
        if player.uid in self._testUID:
            status = PlayerStatus.STATUS_READY
        player.sitdown(seatNo, status)
        self._playerInRoom.sitdown(player, seatNo)
        info = self._genSitdownUserInfo(player)
        self._msgHelper.playerSitdownMsg(player.uid, seatNo, info)
        self._playerSitdownSuccess(player)
        if needJudge:   self._judgeStartRound()

            
    def _playerSitdownSuccess(self, player):
        pass


    def _genSitdownUserInfo(self, player):
        """新的玩家坐下需要通知其他玩家的信息
        """
        return player.getBaseSnapshot()#{"nickname":player.nickname, "chip":0, "a"}

    # def _standup(self, player):
    #     """玩家站起
    #     """
    #     self._playerInRoom.standup(player)
    #     gameLog.info("%s %d, player %d  standup " %(self.__class__.__name__, self._roomID, player.uid))
    #     player.standup()
    #     self._msgHelper.playerStandupMsg(player.uid)

    def _genSaveRoundAccunt(self, accountMsg):
        info = []
        playerInfo = accountMsg["playerInfo"]
        for item in playerInfo:
            info.append( {"uid": item["uid"], "nickname": item["nickname"], "chip": item["chip"]} )
        #accountMsg["playerInfo"] = info
        return info

    def _enter(self):
        task = stackless.getcurrent()
        return task.set_atomic(True)
        #
    pass

    def _exit(self,old_atomic):   
        task = stackless.getcurrent()
        task.set_atomic(old_atomic)
        #
        pass

    def _judgeStartRound(self, args={}):
        """判断是否可以开始新的回合
        """
        old_atomic = self._enter()
        if self._status != GameRoomStatus.STATUS_WAITSTART and self._status != GameRoomStatus.STATUS_ACCOUNT:
            gameLog.info("%s %d  status error, cannot check start" %(self.__class__.__name__, self._roomID))
            self._exit(old_atomic)
            return 
        if self._round >= self._roomMaxRound:
            gameLog.info("%s %d room time out!" %(self.__class__.__name__, self._roomID))
            self._closeRoom()
            self._exit(old_atomic)
            return
        if not self._canStartRound(args):
            gameLog.info("%s %d is inconformity start" %(self.__class__.__name__, self._roomID))
            #self.setStatus(GameRoomStatus.STATUS_WAITSTART)
            self._exit(old_atomic)
            return
        else:
            gameLog.info("%s %d is allow start" %(self.__class__.__name__, self._roomID))
            self.setStatus(GameRoomStatus.STATUS_PLAYING)
            if self._gameTask != None:
                self._gameTask.remove()
                self._gameTask.kill()
            self._exit(old_atomic)
            self._gameTask = stackless.tasklet(self._startRound)()


    def _closeRoom(self, isDissolve=False):
        """房间需要关闭
        """
        self._isClosing = True
        isDissolve = False if self._round > 0 else True
        playerInfo = self._roomAccount(isDissolve)
        self._roomAccountPlayerInfo = playerInfo
        #if not self._isStart = 
        sendIsDissolve = 1 if not self._isStart else 0
        self._isStart = False
        sendInfo = { "playerInfo": playerInfo, "isDissolve": sendIsDissolve, "creatorID":self._creatorID }
        self._sendCloseInfo = sendInfo
        self._msgHelper.closeRoom(sendInfo)
        #
        # 
        if GameCfg.canAddRoomLife == 0 or isDissolve:
            self._realClose(playerInfo, isDissolve)
        else:
            self._genCanAddRoomLifeInfo(playerInfo, isDissolve)
            

    def _realClose(self, playerInfo, isDissolve):
        self._parent.roomClose(self, playerInfo)
        gameDataInterface.closeRoom(self._roomID, int(time.time()), 3 if isDissolve else 2, str(self._genSaveRoomRoundInfo(playerInfo)), self._round)
        #
        if self._round > 0:
            uids = self._playerInRoom.historyPlayer.keys()
            self._updateHadJoinRoom(uids, self._roomID)
        # 
        self._clearTimer()
        self._clearRef()

    def _genCanAddRoomLifeInfo(self, playerInfo, isDissolve):
        self._canChooseAddPlayer = self._playerInRoom.getPlayerInSeat()
        self._creatorID = -1
        self._timer = self._timerManager.addTimer(GameCfg.cfg_AddRoomLifeTime, self, "_afterAddRoomLifeTime", None)

    def _afterAddRoomLifeTime(self, args=None):
        self._realClose(self._roomAccountPlayerInfo, False)

    def _genSaveRoomRoundInfo(self, playerInfo):
        info = []
        for item in playerInfo:
            info.append( {"uid": item["uid"], "nickname": item["nickname"], "chip": item["chip"]} )
        return info

    def _updateHadJoinRoom(self, uids, roomID):
        for uid in uids:
            err, data = gameDataInterface.getHadJoinRoom(uid)
            if err != ErrorCode.ERR_OK:
                data = []
            else:
                if data is None or len(data) == 0:
                    data = []
                else:
                    data = eval(data)
            data.insert(0, [roomID, GameCfg.gameType])
            gameDataInterface.upadteHadJoinRoom(uid, str(data[0:500]))


    def _clearTimer(self):
        self._timerManager.unRegTimer()

    def _clearRef(self):
        self._parent = None
        roomCollection.delRoom(self._roomID)
        self._timer = None
        self._slave = None
        self._playerInRoom = None
        self._msgHelper = None
        self._curRoundPlayer = None
        self._history = None
        self._timerManager = None

    def _roomAccount(self, isDissolve):
        """房间结算
        """
        allPlayers = self._playerInRoom.historyPlayer
        playerInfo = []
        for playerID in allPlayers:
            player = allPlayers[playerID]
            info = player.roomAccount()
            playerInfo.append(info)
        return playerInfo

    def _roundAccount(self):
        """一个回合的结算
        """
        if self._round == 1:
            if self._eachGive == 0:
                gameDataInterface.updatePlayerRoomCard(self._creatorID, -self._creatorCost, int(time.time()), 0, self._roomID, self._pwd)
            else:
                eachGive =  self._creatorCost / int(self._maxPlayer)
                for player in self._curRoundPlayer:
                    gameDataInterface.updatePlayerRoomCard(player.uid, -eachGive, int(time.time()), 0, self._roomID, self._pwd)


    def _gameAccount(self):
        """
        """
        pass 

    def _getAccountTime(self):
        """得到房间结算需要表现的时间
        """
        return GameCfg.cfg_ShowAccountTime_MS
        

    def _afterAccount(self, args=None):
        """结算动作表现结束后进行的操作
        """
        #self.setStatus(GameRoomStatus.STATUS_WA)
        self._clearRound()
        self._playerInRoom.clearRound()
        # force ready
        #players = self._playerInRoom.getPlayerInSeat()
        #for player in players:
        #    player.setStatus(PlayerStatus.STATUS_READY)
        # 
        self._judgeStartRound()

    def _getSnapshotStatus(self):
        if self._status == GameRoomStatus.STATUS_WAITSTART and self._isStart:
            return GameRoomStatus.STATUS_ACCOUNT
        return self._status

    def _clearRound(self):
        players = self._curRoundPlayer 
        for player in players:
            player.clearRound()
            if player.uid in self._testUID:
                player.setStatus(PlayerStatus.STATUS_READY)

    def _waitTime(self, time):
        """流程在这里暂停一段时间,用于需要阻塞函数返回的逻辑中
        """
        self._timerManager.addTimer( int(time), self, "_waitTimeout", None) 
        self._channel.receive()

    def _waitTimeout(self, args=None):
        self._channel.send(0)

    def _waitThenSend(self, time):
        """用于不需要阻塞函数返回的逻辑中，函数照常返回，但是整个游戏流程会阻塞，需要调用函数的地方receive其发出的信号
        """
        self._timerManager.addTimer( int(time), self, "_waitTimeout", None) 




    def _genSnapshot(self, player):
        """玩家进入房间时候，生成房间快照给玩家来展现房间当前的状态
        """
        snapshot = {}
        return snapshot

    def c2s_enterRoom(self, uid, sid, args=None):
        gameLog.info("player %d enter %s %d" %(uid, self.__class__.__name__, self._roomID))
        player = self._playerInRoom.getHistoryPlayerByUID(uid)
        # 如果不在房间，创建一个新的玩家
        needJudge = False
        if not player:
            if not self._checkRoomCard(uid):
                return GameErrorCode.ROOM_NO_ENOUGH_MONEY, None
            if len(self._playerInRoom.getPlayerInSeat()) >= self._maxPlayer:
                return GameErrorCode.ROOM_HAD_FULL, {}
            seatNo = self._playerInRoom.findNoUseSeatNo()
            if seatNo == -1:
                return GameErrorCode.ROOM_HAD_FULL, {}
            else:
                player = GamePlayer(uid) 
                self._playerInRoom.enterRoom(player)
                player.enterRoom(self._roomID)
                # 玩家坐下
                self._sitdown(player, seatNo, PlayerStatus.STATUS_WAIT_READY, False)
                #needJudge = True
        # 进入房间进行处理
        self._playerInRoom.enterRoom(player)
        #
        
        #print "----- plaeyr set sid ", sid
        oldSid = player.sid
        player.setSid(sid)
        #gameLog.error("set sid enter room %d  %s" %(uid, str(SessionID(sid))))
        gameLog.error("[%d] enter room %d, old sid %s  new sid %s" %(uid, self._roomID, str(SessionID(oldSid)), str(SessionID(sid))))
        gameLog.error("room %d now has player %s" %(self._roomID, str([(item.uid,str(SessionID(item.sid))) for item in self._playerInRoom.getPlayerInSeat()])),)
        #
        #
        snapshot = self._genSnapshot(player)
        if needJudge: self._judgeStartRound()
        #if len(self._chooseDissolve) != 0: 
            #self._msgHelper.sendPlayChooseDissolve([self._chooseDissolve, self._timerManager.getLeftTime(self._chooseDissolveTimer)])
        #    self._sendChooseDissolveRoom()
        #
        self._timerManager.addTimer( int(1000), self, "_judgeNeedSendDissolve", None) 
        return ErrorCode.ERR_OK, snapshot

    def _judgeNeedSendDissolve(self, args=None):
        if len(self._chooseDissolve) != 0: 
            #self._msgHelper.sendPlayChooseDissolve([self._chooseDissolve, self._timerManager.getLeftTime(self._chooseDissolveTimer)])
            self._sendChooseDissolveRoom()
        

    def _checkRoomCard(self, uid):
        """一个回合的结算
        """
        if self._eachGive == 0:  
            return True
            # gameDataInterface.updatePlayerRoomCard(self._creatorID, self._creatorCost)
        else:
            eachGive = self._creatorCost / int(self._maxPlayer)
            err, data = gameDataInterface.getPlayerRoomCard(uid)
            gameLog.info("getPlayerRoomCard, err[%d], ret [%s]" %(err, str(data)))
            if err != ErrorCode.ERR_OK or data < eachGive:
                return False
            return True

    @hadInRoom    
    def playerReady(self, uid, opt=1,**kwargs):
        """玩家准备/取消准备
        """
        player = kwargs["player"]
        if self._status != GameRoomStatus.STATUS_PLAYING:
            self._msgHelper.sendPlayerReady(uid, opt)
        if opt == 1:
            #self.userLoginLogout(uid, 0)
            if player.status == PlayerStatus.STATUS_WAIT_READY:
                player.setStatus(PlayerStatus.STATUS_READY)
            self._judgeStartRound()
        else:
            player.setStatus(PlayerStatus.STATUS_WAIT_READY)
        return ErrorCode.ERR_OK, None

    @hadInRoom
    def playerLeaveRoom(self, uid, **kwargs):
        old_atomic = self._enter()
        player = kwargs["player"]
        if self._isStart or self._status == GameRoomStatus.STATUS_PLAYING:
            self._exit(old_atomic)
            return ErrorCode.ERR_FAIL, None
        if uid == self._creatorID:
            self._closeRoom(True)
            self._exit(old_atomic)
            return ErrorCode.ERR_OK, None
        else:
            self._msgHelper.playerLeaveMsg(uid)
            self._playerInRoom.leaveRoom(player)
            self._playerLeaveSuccess(player)
            self._exit(old_atomic)
            return ErrorCode.ERR_OK, None

    def _playerLeaveSuccess(self, player):
        pass

################### dissolve ####################
    @hadInRoom
    def chooseDissolve(self, uid, choose, **kwargs):
        return self._playerChooseDissolve(kwargs["player"], choose)
        # 0 不解散  1 解散
    def _playerChooseDissolve(self, player, choose):
        if not self._isStart and choose == 0:
            self._closeRoom(True)
            return ErrorCode.ERR_FAIL, 0
        if len(self._chooseDissolve) == 0:
            self._firstDissolve = player
            players = [ tmpplayer for tmpplayer in self._playerInRoom.seatInfo if tmpplayer ]
            for tmpplayer in players:
                info = {"uid": tmpplayer.uid, "choose": -1, "avatar": tmpplayer.avatar, "nickname": tmpplayer.nickname}
                self._chooseDissolve.append(info)
        if self._playerHadChooseDissolve(player):
            return ErrorCode.ERR_FAIL, {}
        for item in self._chooseDissolve:
            if item["uid"] == player.uid:
                item["choose"] = choose
        if self._chooseDissolveTimer is None:
            self._chooseDissolveTimer = self._timerManager.addTimer(60000, self, "_chooseDissolveTimeout", None)
        #self._msgHelper.sendPlayChooseDissolve([self._chooseDissolve, self._timerManager.getLeftTime(self._chooseDissolveTimer)])
        self._sendChooseDissolveRoom()
        self._checkDissolveRoom()
        return ErrorCode.ERR_OK, 0

    def _chooseDissolveTimeout(self, args=None):
        self._chooseDissolveTimer = None
        for item in self._chooseDissolve:
            if item["choose"] == -1:
                item["choose"] = 1
        self._sendChooseDissolveRoom()
        #self._msgHelper.sendPlayChooseDissolve([self._chooseDissolve, self._timerManager.getLeftTime(self._chooseDissolveTimer)])
        self._checkDissolveRoom()

    def _findNotChooseDissolvePlayer(self):
        playerUIDs = [ player.uid for player in self._playerInRoom.seatInfo if player ]
        hadChoose = [ item["uid"] for item in self._chooseDissolve ]
        for uid in hadChoose:
            if uid in playerUIDs:
                playerUIDs.remove(uid)
        return playerUIDs

    def _checkDissolveRoom(self):
        for item in self._chooseDissolve:
            if item["choose"] == 0:
                self._msgHelper.sendDissolveRoom({"success":0})
                self._chooseDissolve = []
                self._firstDissolve = None
                self._isChoosingDissolve = False
                self._timerManager.delTimer(self._chooseDissolveTimer)
                self._chooseDissolveTimer = None
                return
        for item in self._chooseDissolve:
            if item['choose'] == -1:
                return 
        self._isChoosingDissolve = False
        self._timerManager.delTimer(self._chooseDissolveTimer)
        self._chooseDissolveTimer = None
        self._chooseDissolve = []
        #for item in self._chooseDissolve:
        #    if item["choose"] == 0:
        #       self._msgHelper.sendDissolveRoom({"success":0})
        #        self._chooseDissolve = []
        #        self._firstDissolve = None
        #        return
        self._msgHelper.sendDissolveRoom({"success":1})
        if self._status == GameRoomStatus.STATUS_PLAYING:
            self._round -= 1
        self._closeRoom(True)

    def _playerHadChooseDissolve(self, player):
        for item in self._chooseDissolve:
            if player.uid == item["uid"] and item["choose"] != -1:
                return True
        return False

    def _sendChooseDissolveRoom(self):
        self._msgHelper.sendPlayChooseDissolve({"firstChoose": {"nickname": self._firstDissolve.nickname, "uid": self._firstDissolve.uid}, "chooseInfo":self._chooseDissolve, "leftTime": 0 if self._chooseDissolveTimer is None else self._timerManager.getLeftTime(self._chooseDissolveTimer)})


#######################################################3

    @hadInRoom
    def sendAudio(self, uid, info, *args, **kwargs):
        """发送语音
        """
        player = kwargs["player"]
        self._msgHelper.sendPlayerAudio(info)
        return ErrorCode.ERR_OK, {}

    def getPlayerGPS(self):
        players = self._playerInRoom.allPlayer
        info = {}
        for uid in players:
            player = self._playerInRoom.getPlayerByUID(uid)
            err, ret = gameDataInterface.getUserGPS(uid)
            info[player.uid] = [str(0),str(0), "已掉线"] if err != ErrorCode.ERR_OK else [str(ret["GPS_X"]), str(ret["GPS_Y"]), ret["IP"]]
        return ErrorCode.ERR_OK, info

    def isPlayerInRoom(self, uid):
        return True if self._playerInRoom.getPlayerByUID(uid) else False

    def userLoginLogout(self, uid, status):
        player = self._playerInRoom.getPlayerByUID(uid) 
        if player:
            #self._msgHelper.sendUserLoginLogout(uid, status)
            player.setOnline(status)
            if status == 1:
                gameLog.error("room [%d] player [%d] clear sid, old sid is [%s]" %(self._pwd, player.uid, str(SessionID(player.sid))))
                player.clearSid()
            self._msgHelper.sendUserLoginLogout(uid, status)


    @hadInRoom
    def playerChooseAddRoomLife(self, uid, choose, **kwargs):
        """
        """
        player = kwargs["player"]
        if player not in self._canChooseAddPlayer:
            return ErrorCode.ERR_OK, choose
        if choose == 1:
            err, data = gameDataInterface.getPlayerRoomCard(uid)
            if err != ErrorCode.ERR_OK or data < self._creatorCost:
                return ErrorCode.ERR_FAIL, choose
            gameDataInterface.updatePlayerRoomCard(uid, -self._creatorCost, int(time.time()), 0, self._roomID, self._pwd)
            self._timerManager.delTimer(self._timer)
            self._canChooseAddPlayer = []
            self._round = 0
            self._creatorID = uid
            self._status = GameRoomStatus.STATUS_WAITSTART
            #
            allSeatPlayer = self._playerInRoom.getPlayerInSeat()
            self._playerInRoom.reInit()
            for tmp in allSeatPlayer:
                tmp.reInit()
            #
            #self._roomMaxRound += self._roomMaxRound
            self._msgHelper.sendAddRoomLife({"uid":uid, "nickname":player.nickname})
            self._afterAccount()
        else:
            self._canChooseAddPlayer.remove(player)
            self.playerLeaveRoom(uid)
            if len(self._canChooseAddPlayer) == 0:
                self._afterAddRoomLifeTime()
        return ErrorCode.ERR_OK, choose
