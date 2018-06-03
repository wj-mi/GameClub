from CommonProtocol import PackKey,PackType
'''
General packet parsing/constructing class
Performance tips:
    1.If more than one properties should be retrieved from the GeneralPack, use 'Fetch' method instead of dot operation.
    2.If more than one properties should be set to the instance of GeneralPack,use 'Fill' method instead of dot operation.

'''
cdef _GEN_PROP_DICT_(object obj):
    cdef dict res
    cdef list props
    res = {}
    props = dir(obj)
    for name in props:
        if name[:2] == "__":    continue
        key,val  = name[3:],getattr(obj,name)
        res[key] = val
    return res
    
cdef class GeneralPack:
    cdef public object __data,__keymap,__keyget
    _DEFAULT_KEYS_  = _GEN_PROP_DICT_(PackKey)
    _KEYCACHES_     = {}
    
    def __init__(self,dict data=None,object PackKeyObj = None):
        cdef object keymap
        if data is None:    data = {}
        keymap = None
        if PackKeyObj is not None:
            cls_name = type(PackKeyObj).__name__
            keymap = GeneralPack._KEYCACHES_.get(cls_name,None)
            if keymap is None:   
                keymap = GeneralPack._DEFAULT_KEYS_.copy()
                keymap.update( _GEN_PROP_DICT_(PackKeyObj) )
                self._KEYCACHES_[cls_name] = keymap
        else:   
            keymap = self._DEFAULT_KEYS_        
        self.__keymap,self.__keyget,self.__data = keymap,keymap.get,data
    
    def __del__(self):  
        self.__data = None
    
    def __dealloc__(self):  
        self.__data = None
    
    def __getattr__(self,key):  
        rk = self.__keyget(key,None)
        if not rk:  return None
        return self.__data.get( rk,None )

    def __setattr__(self,key,val):
        _rk = self.__keyget(key,None)
        if _rk is not None: self.__data[_rk] = val
        else:   raise TypeError("Invalid key[%s] for package" % key)
    #this is used for print
    def __repr__(self):     return str(self.__data)
    
    def __call__(self):     return self.__data

    @property
    def data(self):         return self.__data

    ##
    def Fill(self,**kwargs):
        '''
        @param kwargs: The keys and values to fill into the package.
        example:
           pack.Fill(ID=123,NAME='test')
       '''
        _dsetitem_  = self.__data.__setitem__
        _kget_      = self.__keyget
        for k,v in kwargs.iteritems():
            _rk = _kget_(k,None)
            if _rk is not None: _dsetitem_(_rk,v)
            else:   raise KeyError("Invalid key:" + k)
        _dsetitem_,_kget_ = None,None

    def Fetch(self,*args):
        '''
        @param args: The keys to fetch from the package.
        @return
           The values of the keys.If a key doesn't exist in the package,None is returned.
        example:
           id,tp = pack.Fetch('ID','TYPE')
       '''
        _dget_ = self.__data.get
        _keys_ = map(self.__keyget,args)
        if len(_keys_) > 1:    return map(_dget_,_keys_)
        else:                  return _dget_(_keys_[0])
        _dget_,_keys_ = None,None
    
    #
    def KFetch(self,**kwargs):
        '''
        Fetch fields by given KEY via **kwargs 
        '''
        _dget_ = self.__data.get
        ret , idx = list((None,)*len(kwargs)) , 0
        for k,dv in kwargs.iteritems():
            nk = self.__keyget(k)
            if nk:  ret[idx] = _dget_(nk,dv)
            else:   ret[idx] = dv
            idx += 1
        return ret








   
