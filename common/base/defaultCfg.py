# coding: utf-8

"""
游戏中默认的一些配置
"""
from util.gameLog import gameLog

class DefaultCfg(object):
        gameName = ""                   # 游戏名称（注意，要和文件夹名称相同）
        gameTagCfg = -1                 # 游戏tag
        gameProtocol = ""               # 游戏协议
        mainModule = ""
        
        cfg_AddRoomLifeTime = 5 * 60 * 1000
        canAddRoomLife = 0

        @classmethod
        def setMainModule(cls, name):
                if DefaultCfg.mainModule == "":
                        DefaultCfg.mainModule = name
                        gameLog.info("set main module name [%s] success!" % name)
                else:
                        gameLog.info("main module had set [%s], new value [%s] set fail!" % (DefaultCfg.mainModule, name))



        # 
        isDebug = True