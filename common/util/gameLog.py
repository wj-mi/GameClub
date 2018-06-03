# coding:utf-8
"""游戏日志

对游戏的日志进行设置,游戏中,请使用gameLog模块
"""

import mylogging as logging

logging.basicConfig(
        level = logging.ERROR,
        format = '%(asctime)s %(filename)s[line:%(lineno)d,func:%(funcName)s] %(levelname)s: %(message)s'
        )

gameLog = logging



if __name__ == "__main__":
	def showLog():
		gameLog.debug("this is game logging")
	showLog()
