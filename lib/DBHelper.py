#coding:utf-8
import stackless
import Singleton
import Config
import os
import sys

DEBUG = sys.modules.get('PYTHON_DEBUG_FLAG_SYSTEM', False)

if not DEBUG:
    from DBBase import DBBase
else:
    from DBBase import DBBase

MAX_DB_CONN = 8

class DBHelper(Singleton.Singleton):
    def __init__(self,nconn=MAX_DB_CONN,CHAR_SET='utf8'):
        self._tasklet   = None
        self._atomic    = None
        self._maxconn   = nconn
        self._charset   = CHAR_SET
        #
        self._conn_pool = {}
        pass

    def __enter(self):
        self.__tasklet = stackless.getcurrent()
        self.__atomic = self.__tasklet.set_atomic(True)
	pass

    def __exit(self):
        def _to_exit():
            self.__tasklet.set_atomic( self.__atomic )
	stackless.tasklet(_to_exit)().run()
	pass

    def _initialize(self, cfg_path='./config/db.cfg'): 
        cfg = Config.Config(cfg_path)
        cfg.enter('db')
        dbhost,dbuser,dbpwd,dbname = (cfg.host,cfg.user,cfg.PASSWORD,cfg.DATABASE)
        unix_sock = cfg.unix_sock
        params = {
            'host':         dbhost,
            'unix_socket':  unix_sock,
            'user':         dbuser,
            'passwd':       dbpwd,
            'db':           dbname,
            'charset':      self._charset,
            'use_unicode':  False,
            'compress':     False
            }
        if unix_sock:   params.pop('host',None)
        else:           params.pop('unix_socket',None)
        for i in xrange(0,self._maxconn):
            db = DBBase()
            try:
                db.Connect(**params)
                ls = self._conn_pool.get(cfg_path, [])
                ls.append(db)
                self._conn_pool[cfg_path] = ls
                #self._conn_pool.append(db)
            except Exception,ex:    print "Exception occured when trying to connect to DataBase!EX:%s" % ex
        print '[DBHelper] connection count: %d'%(len(ls))

    @staticmethod
    def getInstance():
        return Singleton.getInstance(DBHelper)
    #
    def GetDefaultDB(self):
        return self.GetSpecifiedDB('./config/db.cfg')

    def GetAgentDB(self):
        return self.GetSpecifiedDB('./config/db_agent.cfg')

    def GetSpecifiedDB(self, cfg_path):
        ls = self._conn_pool.get(cfg_path, [])
        self.__enter()
        if len(ls) < 1:
            self._initialize(cfg_path)
            ls = self._conn_pool.get(cfg_path, [])
        self.__exit()

        if stackless.getcurrent() == stackless.getmain():
            return ls[0]
        idx = 2; ret = 1
        #while idx < len( self._conn_pool ):
        #    if self._conn_pool[idx].conn.waiting() < self._conn_pool[ret].conn.waiting():
        #        ret = idx
        #    idx += 1
        db = ls.pop(ret)
        ls.append(db)
        return db

