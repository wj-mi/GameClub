# coding:utf-8
"""基类模块,通用于创建房间(房卡类游戏)，玩家通过房间号码进入房间的游戏
游戏模块说明:
        游戏管理框架:
                BaseSlave-->BaseManager-->BaseRoom
"""

__author__ = 'xiao-gengen'

from util.gameLog import gameLog

gameSlaveIns = None

def runGameServer(gameName, basePath="./scripts/"):
        import sys 
        sys.path.append(basePath+gameName)
        from defaultCfg import DefaultCfg
        DefaultCfg.setMainModule(gameName)
        if DefaultCfg.mainModule != gameName:
                return 
        print sys.path
        from gameSlave import GameSlave
        gameLog.info("%s game server start..." % (gameName,))
        gameLog.info("notic: %s, %s" % (__author__, "hello world"))
        gameSlaveIns = GameSlave()
