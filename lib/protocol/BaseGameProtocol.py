# coding: utf-8
"""基本的游戏协议

此处定义的协议都是所有游戏共用的
!!!!警告: 所有的游戏协议生成的对象都必须名字相同,以Game开头
"""
from CommonProtocol import PackType,PackKey

class GamePackType:
    _BASE = PackType.PT_APP_BASE    # 256
    # S2S
    _S2S_BASE = _BASE
    S2S_GET_INDEX = _S2S_BASE + 1 
    S2S_USER_LOGIN_LOGOUT = _S2S_BASE + 2
    S2S_INDEX_IN_SERVER = _S2S_BASE + 3
    S2S_GET_PLAYER_IN_ROOM = _S2S_BASE + 4
    S2S_OPEN_CLUB_TABLE = _S2S_BASE + 5
    S2S_CLUB_TABLE_END = _S2S_BASE + 6
    _GAME_S2S_BASE = _S2S_BASE + 500

    # C2S
    _C2S_BASE = _S2S_BASE + 1000    # 1256
    C2S_CREATE_ROOM= _C2S_BASE + 1
    C2S_ENTER_ROOM = _C2S_BASE + 2
    C2S_READY      = _C2S_BASE + 3
    C2S_ONEFIGHTOTHERS = _C2S_BASE + 4
    C2S_OPT =       _C2S_BASE + 5
    C2S_SEND_AUDIO = _C2S_BASE + 6  # 1262
    C2S_NEED_HINT  = _C2S_BASE + 7
    C2S_GET_USER_INFO = _C2S_BASE + 8
    C2S_GET_USER_GPS = _C2S_BASE + 9
    C2S_GET_USER_HAD_IN_ROOM = _C2S_BASE + 10
    C2S_USER_DISSOLVE = _C2S_BASE + 11 
    C2S_LEAVE_ROOM = _C2S_BASE + 12
    C2S_GET_ALL_RECORD = _C2S_BASE + 13
    C2S_CHOOSE_ADD_ROOM_LIFE = _C2S_BASE + 14
    C2S_GET_USER_GPS_TWO = _C2S_BASE + 15
    C2S_GET_USER_GPS_THREE = _C2S_BASE + 16
    #
    _GAME_C2S_BASE = _C2S_BASE + 500
    # S2C
    _S2C_BASE = _C2S_BASE + 1000     # 2256
    S2C_PLAYER_READY   = _S2C_BASE + 1
    S2C_PLAYER_SITDOWN = _S2C_BASE + 2
    S2C_PLAYER_STANDUP = _S2C_BASE + 3
    S2C_START_ROUND = _S2C_BASE + 4
    S2C_ROUND_ACCOUNT  = _S2C_BASE + 5
    S2C_CLOSEROOM = _S2C_BASE + 6
    S2C_SEND_AUDIO = _S2C_BASE + 7
    S2C_PLAYER_CHOOSE_FIGHT = _S2C_BASE + 8
    S2C_PLAYER_FIGHT = _S2C_BASE + 9
    S2C_SEND_PUBLICCARD = _S2C_BASE + 10
    S2C_SEND_NEW_BET = _S2C_BASE + 11
    S2C_SEND_PLAYER_BET = _S2C_BASE + 12
    S2C_BET_END_ACCOUNT = _S2C_BASE + 13
    S2C_CHOOSE_DISSOLVE = _S2C_BASE + 14
    S2C_LEAVE_ROOM = _S2C_BASE + 15
    S2C_SEND_UPDATE_CHIP = _S2C_BASE + 16
    S2C_SEND_DISSOLVE_ROOM = _S2C_BASE + 17 # 2273
    S2C_SEND_USER_LOGINLOGOUT = _S2C_BASE + 18
    S2C_CHOOSE_ADD_ROOM_LIFE = _S2C_BASE + 19
    _GAME_S2C_BASE = _S2C_BASE + 500






class GamePackKey:
    _BASE  = PackKey.PK_APP + 1000 # 1256
    PK_GAMETYPE = _BASE + 1
    PK_ROOMID   = _BASE + 2
    PK_ITEMID   = _BASE + 3
    PK_SEATNO   = _BASE + 4
    PK_ROUND    = _BASE + 5
    PK_CHIP     = _BASE + 6
    PK_TIME     = _BASE + 7
    PK_LEV      = _BASE + 8
    PK_STATUS   = _BASE + 9

class GameClickReturnCode:
    TYPE_USERINFO = 0       # 返回座位上用户的信息
    TYPE_NONE     = 1       # 什么都不做
    TYPE_WAITCHIP = 2       # 需要补充筹码
    TYPE_SIT      = 3       # 坐下
    TYPE_LOSE_MONEY = 4     # 金币不足,无法进行其他操作
    TYPE_LIMIT    = 5       # 联盟买入限制

class GameErrorCode:
    _BASE = 1000    
    ROOM_HAD_FULL  = _BASE + 0    # 房间已经满了
    SHOULD_OWNER   = _BASE + 1    # 执行操作的必须是房主
    ACTION_NOT_ALLOW = _BASE + 2  # 不允许的操作
    ROOM_NO_ENOUGH_MONEY = _BASE + 3
    _GAME_ERROR_CODE_BASE = _BASE + 100


class GameRoomStatus:
    STATUS_FIGHT      = 0      # 正在进行硬牌环节
    STATUS_WAITSTART  = 1      # 但是不符合进行游戏的条件
    STATUS_PLAYING    = 2      # 房间正在游戏
    STATUS_ACCOUNT    = 3      # 正在结算
    STATUS_READY      = 4      # 准备倒计时阶段
    STATUS_CLOSE      = 5      # 房间关闭
    STATUS_IDLE       = 7      # 结算完到还没有进入下一个ready的阶段

class BankerMode:
    MODE_FIXED = 0  # 固定庄
    MODE_FIGHT = 1  # 抢庄

class BankerLimit:
    BANKER_LIMIT = 0
    BANKER_NOT_LIMIT = 1

class PlayerStatus:
    STATUS_NO_ROOM     = -1 # 玩家没有进入房间
    STATUS_WAIT_READY  = 0  # 玩家坐下但未准备
    STATUS_READY       = 1  # 玩家准备
    STATUS_NORMAL_GAME = 3  # 玩家正常游戏
    __STATUS_OTHER_BASE  = 10 # 各个不同的游戏玩家状态请从STATUS_OTHER_BASE向上加
