#coding:utf-8

#       Types of the packages
#
#{PK_TYPE:PT_REG}
class __PackType(object):
    __slots__ = ()
    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Only for servers
    #Register packet
    PT_REG          = 0x10  #16
    #Register result
    PT_REG_RES      = 0x11  #17

    '''Packet type for 'get info'
    type。schema朝向 。 body
    {type:PT_GET,schema:PS_S2S,body:{type:<command>,....}}
    '''
    PT_GET          = 0x20  #32
    #Result packet type for 'get info'
    PT_GET_RES      = 0x21  #33
    '''Packet type for 'set info'
    {type:PT_SET,schema:PS_S2S,body:{type:<command>,....}}
    '''
    PT_SET          = 0x22  #34
    #result for 'PT_SET'
    PT_SET_RES      = 0x23  #35

    #
    PT_RELOAD_CFG   = 0xF0  #
    '''Notify packet type
    *   Different from get/set command , when a packet send out with type : PT_NOTIFY,
    * we don't wait for the response.
    '''
    PT_NOTIFY       = 0xFF #255
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    #Heart-beat packet
    PT_HEART_BEAT   = 0x30  #48
    PT_HEART_RES    = 0x31  #49
    PT_SVR_STATUS   = 0x32  #50(server status query. S2S only.)

    #IPC-bind packet
    PT_IPC_UPDATE   = 0x40
    PT_IPC_BIND     = 0x41
    PT_IPC_UNBIND   = 0x42

    '''Connection request from client.
    {PK_TAG:TAG_CONN,PK_TYPE:0x01,PK_SCHEMA:PS_C2S,PK_UID:<uid>,PK_TOKEN:<token>}
    ctos
    '''
    PT_CONN         = 0x01  #1
    PT_CLOSE        = 0x02  #2
    PT_TIME_VERIFY  = 0x43  #2

    #=====================
    PT_APP_BASE     = 0x100 #256

    PT_APP_READY    = 0xFFFE #65534

    PT_RESULT       = 0xFFFF#65535 result

    PT_DFINE = 99

    #write to attributes is denied.
    def __setattr__(self,attr,val): raise TypeError("Attribute is readyonly")
#
#
PackType = __PackType()



##       The keys used in the packages.
#
class __PackKey(object):
    __slots__   = ()
    PK_TYPE     = 0x10  #(16)type
    PK_ID       = 0x11  #(17)id
    PK_TAG      = 0x12  #(18)tag
    PK_TAGS     = 0x13  #(19)tags
    PK_FROM     = 0x14  #(20)from
    PK_TO       = 0x15  #(21)to
    PK_SCHEMA   = 0x16  #(22)schema
    PK_BODY     = 0x17  #(23)body
    PK_ERROR    = 0x18  #(24)error
    PK_CID      = 0x19  #(25)conn-server id
    PK_RID      = 0x1A  #(26)router-server id
    PK_SID      = 0x1B  #(27)Clinet session id
    PK_UID      = 0x1C  #(28)Unique identifier.
    PK_ROLEID   = 0x1D  #(29)Identifier of role.
    PK_CHID     = 0x1E  #(30)Channel ID
    PK_NAME     = 0x1F  #
    PK_PARAM    = 0x20  #(32)Parameters.
    PK_FROM_TAG = 0x21  #(33)
    PK_RAW_BODY = 0x22  #(34)
    PK_ROOMID = 1258
    #---------------------------
    PK_SRV_TYPE = 0x30  #(48)Server type

    #-----------S2C keys--------
    PK_TT       = 0x40  #(64)Type of the target
    #---------Token generates by login server,and used by connection server-------
    PK_TOKEN    = 0x50  #(80)Token
    #-----------For ipc---------
    PK_IPC_ONOFF = 0x5F
    PK_BIND_SID = 0x60
    PK_BIND_TAG = 0x61
    PK_BIND_DEV = 0x62
    #-----------For cost record---------
    PK_COST_RECORD = 0x63
    PK_COST_ACT = 0x64
    PK_COST_EXT = 0x65
    #--------------------------------------------------
    PK_REQID    = 0xFD  #(253)The identifier of the request.
    PK_REQUEST  = 0xFE  #(254)The request this result packet is associated.
    PK_DESC     = 0xFF  #(255)The description of the error(not for all errors)
    PK_APP      = 0x100 #(256)The start value of package-key of other application.

    #write to attributes is denied.
    def __setattr__(self,attr,val): raise TypeError("Attribute is readonly")

#
#
PackKey = __PackKey()


##       The schemas used in packages.
#
class __PackSchema:
    PS_C2C      = 0x00  #client to client(in p2p mode,if a client-to-client can't deliver directly,then the connection server can help)
    PS_C2S      = 0x01  #client to server
    PS_S2C      = 0x02  #server to client
    PS_S2S      = 0x03  #server to server
    PS_S2R      = 0x06  #server to router
    PS_R2S      = 0x07  #router to server
    PS_R2R      = 0x08  #router to router

    #write to attributes is denied.
    def __setattr__(self,attr,val): raise TypeError("Attribute is readonly")

