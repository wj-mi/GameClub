from CommonProtocol import PackKey,PackType
'''
General packet parsing/constructing class
Performance tips:
    1.If more than one properties should be retrieved from the GeneralPack, use 'Fetch' method instead of dot operation.
    2.If more than one properties should be set to the instance of GeneralPack,use 'Fill' method instead of dot operation.

'''
def _GEN_PROP_DICT_(obj):
    res = {}
    rset = res.__setitem__
    props = dir(obj)
    for name in props:
        if name[:2] == "__":    continue
        key,val = name[3:],getattr(obj,name)
        rset(key,val)
    return res
    
class GeneralPack(object):
    __slots__       = ("__data","__km","__keyget")
    _D_K_  = _GEN_PROP_DICT_(PackKey)
    _K_C_     = {}
    def __init__(self,data=None,PackKeyObj = None):
        if data is None:    data = {}
        km = None
        if PackKeyObj is not None:
            cls_name = type(PackKeyObj).__name__
            km = self._K_C_.get(cls_name,None)
            if km is None:   
                km = self._D_K_.copy()
                km.update( _GEN_PROP_DICT_(PackKeyObj) )
                self._K_C_[cls_name] = km
        else:   
            km = self._D_K_        
        self.__km,self.__keyget,self.__data = km,km.get,data
    
    def __del__(self):  
        self.__km,self.__keyget,self.__data = None,None,None
        del self.__data
    
    def __getattr__(self,key):  
        try: return object.__getattr__(self,key)
        except AttributeError,ae:
            rk = self.__keyget(key,None)
            if rk is None:  return None
            return self.__data.get(rk,None )

    def __setattr__(self,key,val):
        try:    object.__setattr__(self,key,val)
        except AttributeError,ae:
            _rk = self.__keyget(key,None)
            if _rk is not None: self.__data[_rk] = val
            else:   raise TypeError("Invalid key[%s] for package" % key)
    #this is used for print
    def __repr__(self):     return str(self.__data)
    
    def __call__(self,**kwargs):     
        if kwargs:  self.__data.update( kwargs )
        return self.__data

    @property
    def data(self):         return self.__data

    ##
    #@param kwargs: The keys and values to fill into the package.
    #example:
    #   pack.Fill(ID=123,NAME='test')
    def Fill(self,**kwargs):
        _ds_    = self.__data.__setitem__
        _kg_    = self.__keyget
        def F(item):
            k,v = item
            _rk = _kg_(k,None)
            if _rk is not None: _ds_(_rk,v)
            else:   raise KeyError("Invalid key[%s]" % k)
        map( F, kwargs.items() )

    ##
    #@param args: The keys to fetch from the package.
    #@return
    #   The values of the keys.If a key doesn't exist in the package,None is returned.
    #example:
    #   id,tp = pack.Fetch('ID','TYPE')
    def Fetch(self,*args):
        _dget_ = self.__data.get
        _keys_ = map(self.__keyget,args)
        if len(_keys_) > 1:     return map(_dget_,_keys_)
        else:                   return _dget_(_keys_[0])

    ##  Fetch values via given key-names and default values.
    #
    #example:
    #   id,tp = pack.KFetch(ID=-1,TYPE=0)
    def KFetch(self,**kwargs):
        _dget_ = self.__data.get
        ret , idx = list((None,)*len(kwargs)) , 0
        for k,dv in kwargs.iteritems():
            nk = self.__keyget(k)
            if nk:  ret[idx] = _dget_(nk,dv)
            else:   ret[idx] = dv
            idx += 1
        return ret




if __name__ == "__main__":
    pack = GeneralPack()
    pack.Fill(ID='hello',PARAM='parameters')
    pack.SID = "asdfasdf"
    v1,v2,v3 = pack.Fetch('ID','PARAM','NAME')
    print GeneralPack.__dict__
    print dir(pack)
    print v1,v2,v3

    def test():    
        for i in xrange(0,100000):
            pack = GeneralPack()
            pack.Fill(ID='hello',PARAM={1:'ID',2:'something',3:{'name':'inner'}})
            #_id,param,null = pack.ID,pack.PARAM,pack.NAME
            _id,param,null = pack.Fetch('ID','PARAM','NAME')

    import cProfile, pstats
    cProfile.run("test()", "testout.txt")
    p = pstats.Stats("testout.txt")
    p.strip_dirs().sort_stats("time").print_stats(20)

    
