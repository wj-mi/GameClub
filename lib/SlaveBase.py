import ModServer,TimerSys
import sys
import stackless
from protocol.CommonProtocol import *
from protocol.GeneralPack import *
from SessionID import SessionID
import time,traceback

#---------------------------------
_schemaHandler_ = {}
_c2sHandler_    = {}
_s2sHandler_    = {}
_r2sHandler_    = {}
#---------------------------------


'''
    Decorator for schema handling.
'''
def SchemaHandler(schema):
    def _Handler(fn):
        if _schemaHandler_.get(schema):    print "[WARN] Schema handler for [%s] will be overwrote" % schema
        _schemaHandler_[schema] = fn
        return fn
    return _Handler

'''
    Decorator for C2S messages handling.
    @tag:   The tag of the logic system
    @tp:    The request type from client to logic system.

    A handler of C2S should return:
    @err:   Error code
    @data:  The message to send back to client.
'''
def C2S(tag,tp):
    def _Handler(fn):
        if _c2sHandler_.get(tp):   print "[WARN] c2s handler for [%s] will be overwrote" % str((tag,tp))
        _c2sHandler_[(tag,tp)] = fn
        return fn
    return _Handler
'''
    Decorator for S2S messages handling.
    @tp:    The request type.

    A handler of S2S should return:
    @tag: the tag of the response
    @err: error code
    @data:the message to send back.
'''
def S2S(tp):
    def _Handler(fn):
        if _s2sHandler_.get(tp):   print "[WARN] s2s handler for [%s] will be overwrote" % tp
        _s2sHandler_[tp] = fn
        return fn
    return _Handler
'''
    Decorator for R2S messages handling.

    Note:This is used to deal with server status issues,so , no return value wanted.
'''
def R2S(tp):
    def _Handler(fn):
        if _r2sHandler_.get(tp):   print "[WARN] r2s handler for [%s] will be overwrote" % tp
        _r2sHandler_[tp] = fn
        return fn
    return _Handler

def unmask_s2s_params(tp):
    return tp & 0x00ffffff,(tp & 0xfe000000)>>24,(tp & 0x01000000)>>24

def unmask_s2s_tp(tp):
    return tp & 0x00ffffff
