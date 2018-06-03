#coding:utf-8
import ModServer,TimerSys,stackless
gServer = ModServer.GetServer()
from SessionID import SessionID
from DBHelper import DBHelper
from protocol.CommonProtocol import ConnError
import hashlib
import types
import base64



import sys 
sys.path.append("./scripts/common")
sys.path.append("./scripts/common/util")
import gameDataInterface
import time
import re

#gameDataInterface.clearOnlineInfo()

#========================================================
#
DB = None
SESSION_TABLE = {}
#
def get_db():
    global DB
    if DB is None:
        DB = DBHelper.getInstance().GetDefaultDB()
    return DB

def get_user_old_sid(uid):
    db = get_db()
    res = res = db.Call('get_online_sid',(uid,))
    if not res:
        return None
    else:
        return res[0]['sid']

def filter_emoji(text,restr=''):
    '''''
    过滤表情
    '''
    try:
        text = unicode(text,"utf-8")
    except:
        pass
    try:
        highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return highpoints.sub(u'',text)


#
def do_check(sid,token,ip):
    #db = get_db()
    #
    ip = ip.split(":")[0]
    if token["type"] == 1:
        nickname = filter_emoji(token['nickname'])#.decode("utf8") #.encode("utf8")
        gender = token['sex']
        avatar = token.get('headimgurl',"")
        wx_id = token["unionid"]
        #openid = token["openid"]
        gps_x = token.get("gps_x", '0')
        gps_y = token.get("gps_y", '0')
        res = None
        # 其他地方有登陆
        err, res = gameDataInterface.userLogin(wx_id, str(nickname), gender, avatar)  #db.Call("user_login_in", (wx_id, nickname, gender, avatar))
        print "--------------------------------- do check   ", res
	if not res:
            return None,-1, None
        uid = res['uid']
        if uid:
            old_sid = get_user_old_sid(uid)
            phoneName = token.get("mobilePhone", 0)
            if phoneName == 0:
                phoneName = "unKnow"
            elif phoneName == 1:
                phoneName = "Android"
            elif phoneName == 2:
                phoneName = "IOS"
            #gameDataInterface.login_update_online_info(uid, ip, gps_x, gps_y, phoneName, time.time(), str(sid))
            if res["new_player"]:
                gameDataInterface.update_user_agent(uid, int(time.time()))
            return old_sid,uid, (uid, ip, gps_x, gps_y, phoneName, time.time(), str(sid))
        else:
            return None,-2, None
    else:
        uid = token["uid"]
        gps_x = token.get("gps_x", '-1')
        gps_y = token.get("gps_y", '-1')
        gameDataInterface.login_update_online_info(uid, ip, gps_x, gps_y, token.get("mobilePhone", "0"))
        return None, int(token["uid"]), None
        
#
def OnVerify(*args):
    for m in args:
        def _fCheck(m):
            s,token,host = m
            sid = SessionID(s)            
            #token = '{"nickname": "中", "type": 1, "headimgurl": "http://www.baidu.com", "sex": 1, "unionid":"1345678" }'
            #print "Verify--------->:",sid,token,host
            ### test ####
            # userid = 123445
            # global SESSION_TABLE
            # SESSION_TABLE[str(sid)] = userid
            # gServer.ClientAuthorized(sid.SID,userid)
            # return 
            ###  
            params = eval(token.strip())
            print "player info ", params
            #  验证
            old_sid,ret, update = do_check(sid,params,host)
            #print "--------+++ ret ", ret
            if ret <= 0:
                gServer.Close(sid.SID,ConnError.CONN_ERR_INVALID_TOKEN)
                return 
            else:   # 关闭旧的SID
                checkRet, data = gameDataInterface.getSIDInfo(str(sid))
                if checkRet == 0 and data is not None and data["uid"] != ret:
                    #gServer.Close(sid.SID,ConnError.CONN_ERR_INVALID_TOKEN)
                    gServer.CloseExists(sid.data,ConnError.CONN_ERR_LOGIN_AGAIN)
                    return
                if old_sid:
                    osid = SessionID()
                    osid.fromStr(old_sid)
                    # gate
                    gServer.CloseExists(osid.data,ConnError.CONN_ERR_LOGIN_AGAIN)
                    # just one
                    #gServer.Close(osid.SID,ConnError.CONN_ERR_LOGIN_AGAIN)
                gameDataInterface.login_update_online_info(*update)
            userid = ret
            global SESSION_TABLE
            SESSION_TABLE[str(sid)] = userid
            gServer.ClientAuthorized(sid.SID,userid)
        stackless.tasklet(_fCheck)(m)

def OnSessLost(sid):
    s = SessionID(sid)
    #print "----------SessionLost:",s
    userid = SESSION_TABLE.pop(str(s),-1)
    #gameDataInterface.logout_update_online_info(userid, str(s))
    return 

gServer.SetVerifyFunc(OnVerify)
gServer.SetLostFunc(OnSessLost)
