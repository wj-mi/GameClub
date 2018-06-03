#coding:utf-8   
'''
    Based on the original MySQLdb.connections.Connection
    #
    IMPORTANT:
        This should be used with the server processes which has 'EventMgr' module,
    also stackless python is required for the microthreads.
    
                                Royce(2012-04-14)
'''
import TimerSys,EventMgr,stackless,sys,traceback
import cursors
from _mysql_exceptions import Warning, Error, InterfaceError, DataError, \
     DatabaseError, OperationalError, IntegrityError, InternalError, \
     NotSupportedError, ProgrammingError
import types, _mysql
from weakref import proxy
import re,time


def defaulterrorhandler(connection, cursor, errorclass, errorvalue):
    """

    If cursor is not None, (errorclass, errorvalue) is appended to
    cursor.messages; otherwise it is appended to
    connection.messages. Then errorclass is raised with errorvalue as
    the value.

    You can override this with your own error handler by assigning it
    to the instance.

    """
    error = errorclass, errorvalue
    if cursor:  cursor.messages.append(error)
    else:   connection.messages.append(error)
    #Unrgister event..
    if not connection.open: 
        EventMgr.UnregEvent(connection.fd)
    #----
    if connection._query_channel.balance < 0:
        del cursor,connection
        connection._query_channel.send_exception( errorclass, errorvalue )
    else:
        del cursor,connection    
        raise errorclass, errorvalue   
    pass
    

re_numeric_part = re.compile(r"^(\d+)")

def numeric_part(s):
    """Returns the leading numeric part of a string.
    
    >>> numeric_part("20-alpha")
    20
    >>> numeric_part("foo")
    >>> numeric_part("16b")
    16
    """
    m = re_numeric_part.match(s)
    if m:   return int(m.group(1))
    return None