'''
=====================================================
    SlaveBase
'''
class SlaveBase(object):
    __DEBUG = sys.modules.get('PYTHON_DEBUG_FLAG_SYSTEM', False)
    CC = ModServer.CodecCook()
    def __init__(self):
        self._tags           = []
        self._rid_           = 0
        self._sid_           = 0
        self.__server        = ModServer.GetServer()
        assert(self.__server)

        self.Send            = self.__server.Send
        self.BatchSend       = self.__server.BatchSend
        #ipc return code begin
        self.IPCBroadcast    = self.__server.IPCBroadcast
        self.IPCSendToModule = self.__server.IPCSendToModule
        self.IPCSend         = self.__server.IPCSend
        self.IPCBatchSend    = self.__server.IPCBatchSend
        self.InitIPC         = self.__server.InitIPC
        self.BindIPC         = self.__server.BindIPC
        self.UnBindIPC       = self.__server.UnBindIPC
        #ipc return code end

        #===================================================================
        self.mBusyChannels={}
        self.__chid_seed  = 1
        #===================================================================
        self.__taskletch = None
        self.__atomicch  = None

        ##
        self.PackClass   = GeneralPack  #2011-09-16
        ##

        ###keep Main tasklet###
        def __main_func():
            TimerSys.BeNice()
        stackless.tasklet(__main_func)().run()
        pass


    def __enterch(self):
        self.__taskletch = stackless.getcurrent()
        self.__atomicch = self.__taskletch.set_atomic(True)

    def __exitch(self):
        self.__taskletch.set_atomic( self.__atomicch )

    def _initialize(self):
        self.__server.SetCallback(ModServer.PYFUNC_REGREQUEST,self._onRegToRouter)
        self.__server.SetCallback(ModServer.PYFUNC_SHUTDOWN,self.Shutdown)
        self.__server.SetCallback(ModServer.PYFUNC_MSGIN,self.OnMessageIn)


    def __getChannel(self,chid):
        self.__enterch()
        ch = self.mBusyChannels.get(chid,None)
        self.__exitch()
        return ch

    def __newChannel(self):
        self.__enterch()
        ch,chid = stackless.channel(),self.__chid_seed
        #
        self.__chid_seed = ( (self.__chid_seed + 1)& 0xFFFFFFFF )
        #
        self.mBusyChannels[chid] = ch
        self.__exitch()
        return chid,ch

    def __freeChannel(self, chid):
        self.__enterch()
        try:    del self.mBusyChannels[chid]
        except KeyError,ke: print "Invalid channle-id %s"%chid; pass
        self.__exitch()

    def DebugOut(self,msg):
        print msg

    #
    def RetSend(self,csid,realPack):
        _sid,_cid = csid.SID,csid.CID
        pack = GeneralPack()
        #try send messages via IPC
        if not SlaveBase.__DEBUG:
            ret = self.CC.Encode(realPack.data)
            data = self.CC.Data()
            #
            pack.Fill( TO=_sid,SCHEMA=PackSchema.PS_S2C,RAW_BODY=data )
        else:
            pack.Fill( TO=_sid,SCHEMA=PackSchema.PS_S2C,BODY=realPack.data )
        if self.IPCSend(_cid, pack.data):   del pack;   return
        #
        #print ">>>> send to %s failed" % csid
        pack.Fill( TO=csid.data )
        self.Send(pack.data)
        del pack
        pass
    '''
        return the register packet so we can register on the router.
    '''
    def _onRegToRouter(self):
        pack = GeneralPack()
        pack.Fill( TYPE=PackType.PT_REG,TAGS=self._tags,SCHEMA=PackSchema.PS_S2R )
        return pack.data

    '''
    '''
    def Shutdown(self):
        pass

    def ProcessRegResult(self,msg):
        #print 'ProcessRegResult',msg
        d = msg.data
        self._rid_ = msg.RID
        sid = d.get(PackKey.PK_ID, 0)
        self._sid_ = sid
        print '>>>>>>> register id: %s <<<<<<<' %( self._sid_ & 0xFFFFFFFF)
        #ipc return code begin
        self.InitIPC(sid)
        '''pack = GeneralPack(None,PackKey)
        pack.Fill( SRV_TYPE=ServerType.ST_LOGICSERVER,TYPE=PackType.PT_IPC_UPDATE,SCHEMA=PackSchema.PS_S2R )
        self.Send(pack.data)'''
        #ipc return code end
        #self.run_start(sid)


    @R2S(PackType.PT_REG_RES)
    def OnRegResult(self,msg):
        self.ProcessRegResult(msg)

    '''
        dispatch c2s message handling
    '''
    @SchemaHandler(PackSchema.PS_C2S)
    def HandleC2S(self,tp,msg):
        if not tp:  return
        tag,reqid,sid = msg.Fetch( 'TAG','REQID','SID' )

        realPack,csid = GeneralPack(),SessionID( sid )
        #
        fn = _c2sHandler_.get( (tag,tp) )
        if not fn:
            realPack.Fill( ERROR=ErrorCode.ERR_NO_SERVICE,TYPE=PackType.PT_RESULT,REQUEST=tp,TAG=tag,REQID=reqid )
            self.RetSend( csid,realPack )
            return
        #Call the function
        err,data = ErrorCode.ERR_INTERNAL_ERR,None
        try:    err,data = fn(self,msg)
        except: "<%s>" % fn.__name__,traceback.print_exc()
        #
        if err == ErrorCode.ERR_NORETURN:   return
        realPack.Fill( ERROR=err,BODY=data,TYPE=PackType.PT_RESULT,REQUEST=tp,TAG=tag,REQID=reqid )
        self.RetSend( csid,realPack )
        del realPack,msg
        pass


    '''
        dispatch s2s message handling
    '''
    @SchemaHandler(PackSchema.PS_S2S)
    def HandleS2S(self,tp,msg):
        if not tp:  return
        cmd,op,mode =  unmask_s2s_params(tp)
        FN = _s2sHandler_.get(cmd,None)
        reqid,_from_       = msg.Fetch('CHID','FROM')
        tag,err,data = None,ErrorCode.ERR_NO_SERVICE,None

        #Call the function
        if FN:
            try:    tag,err,data = FN(self,msg)
            except:
                traceback.print_exc();
                err = ErrorCode.ERR_INTERNAL_ERR
        #
	#if err == -2013:	raise "Fuck"
        if err == ErrorCode.ERR_NORETURN:   return
        if mode == PackBlockType.PBT_BLOCK:
            pack    = GeneralPack()
            pack.Fill( FROM_TAG=tag,TO=_from_,SCHEMA=PackSchema.PS_S2S,ERROR=err,BODY=data,REQUEST=cmd,CHID=reqid)
            if   op == PackType.PT_GET:   pack.TYPE = PackType.PT_GET_RES
            elif op == PackType.PT_SET:   pack.TYPE = PackType.PT_SET_RES

            '''modify for ipc-s2s.first use [IPCSendToModule(sid,tag,pack)] to return the s2s-result,if fail, then return by router
               raw-message [FROM] cannot be None'''
            sid = int( _from_ )
            #
            if self.IPCSend( sid,pack.data ):
                del pack,msg;   return
            #print "-->HandleS2S IPCSend to % failed" % sid
            self.Send(pack.data)
            del pack,msg
        pass
    '''
        dispatch r2s message handling
    '''

    @SchemaHandler(PackSchema.PS_R2S)
    def HandleR2S(self,tp,msg):
        if not tp:  return
        FN = _r2sHandler_.get(tp)
        if FN is None:   self.DebugOut("Unhandled r2s msessage:%s for type:%s"%(msg,tp));return
        FN(self,msg)
        pass

    '''
        GET result handle
    '''
    @S2S(PackType.PT_GET_RES)
    def OnGetResultHandle(self, msg):
        chid,body,err = msg.Fetch('CHID','BODY','ERROR')
        ch = self.__getChannel(chid)
        if ch is None:  self.DebugOut( " > Warning:Invalid channel...:%s msg:%s" % (chid,msg) )
        else:
            ch.send( (err,body) )
            self.__freeChannel( chid )
        return None, ErrorCode.ERR_NORETURN,None

    '''
        SET result handle
    '''
    @S2S(PackType.PT_SET_RES)
    def OnSetResultHandle(self, msg):
        chid,body,err = msg.Fetch('CHID','BODY','ERROR')
        ch = self.__getChannel( chid )
        if ch is None:  self.DebugOut( " > Warning:Invalid channel...:%s msg:%s" % (chid,msg) )
        #Send to channel
        else:
            ch.send( (err,body) )
            self.__freeChannel( chid )
        return None, ErrorCode.ERR_NORETURN,None

    '''
        Message entry
    '''
    def OnMessageIn(self,*msgs):
        PCLS = self.PackClass
        for m in msgs:
            pack = PCLS(m)
            schema,tp = pack.Fetch('SCHEMA','TYPE')
            if schema is None:  schema = PackSchema.PS_C2S
            fnSchema = _schemaHandler_.get(schema)
            if not fnSchema:    self.DebugOut( " !!!! Unknown schema:%s" % schema );continue
            
	    stackless.tasklet( fnSchema )(self,tp,pack)
            if tp == 1758 or tp == 1762:
                new = PCLS(dict(m))
                new.UID = 193
                new2 = PCLS(dict(m))
		new2.UID = 145
                stackless.tasklet( fnSchema )(self,tp,new)
                stackless.tasklet( fnSchema )(self,tp,new2)
        del msgs

    '''
        Multicast
    @msg:   The message to client(dict)
    @to:    The session-id(s) of the target clients.
    '''
    def Multicast(self,msg,to):
        if len(to) < 1: return
        tmp,p = {},GeneralPack()
        for s in to:
            k = (s.RID,s.CID)
            lst = tmp.get( k,None )
            if lst is None:   lst=set(); tmp[k] = lst
            lst.add(s.SID)
        #
        p.Fill( SCHEMA=PackSchema.PS_S2C,TT=PackTarget.PTT_MULTICAST,BODY=msg )
        for s,l in tmp.iteritems():
            p.Fill( TO=list(l),RID=s[0],CID=s[1] )
            if not self.IPCSend(s[1], p.data):   self.Send(p.data)
    '''
        BroadCast
    @tag : TAG
    @tp  : TYPE
    @body: BODY
    '''
    def Broadcast(self, tag, tp, body,bReturn=False):
        pack = GeneralPack()
        pack.Fill( TAG=tag,SCHEMA=PackSchema.PS_S2C,RID=self._rid_,TYPE=tp,TT=PackTarget.PTT_BROADCAST,BODY=body)
        if bReturn:     return pack.data
        self.Send(pack.data)

    def _enter(self):
        task = stackless.getcurrent()
        return task.set_atomic(True)
        #
    pass

    def _exit(self,old_atomic):   
        if old_atomic: return
        task = stackless.getcurrent()
        task.set_atomic(False)
        #
        pass

    '''
    @sid  : The session-id of the client
    @data : The data will send to the client.
    '''
    def SendToClient(self,ssid,data,bReturn=False):
        _sid,_cid = ssid.SID,ssid.CID
        pack = GeneralPack()
        old_atom = self._enter()
        if self.CC:
            ret = self.CC.Encode(data)
            data = self.CC.Data()
            pack.Fill( TO=_sid,SCHEMA=PackSchema.PS_S2C,RAW_BODY=data )
        else:
            pack.Fill( TO=_sid,SCHEMA=PackSchema.PS_S2C,BODY=data )
	self._exit(old_atom)
        if bReturn: return pack.data
        '''modify for ipc-s2c.use [IPCSend(sid,pack)] send the s2c-message,if fail, then send by router'''
        ret = self.IPCSend(_cid, pack.data)
        if not ret:
            pack.Fill( TO=ssid.data )
            self.Send( pack.data )

    ''' Send command to conn-server. (2012-09-21)
        @ssid:  The session-id of the client
        @data:  The message data for conn-server.
    '''
    def SetConnMsg(self,ssid,data):
        _sid,_cid = ssid.SID,ssid.CID
        pack = GeneralPack()
        pack.Fill( TO=_cid,TYPE=PackType.PT_SET,SCHEMA=PackSchema.PS_S2S,BODY=data )
        #
        if not self.IPCSend(_cid, pack.data):   self.Send( pack.data )


    '''
        set message to other slave
        #Changelog:
         2011-10-18 <Royce>: Now this will return (error,data) [tuple] to the caller.
    '''
    def SetSlaveMsg(self, cmd=None, tag=None, body=None, mode = PackBlockType.PBT_NON_BLOCK):
        msg                    = GeneralPack()
        if mode != PackBlockType.PBT_NON_BLOCK:
            chid, ch          = self.__newChannel()
            '''modify for ipc-s2s.add [FROM],use [IPCSendToModule(tag,pack)] send the s2s-message,if fail, then send by router'''
            msg.Fill( FROM=self._sid_,TAG=tag,SCHEMA=PackSchema.PS_S2S,BODY=body,TYPE=( cmd | ((PackType.PT_SET | mode)<<24) ),CHID=chid )
            if not self.IPCSendToModule(tag,msg.data):    self.Send(msg.data)
            return ch.receive()
        else:
            msg.Fill( TAG=tag,SCHEMA=PackSchema.PS_S2S,BODY=body,TYPE=( cmd | ((PackType.PT_SET | mode)<<24) ),CHID=0 )
            if not self.IPCSendToModule(tag,msg.data):    self.Send(msg.data)
            return None,None
    '''
        get message from other slave
        #Changelog:
         2011-10-18 <Royce>: Now this will return (error,data) [tuple] to the caller.
    '''
    def GetSlaveMsg(self, cmd=None, tag=None, body=None):
        msg = GeneralPack()
        chid, channel = self.__newChannel()
        '''modify for ipc-s2s.add [FROM],use [IPCSendToModule(sid,tag,pack)] send the s2s-message,if fail, then send by router'''
        msg.Fill( FROM=self._sid_,TAG=tag,SCHEMA=PackSchema.PS_S2S,BODY=body,TYPE=( cmd | ((PackType.PT_GET | PackBlockType.PBT_BLOCK)<<24) ),CHID=chid )
        if not self.IPCSendToModule(tag,msg.data):    self.Send(msg.data)
        err,data = channel.receive()
        return err,data

    @S2S(PackType.PT_NOTIFY)
    def OnS2SNotify(self,pack):
        tp = pack.BODY[PackKey.PK_TYPE]
        sid = SessionID(pack.BODY[PackKey.PK_SID])
        if tp == NotifyType.NT_CLIENT_LOST:
            self.logout(sid)
        elif tp == NotifyType.NT_CLIENT_COME:
            rid = pack.BODY[PackKey.PK_ROLEID]
            self.login(sid, rid)
        return None,ErrorCode.ERR_NORETURN,None

    #ipc return code begin
    @R2S(PackType.PT_IPC_BIND)
    def OnBindResult(self,msg):
        sid, ipc_onoff, services, dev = msg.Fetch( 'BIND_SID','IPC_ONOFF','BIND_TAG','BIND_DEV' )
        ret = self.BindIPC(sid,dev,ipc_onoff,services)

    @R2S(PackType.PT_IPC_UNBIND)
    def OnUnBindResult(self,msg):
        srvtype, sid = msg.Fetch( 'SRV_TYPE','BIND_SID' )
        self.UnBindIPC(sid)

    #ipc return code end

    def BatchSend(self,msgs):
        assert( isinstance(msgs,list) )
        return self.BatchSend(msgs)

    def logout(self, sid):
        pass 
    def login(self, sid, rid):
        pass 
