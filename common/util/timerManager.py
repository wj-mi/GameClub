# coding:utf-8
# xiao-gengen

'''
用来负责整个游戏系统的时间相关数据
'''
import TimerSys
import time
import stackless

# 定时器中的一个小单元
class TimerObj:
    def __init__(self, index, lifeTime, obj, callback, args, startTime):
        self.index = index 
        self._lifeTime = lifeTime
        self._obj = obj 
        self._callback = callback
        self._args = args
        if startTime is None:
            startTime = int(time.time()*1000)
        self._startTime = int(startTime)

    def __del__(self):
        self._obj = None

    def getLeftTime(self):
        """得到剩余的时间
        """
        return int(self._lifeTime) - (int(time.time()*1000) - int(self._startTime))

    def getLifeTime(self):
        """得到总共的时间
        """
        return self._lifeTime

    def addLifeTime(self, time):
        """增加时间
        """
        self._lifeTime += time 

    def callBack(self):
        """调用处理函数
        """
        #TimerSys.BeNice()
        callback = getattr(self._obj, self._callback)
        if self._args is None:
            callback()
        else:
            callback(*self._args)
        del self._obj
        del self._args

class TimerManager:
    global TimerObj
    def __init__(self):
        self._indexStream = 0
        self._allTimers = {}
        self._timer = TimerSys.RegTimer(500, self._checkTimer, TimerSys.TF_LOOP, None)

    def unRegTimer(self):
        self._allTimers = {}
        TimerSys.UnregTimer(self._timer)

    def __del__(self):
        pass 

    def hasTimer(self, time):
        if self._allTimers.has_key(time):
            return True
        else:
            return False
    '''
    索引向后,返回当前值(^-^可能有bug)
    '''
    def nextIndex(self):
        oldIndex = self._indexStream
        start = self._indexStream
        tmp = start 
        while True:
            tmp = (tmp + 1)%100000
            if not self._allTimers.has_key(tmp): #or tmp == start:
                self._indexStream = tmp
                break
        return oldIndex

    '''
    添加一个定时器
    '''
    def addTimer(self, lifeTime, obj, callback, args=None, startTime=None):
        index = self.nextIndex()
        self._allTimers[index] = TimerObj(index, lifeTime, obj, callback, args, startTime)
        return index

    '''
    删除定时器
    '''
    def delTimer(self, index):
        self._allTimers.pop(index, None)

    '''
    得到某个定时器剩余的时间
    '''
    def getLeftTime(self, id):
        try:
            if self._allTimers.has_key(int(id)):
                return self._allTimers[int(id)].getLeftTime()
            else:
                return 0
        except:
            pass

    '''
    得到某个定时器的总时间
    '''
    def getLifeTime(self, id):
        try:
            if self._allTimers.has_key(int(id)):
                return self._allTimers[int(id)].getLifeTime()
            else:
                return 0
        except:
            pass

    '''
    添加一个定时器的时间
    '''
    def addLifeTime(self, id, time):
        timer = self._allTimers.get(id, None)
        if timer:
            timer.addLifeTime(time)


    '''
    到时间检测
    '''
    def _checkTimer(self, args=None):
        needDel = {}
        keys = self._allTimers.keys()
        for index in keys:
            timer = self._allTimers.get(index, None)
            if timer and timer.getLeftTime() <= 0:
                #timer.callBack()
                try:
                    stackless.tasklet(timer.callBack)().insert()
                except:
                    pass 
                if self._allTimers.has_key(index):
                    del self._allTimers[index]