#
#
PackSchema = __PackSchema()

class _connError:
    CONN_ERR_UNDEFINED     = -1
    CONN_ERR_INVALID_TOKEN = -10
    CONN_ERR_TOKEN_TIMEOUT = -11 #token timeout 
    CONN_ERR_LOGIN_AGAIN   = -12 #login from other place or login repeatly.
    CONN_ERR_INDULGE_LIMIT = -13 # 防沉迷 主动提出
    #
    CONN_ERR_KICK          = -20 #
    #
    CONN_ERR_SERVER_FULL   = -400


    def __setattr__(self,attr,val): raise TypeError("Attribute is readonly")

ConnError = _connError()


#
# ========== Server Type

class __serverType:
    ST_UNKNOWN          = -1 #unknown server type
    ST_CONNSERVER       = 1 #connection server
    ST_LOGICSERVER      = 2 #logic server
    ST_ROUTERSERVER     = 3 #router server
    ST_LOGINSERVER      = 4 #login server
    ST_P2PSERVER        = 5 #p2p server

    def __setattr__(self,attr,val): raise TypeError("Attribute is readonly")

ServerType = __serverType()


#==================================================================================
#       Servers only

class __errorCode:
    ERR_OK             =   0     #Everything is fine.
    ERR_FAIL           =   -1    #
    ERR_NO_SERVICE     =   404   #No such service
    ERR_INTERNAL_ERR   =   500   #internal error
    ERR_NORETURN       =   65535 #No return !!!! This is used when you don't want to return package to client(or other server).
    # ERR_BASE
    ERR_BASE          = -1000
    ERR_REPEAT_NAME = ERR_BASE - 3

ErrorCode = __errorCode


class __notifyType:
    NT_CLIENT_LOST     =   0x10 #(16)Connection lost
    NT_CLIENT_COME     =   0x11 #(17)Connection established
    NT_CONN_SVR_LOST   =   0x20 #(32)Connection server left the server-group
    NT_CONN_SVR_COME   =   0x21 #(33)Connection server joined the server-group
    NT_LOGIC_SVR_LOST  =   0x30 #(48)A logic server left the server-group
    NT_LOGCI_SVR_COME  =   0x31 #(49)A logic server joined the server-group
    NT_ROUTER_SVR_COME =   0x40 #(64)A router server joined the server-group
    NT_ROUTER_SVR_LOST =   0x41 #(65)A router server left the server-group

    #write to attributes is denied.
    def __setattr__(self,attr,val): raise TypeError("Attribute is readonly")

NotifyType = __notifyType()


class __PackTargetType:
    PTT_NORMAL      = 0x0
    PTT_MULTICAST   = 0x1
    PTT_BROADCAST   = 0xF
PackTarget = __PackTargetType()



class __TagType:
    TAG_CONN            = 0x01    #
    TAG_ECHO            = 0x09    #
    TAG_STATUS          = 0x10    #
    TAG_ROLE            = 0x11    #for role release
    TAG_CLUB           = 0x13   #for item release
    TAG_TASK            = 0x12    #for task release
    TAG_MAP             = 0x15    #for map server
    TAG_CHAT            = 0x16    #for chat server
    TAG_RELATION        = 0x17    #for relation server
    TAG_SESSION         = 0x18    #for session server
    TAG_REWARD          = 0x19    #for reward server
    TAG_ACTIVITY        = 0x20    #for Activity server
    TAG_HOME            = 0x21    #for Home server
    TAG_TRADE           = 0x23    #for Trade server
    TAG_MALL            = 0x24
    TAG_RANK            = 0x25
    TAG_BULLETIN        = 0x26
    TAG_INDULGET        = 0x27
    TAG_FORCE           = 0x28
    TAG_FAMILY          = 0x29    #for Family server 41
    TAG_KNOW            = 0x2A
    ###############################
    TAG_DB              = 0xEE
    ###############################
    TAG_DAGONG          = 0xF0
    TAG_MAJIANG         = 0xF1
    TAG_SHISANZHANG     = 0xF2
    TAG_CLUB            = 0xFE
    TAG_ACCOUNT         = 0xFF
    TAG_NONAME          = 0xD3

    def __setattr__(self,attr,val): raise TypeError("Attribute is readonly")

TagType = __TagType()

class __PackBlockType:
    PBT_BLOCK       = 0x01
    PBT_NON_BLOCK   = 0x00

    def __setattr__(self,attr,val): raise TypeError("Attribute is readonly")

PackBlockType = __PackBlockType()
#==================================================================================

try:    import _debug_
except:pass


