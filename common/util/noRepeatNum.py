# coding: utf-8 

'''
xiao-gengen
生成不重复的编号
!!!! 临时使用,不会是正式版本
'''

import random
from gameCfg  import GameCfg

NO_USE = []
#USING  = []

#for i in range(100000, 1000000):
for i in range(GameCfg.codeBegin, GameCfg.codeEnd):
    NO_USE.append(i)

random.shuffle(NO_USE)

# 需要得到一个数字
def getCode():
    if len(NO_USE) > 0:
        num = NO_USE[0]
        NO_USE.remove(num)
        return num 
    return None

# 返回一个数字
def returnCode(code):
    try:
        #USING.remove(code)
        NO_USE.append(code)
    except MyException,e:
        print e.message





# test
if __name__ == '__main__':
    for i in range(10):
        print getCode()

    print len(NO_USE)
    #print USING