class Connection(_mysql.connection):
    """MySQL Database Connection Object"""
    default_cursor = cursors.Cursor
    def __init__(self, *args, **kwargs):
        """
        Create a connection to the database. It is strongly recommended
        that you only use keyword parameters. Consult the MySQL C API
        documentation for more information.
        #--------------------------------------------------------------------------------------
        host:               string, host to connect
        user:               string, user to connect as
        passwd:             string, password to use
        db:                 string, database to use
        port:               integer, TCP/IP port to connect to
        unix_socket:        string, location of unix_socket to use
        conv:               conversion dictionary, see MySQLdb.converters
        connect_timeout:    number of seconds to wait before the connection attempt fails.
        compress:           if set, compression is enabled
        named_pipe:         if set, a named pipe is used to connect (Windows only)
        init_command:       command which is run once the connection is created
        read_default_file:  file from which default client values are read
        read_default_group: configuration group to use from the default file
        cursorclass:        class object, used to create cursors (keyword only)
        use_unicode:        If True, text-like columns are returned as unicode objects
                            using the connection's character set.  Otherwise, text-like
                            columns are returned as strings.  columns are returned as
                            normal strings. Unicode objects will always be encoded to
                            the connection's character set regardless of this setting.
        
        charset:            If supplied, the connection character set will be changed
                            to this character set (MySQL-4.1 and newer). This implies
                            use_unicode=True.

        sql_mode:           If supplied, the session SQL mode will be changed to this
                            setting (MySQL-4.1 and newer). For more details and legal
                            values, see the MySQL documentation.
          
        client_flag:        integer, flags to use or 0 (see MySQL docs or constants/CLIENTS.py)

        ssl:                dictionary or mapping, contains SSL connection parameters;
                            see the MySQL documentation for more details
                            (mysql_ssl_set()).  If this is set, and the client does not
                            support SSL, NotSupportedError will be raised.

        local_infile:       integer, non-zero enables LOAD LOCAL INFILE; zero disables
        #--------------------------------------------------------------------------------------
        
        There are a number of undocumented, non-standard methods. See the
        documentation for the MySQL C API for some hints on what they do.
        """
        from constants import CLIENT, FIELD_TYPE
        from converters import conversions

        conv,kwargs2 = conversions,kwargs.copy()
        
        if kwargs.has_key('conv'):  conv = kwargs['conv']

        conv2 = {}
        for k, v in conv.items():
            if isinstance(k, int) and isinstance(v, list):
                conv2[k] = v[:]
            else:   conv2[k] = v
        kwargs2['conv'] = conv2

        self.cursorclass = kwargs2.pop('cursorclass', self.default_cursor)
        charset = kwargs2.pop('charset', '')

        if charset:     use_unicode = True
        else:           use_unicode = False
        
        use_unicode     = kwargs2.pop('use_unicode', use_unicode)
        sql_mode        = kwargs2.pop('sql_mode', '')
        client_version  = tuple([ numeric_part(n) for n in _mysql.get_client_info().split('.')[:2] ])
        #
        client_flag     = kwargs.get('client_flag', 0)
        if client_version >= (4, 1):    client_flag |= CLIENT.MULTI_STATEMENTS
        if client_version >= (5, 0):    client_flag |= CLIENT.MULTI_RESULTS
        kwargs2['client_flag'] = client_flag


        #
        #
        super(Connection, self).__init__(*args, **kwargs2)
        self.encoders = dict([ (k, v) for k, v in conv.items()  if type(k) is not int ])
        
        self._server_version = tuple([ numeric_part(n) for n in self.get_server_info().split('.')[:2] ])

        db = proxy(self)
        def _get_string_literal():
            def string_literal(obj, dummy=None):
                return db.string_literal(obj)
            return string_literal

        def _get_unicode_literal():
            def unicode_literal(u, dummy=None):
                return db.literal(u.encode(unicode_literal.charset))
            return unicode_literal

        def _get_string_decoder():
            def string_decoder(s):
                return s.decode(string_decoder.charset)
            return string_decoder
        
        string_literal       = _get_string_literal()
        self.unicode_literal = unicode_literal = _get_unicode_literal()
        self.string_decoder  = string_decoder  = _get_string_decoder()
        #--------charset
        if not charset:     charset = self.character_set_name()
        self.set_character_set(charset)
        #--------sql-mode
        if sql_mode:    self.set_sql_mode(sql_mode)

        if use_unicode:
            self.converter[FIELD_TYPE.STRING].append((None, string_decoder))
            self.converter[FIELD_TYPE.VAR_STRING].append((None, string_decoder))
            self.converter[FIELD_TYPE.VARCHAR].append((None, string_decoder))
            self.converter[FIELD_TYPE.BLOB].append((None, string_decoder))

        self.encoders[types.StringType] = string_literal
        self.encoders[types.UnicodeType] = unicode_literal
        self._transactional = self.server_capabilities & CLIENT.TRANSACTIONS
        
        # PEP-249 requires autocommit to be initially off
        if self._transactional:     self.autocommit(False)
        self.messages = []
        
        #------------------------------------------------Royce
        #
        self._orig_query    = super(Connection,self).query
        self.query          = self._async_query
        #
        self._orig_ping     = super(Connection,self).ping
        self.ping           = self._async_ping
        self._myfd          = self.fd
        #
        self._wait_channel  = stackless.channel()
        self._wait_channel.preference = 1
        self._query_channel = stackless.channel()
        self._release_wait(0,bInitial = True)
        self._waitings      = {}
        #EventMgr.RegEvent( self._myfd,EventMgr.EVO_READ | EventMgr.EVO_PERSIST,self._event_cb,None )
        #
        #------------------------------------------------------
        
    def cursor(self, cursorclass=None):
        """

        Create a cursor on which queries may be performed. The
        optional cursorclass parameter is used to create the
        Cursor. By default, self.cursorclass=cursors.Cursor is
        used.

        """
        cursor = (cursorclass or self.cursorclass)(self)
        cursor._do_get_result   = types.MethodType(Connection._cursor_do_get_result,proxy(cursor),cursorclass)
        cursor._post_get_result = types.MethodType(Connection._cursor_post_get_result,proxy(cursor),cursorclass)
        return cursor

    def __enter__(self): return self.cursor()
    
    def __exit__(self, exc, value, tb):
        if exc:     self.rollback()
        else:       self.commit()
            
            
    def __del__(self):
        EventMgr.UnregEvent(self._myfd)
    
    
    def literal(self, o):
        """

        If o is a single object, returns an SQL literal as a string.
        If o is a non-string sequence, the items of the sequence are
        converted and returned as a sequence.

        Non-standard. For internal use; do not use this in your
        applications.

        """
        return self.escape(o, self.encoders)

    def begin(self):
        """Explicitly begin a connection. Non-standard.
        DEPRECATED: Will be removed in 1.3.
        Use an SQL BEGIN statement instead."""
        from warnings import warn
        warn("begin() is non-standard and will be removed in 1.3",DeprecationWarning, 2)
        self._orig_query("BEGIN")
        r = self.store_result()
        res = r.fetch_row(0)
        print "begin result:",res
        
        
    if not hasattr(_mysql.connection, 'warning_count'):
        def warning_count(self):
            """Return the number of warnings generated from the
            last query. This is derived from the info() method."""
            from string import atoi
            info = self.info()
            if info:    return atoi(info.split()[-1])
            else:       return 0

    def set_character_set(self, charset):
        """Set the connection character set to charset. The character
        set can only be changed in MySQL-4.1 and newer. If you try
        to change the character set from the current value in an
        older version, NotSupportedError will be raised."""
        if self.character_set_name() != charset:
            try:
                super(Connection, self).set_character_set(charset)
            except AttributeError:
                if self._server_version < (4, 1):
                    raise NotSupportedError("server is too old to set charset")
                self._orig_query('SET NAMES %s' % charset)
                r = self.store_result()
                res = r.fetch_row(0)
                print "set_character_set result:",res
        self.string_decoder.charset = charset
        self.unicode_literal.charset = charset

    def set_sql_mode(self, sql_mode):
        """Set the connection sql_mode. See MySQL documentation for
        legal values."""
        if self._server_version < (4, 1):
            raise NotSupportedError("server is too old to set sql_mode")
        self._orig_query("SET SESSION sql_mode='%s'" % sql_mode)
        r = self.store_result()
        res = r.fetch_row(0)
        print "set_sql_mode result:",res
        
    def show_warnings(self):
        """Return detailed information about warnings as a
        sequence of tuples of (Level, Code, Message). This
        is only supported in MySQL-4.1 and up. If your server
        is an earlier version, an empty sequence is returned."""
        if self._server_version < (4,1): return ()
        self._orig_query("SHOW WARNINGS")
        r = self.store_result()
        warnings = r.fetch_row(0)
        print "show_warnings result:",warnings
        return warnings
        
    #=====================================================
    def _release_wait(self,_id,err=0,bInitial = False):
        def _f():
            self._wait_channel.send(err)
            pass
        #
        if bInitial:    stackless.tasklet(_f)(); return 
        if self._waitings.pop(_id,False):
            stackless.tasklet(_f)()
        
    
    def waiting(self):  return - self._wait_channel.balance
    
    def _wait(self):
        self._wait_channel.receive()
        pass
            
    def _async_ping(self,bReconnect=0):
        def do_ping():
            self._wait()
            #
            cur_task = stackless.getcurrent()
            qid = id(cur_task)
            self._waitings[qid] = True
            try:        self._orig_ping(bReconnect)
            except Exception,ex:    print "[async_ping]:",ex
            finally:    self._release_wait(qid);del cur_task
        if self.waiting() == -1:
            stackless.tasklet(do_ping)().run()
        
    def _async_query(self,squery):
        cur_task = stackless.getcurrent()
        qid = id(cur_task)
        if cur_task == stackless.getmain():
            self._waitings[qid] = False
            return self._orig_query(squery)
        #    
        self._wait()
        self._waitings[qid] = True
        self.send_query(squery)
        EventMgr.RegEvent( self.fd,EventMgr.EVO_READ,self._event_cb,qid )
        try:    
            ret = self._query_channel.receive()
        except Exception,ex:
            self._release_wait( qid )
            raise ex
        finally:    del cur_task
        #
        return ret
        
    def _on_sock_read(self,obj_arg):
        try:
            err = self.read_query_result()
            self._query_channel.send(err)
        except Exception,ex:
            self._query_channel.send_exception( Exception,ex )
        pass
    
    def _on_sock_write(self,obj_arg):
        pass
        
    def _on_sock_error(self,obj_arg):
        #EventMgr.UnregEvent(connection.fd)
        ##  Release lock...
        #self._release_wait()
        pass

    def _event_cb(self,fd,evflags,obj_arg):
        if evflags & EventMgr.EVO_READ:     self._on_sock_read(obj_arg)
        elif evflags & EventMgr.EVO_WRITE:  self._on_sock_write(obj_arg)
        elif evflags & EventMgr.EVO_ERROR:  self._on_sock_error(obj_arg)
        else:   print "fd:%s    event-flags:%s   obj_arg:%s" % (fd,evflags,obj_arg)

    
    @staticmethod        
    def _cursor_do_get_result(cursor):
        db = cursor._get_db()
        cursor._result = db.store_result()
        
        cursor.rowcount,cursor.rownumber = db.affected_rows(),0
        if cursor._result:
            cursor.description = cursor._result.describe()
            cursor.description_flags = cursor._result.field_flags()
        cursor.lastrowid,cursor._warnings,cursor._info = db.insert_id(),db.warning_count(),db.info()
        #
        cur_task = stackless.getcurrent()
        db = cursor._get_db()
        db._release_wait( id(cur_task) )
        del cur_task
    
    @staticmethod        
    def _cursor_post_get_result(cursor):
        cursor._rows = cursor._fetch_row(0)
        cursor._result = None
        

    #=====================================================
    Warning = Warning
    Error = Error
    InterfaceError = InterfaceError
    DatabaseError = DatabaseError
    DataError = DataError
    OperationalError = OperationalError
    IntegrityError = IntegrityError
    InternalError = InternalError
    ProgrammingError = ProgrammingError
    NotSupportedError = NotSupportedError

    errorhandler = defaulterrorhandler
