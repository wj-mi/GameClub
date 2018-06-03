# coding:utf-8

"""
操作类型
1.吃
2.碰
3.杠
4.胡
胡牌类型
1.清一色(大胡)
2.7对(大胡)
3.其他(小胡)
"""
"""
# 麻将的表示方式
# tong 1, 2, 3, 4, 5, 6, 7, 8, 9, 
# tiao 11, 12, 13, 14, 15, 16, 17, 18, 19, 
# wan  21, 22, 23, 24, 25, 26, 27, 28, 29, 
# zhong  31
# fa     41 
# bai    51
共 120 张
"""

from gameDealer import GameDealer
import time

ALLCARDS = [ 1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,31,41,51 ]

def time_count(func):
    def wrap(*args, **kwargs):
        begin = time.time()
        rest = func(*args, **kwargs)
        #print 'run time: ', time.time() - begin
        return rest
    return wrap

server2client = {

}

client2server = {

}




def _genAllCardSizeAndType(cards):
    info = {}
    for card in cards:
        cardType = card/10 
        cardSize = card%10
        info[card] = [cardSize, cardType]
    return info

ALLCARDSSIZEANDTYPE = _genAllCardSizeAndType(GameDealer.genNewCardsAll())


def _findSameSizeAndSameTypeCards(srcCards, card):
    """找srcCards中和card大小和花色相同的牌
    """
    cardSizeType = ALLCARDSSIZEANDTYPE[card]
    return [ tmp for tmp in srcCards if ALLCARDSSIZEANDTYPE[tmp] == cardSizeType ]

def _findNearCard(card):
    """查找临近的牌
    包括前2张|前后各1张|后2张
    """
    cardInfo = ALLCARDSSIZEANDTYPE[card]
    size = cardInfo[0]
    findRet = []
    # 前2张
    if size >= 3:
        findRet.append([cardInfo[1]*10+size-1, cardInfo[1]*10+size-2])
    # 前后各一张
    if size >= 2 and size <= 8:
        findRet.append([cardInfo[1]*10+size-1, cardInfo[1]*10+size+1])
    # after 2
    if size <= 7:
        findRet.append([cardInfo[1]*10+size+1, cardInfo[1]*10+size+2])
    return findRet

    # 2017-12-08 20:08:10,155 gameRoom.py[line:503,func:playerChooseAct] INFO: player[9927] action[1]
    # ----------choose chi  curBet  8   receive card  [7, 9]   ret  [[7, 6]]


def _judgeCanChi(srcCards, card):
    """判断srcCards能否吃card牌
    如果card不是中发白,找card的 前2张|前后各1张|后2张
    3种情况满足其中的一种就可以
    """
    if card >= 31:
        return []
    needCards = _findNearCard(card)
    usefulCards = [ needCard for needCard in needCards if needCard[0] in srcCards and needCard[1] in srcCards ]
    return usefulCards

def judgeCanChi(srcCards, card):
    return _judgeCanChi(srcCards, card)

def _judgeCanGangOrPeng(srcCards, card):
    """判断scrCards能否碰或杠card牌
    0 不能碰也不能杠 1 能碰  2 能杠 3 能碰能杠
    """
    cards = _findSameSizeAndSameTypeCards(srcCards, card)
    if len(cards) <= 1:
        return 0, cards 
    return 3 if len(cards) == 3 else 1

def judgeCanGangOrPeng(srcCards, card):
    return _judgeCanGangOrPeng(srcCards, card)

# def judgeWanneng(srcCards, card, laizi, pengGangChi, selfGet):
#     return _judgeWanneng(srcCards, card, laizi, pengGangChi, selfGet)


def _sameType(cards, laizi, pengGangChi):
    """
    清一色
    :param cards: 除去万能牌之后的牌
    :return: true/false
    """
    cards.extend(pengGangChi[0])
    cards.extend(pengGangChi[1])
    for chi in pengGangChi[2]:
        cards.extend(chi)
    allType = [ ALLCARDSSIZEANDTYPE[card][1] for card in cards ]
    if len(allType) == 1:
        return 1
    num = cards.count(laizi)
    for i in range(num):
        cards.remove(laizi)
    allType = [ ALLCARDSSIZEANDTYPE[card][1] for card in cards ]
    return 2 if len(set(allType)) == 1 else 0


def judgePlayerAction(srcCards, card, laizi, pengGangChi, selfGet=False):
    info = {"peng":0, "gang":0, "chi":0, "hu":0}
    ret = _judgeCanGangOrPeng(srcCards, card)
    if ret == 1:
        info["peng"] = 1
    elif ret == 3:
        info["peng"] = 1
        info["gang"] = 1
    if len(_judgeCanChi(srcCards, card)) > 0:
        info["chi"] = 1
    hu = _judgeWanneng(srcCards, card, laizi, pengGangChi,selfGet)
    info["hu"] = 1 if hu[0] != 0 else 0
    info["huType"] = hu
    if info["peng"] == 0 and info["gang"] == 0 and info["chi"] == 0 and info["hu"] == 0:
        return None
    return info


def _judgeWanneng(srcCards, getCard, laizi, pengGangChi, selfGet):
    """ 
    [胡牌的类型,是否是清一色, useLaizi]
    """
    #
    if not selfGet:
        canHuAll = True
        for item in ALLCARDS:
            ret = 0
            cards = srcCards[:]
            cards.append(item)
            cards.sort()
            ret = _checkHu(cards, laizi, pengGangChi)
            if ret[0] == 0:
                canHuAll = False
                break
            if item == getCard and (ret[0] == 1 or (ret[0] != 0 and ret[1] != 0)):
                canHuAll = False
                break
        if canHuAll == True:
            return [0,0,0]
    cards = srcCards[:]
    cards.append(getCard)
    cards.sort()
    ret = _checkHu(cards, 0, pengGangChi)
    if ret[0] != 0:
        ret.append(0)
    else:
        ret = _checkHu(cards, laizi, pengGangChi)
        ret.append(1)
    return ret 

def judgeWanneng(srcCards, getCard, laizi, pengGangChi,selfGet=False):
    return _judgeWanneng(srcCards, getCard, laizi, pengGangChi,selfGet)

def _checkHu(srcCards, laizi, pengGangChi):
    """检查是否能胡牌
    参数:srcCards为原牌 laizi表示癞子牌
    返回值:[胡牌的类型,是否是清一色] 类型：0 不能胡 1 七对 2 3n+2  | 0 不是清一色 1 是清一色
    """
    # 保存结果
    canHuCardInfo = {1:[], 2:[]}
    tingPaiInfo = {}   # { 1: [3,4,5],  }
    #huInfo = {}  # {1: [2,3,4], 2: [3,4,5]} 出1可以胡2,3,4；2可以胡 3，4，5
    #
    srcCardsCopy = srcCards[:]
    cardRemoveLaizi, laiziCount = _removeLaizi(srcCardsCopy, laizi)
    needJudge = [ _judgeQidui, _loopCheckLian , _loopCheckSanpeng ]
    #
    ret = 0
    for item in needJudge:
        ret = item(cardRemoveLaizi[:], laiziCount) 
        if ret != 0: break
    isQing = 0 
    if ret != 0:
        isQing = _sameType(srcCards, laizi, pengGangChi)
    return [ret, isQing]

def _removeLaizi(srcCards, laizi):
    """从牌srcCards中移除癞子
    返回值 移除后的牌和癞子的个数
    """
    cards = srcCards[:]
    laiziCount = cards.count(laizi)
    _removeItems(cards, [laizi]*laiziCount)
    return cards, laiziCount


def _judgeQidui(cards, laiziCount):
    """判断是否是七对
    cards为移除了laizi后的牌
    """
    if len(cards) + laiziCount != 14: return 0
    cards = cards[:]
    while True:
        if _removeTwo(cards):
            if len(cards) == 0:
                return 1
        else:
            if len(cards) == 0:
                return 1
            elif len(cards) == 1:
                if laiziCount == 1 or laiziCount == 3:
                    return 1
            elif len(cards) == 2:
                if laiziCount == 2 or laiziCount == 4:
                    return 1
            elif len(cards) == 3:
                if laiziCount == 3:
                    return 1
            elif len(cards) == 4:
                if laiziCount == 4:
                    return 1
            return 0
    return 0

def _loopCheckLian(cards, laiziCount=0):
    cards = cards[:]
    canHu = False
    while True:
        breakLoop, canHu = _checkLian(cards, laiziCount) 
        if breakLoop:
            break
    return 2 if canHu else 0

def _checkLian(cards, laiziCount):
    """判断连牌的情况
    !必须留上一个对子
    """
    #cards = cards[:]
    starcur = cards[:]
    canHu = False
    if len(cards) == 0:   # 手牌已经没有了，只有癞子牌了
        if laiziCount == 2:
            canHu = True
            return True, canHu
    elif len(cards) == 1:
        if laiziCount == 1 or laiziCount == 4:
            canHu = True
            return True, canHu
    elif len(cards) == 2:
        if (cards[0] == cards[1]):
            if laiziCount == 0 or laiziCount == 3:
                canHu = True
                return True, canHu
        elif laiziCount == 3:
            canHu = True
            return True, canHu
    for i in range(len(cards)):
        for card0 in cards:
            if card0 == cards[i] + 1:
                for card1 in cards:
                    if card1 == cards[i] + 2:
                        _removeItems(cards, [cards[i], card0, card1])
                        if len(starcur) > 3:
                            x = 1
                            while x <= 6:
                                # r = starcur.index(card1+x)
                                if card1+x in starcur: #r != -1:
                                    r = card1 + x
                                    cards3 = starcur[:]
                                    _removeItems(cards3, [r-2,r-1,r])
                                    #for card4 in cards3:
                                    if _loopCheckLian(cards3, laiziCount) != 0:
                                        canHu = True
                                        return True, canHu
                                    x += 1
                                    continue
                                break
                        return False, canHu



                        # for card2 in cards:
                        #     if (card2 == card1+1):
                        #         _removeItems(starcur, [card0, card1, card2])
                        #         if _loopCheckLian(starcur, laiziCount)!= 0:
                        #             canHu = True
                        #             return True, canHu 

                        #         #from time import *
                        #         #sleep(1)
                        #         break
                        # #print "---- break fallse"
                        # return False, canHu
    if len(cards) == 3:
        #print "----- len 3"
        if laiziCount == 2:
            if _removeTwo(cards) or _removeNext(cards):
                canHu = True
                return True, canHu
    if len(cards) == 4:
        #print "----- len 4"
        if laiziCount == 1:
            if _removeTwo(cards):
                if _removeNext(cards) or _removeTwo(cards):
                    canHu = True
                    return True, canHu
        elif laiziCount == 4:
            if _removeNext(cards) or _removeTwo(cards):
                canHu = True
                return True, canHu
    if len(cards) == 5:
        #print "----- len 5"

        if laiziCount == 3:
            tmp = cards[:]
            if _removeTwo(tmp):
                if _removeTwo(tmp) or _removeNext(tmp):
                    canHu = True
                    return True, canHu
            tmp = cards[:]
            if _removeNext(tmp):
                if _removeTwo(tmp) or _removeNext(tmp):
                    canHu = True
                    return True, canHu
    if len(cards) == 6:
        #print "----- len 6"
        if (laiziCount == 2):
            tmp = cards[:]
            if _removeTwo(cards):
                tmp2 = cards[:]
                if _removeTwo(tmp2):
                    if _removeTwo(tmp2) or _removeNext(tmp2):
                        canHu = True
                        return True, canHu
                tmp2 = cards[:]
                if _removeNext(tmp2):
                    if _removeTwo(tmp2) or _removeNext(tmp2):
                        canHu = True
                        return True, canHu
            cards = tmp[:]
            if _removeNext(cards):
                tmp2 = cards[:]
                if _removeTwo(tmp2):
                    if _removeTwo(tmp2) or _removeNext(tmp2):
                        canHu = True
                        return True, canHu
                tmp2 = cards[:]
                if _removeNext(tmp2):
                    if _removeTwo(tmp2):
                        canHu = True
                        return True, canHu

    if len(cards) == 7:
        #print "----- len 7"
        if laiziCount == 4:
            tmp = cards[:]
            if _removeTwo(tmp):
                tmp2 = tmp[:]
                if _removeTwo(tmp2):
                    if _removeTwo(tmp2) or _removeNext(tmp2):
                        canHu = True
                        return True, canHu
                tmp2 = tmp[:]
                if _removeNext(tmp2):
                    if _removeTwo(tmp2) or _removeNext(tmp2):
                        canHu = True
                        return True, canHu
            tmp = cards[:]
            if _removeNext(tmp):
                tmp2 = tmp[:]
                if _removeTwo(tmp2):
                    if _removeTwo(tmp2) or _removeNext(tmp2):
                        canHu = True
                        return True, canHu
                tmp2 = tmp[:]
                if _removeNext(tmp2):
                    if _removeTwo(tmp2) or _removeNext(tmp2):
                        canHu = True
                        return True, canHu
    if len(cards) == 8:
        #print "----- len 8"
        if laiziCount == 3:
            tmp = cards[:]
            if _removeTwo(tmp):
                tmp2 = tmp[:]
                if _removeTwo(tmp2):
                    tmp3 = tmp2[:]
                    if _removeTwo(tmp3):
                        if _removeTwo(tmp3) or _removeNext(tmp3):
                            canHu = True
                            return True, canHu
                    tmp3 = tmp2[:]
                    if _removeNext(tmp3):
                        if _removeTwo(tmp3) or _removeNext(tmp3):
                            canHu = True
                            return True, canHu
                tmp2 = tmp[:]
                if _removeNext(tmp2):
                    tmp3 = tmp2[:]
                    if _removeTwo(tmp3):
                        if _removeTwo(tmp3) or _removeNext(tmp3):
                            canHu = True
                            return True, canHu
                    tmp3 = tmp2[:]
                    if _removeNext(tmp3):
                        if _removeTwo(tmp3) or _removeNext(tmp3):
                            canHu = True
                            return True, canHu
            tmp = cards[:]
            if _removeNext(tmp):
                tmp2 = tmp[:]
                if _removeTwo(tmp2):
                    tmp3 = tmp2[:]
                    if _removeTwo(tmp3):
                        if _removeTwo(tmp3) or _removeNext(tmp3):
                            canHu = True
                            return True, canHu
                    tmp3 = tmp2[:]
                    if _removeNext(tmp3):
                        if _removeTwo(tmp3) or _removeNext(tmp3):
                            canHu = True
                            return True, canHu
                tmp2 = tmp[:]
                if _removeNext(tmp2):
                    tmp3 = tmp2[:]
                    if _removeTwo(tmp3):
                        if _removeTwo(tmp3) or _removeNext(tmp3):
                            canHu = True
                            return True, canHu
                    tmp3 = tmp2[:]
                    if _removeNext(tmp3):
                        if _removeTwo(tmp3):
                            canHu = True
                            return True, canHu

    if len(cards) == 10:
        #print "----- len 10"
        if laiziCount == 4:
            tmp = cards[:]
            if _removeTwo(tmp):
                tmp2 = tmp[:]
                if _removeTwo(tmp2):
                    tmp3 = tmp2[:]
                    if _removeTwo(tmp3):
                        tmp4 = tmp3[:]
                        if _removeTwo(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                        tmp4 = tmp3[:]
                        if _removeNext(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                    tmp3 = tmp2[:]
                    if _removeNext(tmp3):
                        tmp4 = tmp3[:]
                        if _removeTwo(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                        tmp4 = tmp3[:]
                        if _removeNext(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                tmp2 = tmp[:]
                if _removeNext(tmp2):
                    tmp3 = tmp2[:]
                    if _removeTwo(tmp3):
                        tmp4 = tmp3[:]
                        if _removeTwo(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                        tmp4 = tmp3[:]
                        if _removeNext(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                    tmp3 = tmp2[:]
                    if _removeNext(tmp3):
                        tmp4 = tmp3[:]
                        if _removeTwo(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                        tmp4 = tmp3[:]
                        if _removeNext(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
            tmp = cards[:]
            if _removeNext(tmp):
                tmp2 = tmp[:]
                if _removeTwo(tmp2):
                    tmp3 = tmp2[:]
                    if _removeTwo(tmp3):
                        tmp4 = tmp3[:]
                        if _removeTwo(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                        tmp4 = tmp3[:]
                        if _removeNext(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                    tmp3 = tmp2[:]
                    if _removeNext(tmp3):
                        tmp4 = tmp3[:]
                        if _removeTwo(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                        tmp4 = tmp3[:]
                        if _removeNext(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                tmp2 = tmp[:]
                if _removeNext(tmp2):
                    tmp3 = tmp2[:]
                    if _removeTwo(tmp3):
                        tmp4 = tmp3[:]
                        if _removeTwo(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                        tmp4 = tmp3[:]
                        if _removeNext(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                    tmp3 = tmp2[:]
                    if _removeNext(tmp3):
                        tmp4 = tmp3[:]
                        if _removeTwo(tmp4):
                            if _removeTwo(tmp4) or _removeNext(tmp4):
                                canHu = True
                                return True, canHu
                        tmp4 = tmp3[:]
                        if _removeNext(tmp4):
                            if _removeTwo(tmp4):
                                canHu = True
                                return True, canHu
    return True, canHu

def _loopCheckSanpeng(cards, laiziCount):
    """
    """
    peng = _checkPengCount(cards)
    tmpCards0 = None
    for i in range(len(peng)):
        tmpCards0 = cards[:]
        _removeSanpeng(tmpCards0, peng[i])
        if _loopCheckLian(tmpCards0, laiziCount) != 0: return 2
        if len(peng) >= 2:
            for j in range(len(peng)):
                tmpCards1 = tmpCards0[:]
                _removeSanpeng(tmpCards1, peng[j])
                if _loopCheckLian(tmpCards1, laiziCount) != 0: return 2
                if len(peng) >= 3:
                    for k in range(len(peng)):
                        tmpCards2 = tmpCards1[:]
                        _removeSanpeng(tmpCards2, peng[k])
                        if _loopCheckLian(tmpCards2, laiziCount) != 0: return 2
                        if len(peng) >= 4:
                            for l in range(peng):
                                tmpCards3 = tmpCards2[:]
                                _removeSanpeng(tmpCards3, peng[l])
                                if _loopCheckLian(tmpCards3, laiziCount) != 0: return 2
    return 0

def _checkPengCount(cards):
    setCards = set(cards)
    peng = [ card for card in setCards if cards.count(card) >= 3 ]
    return peng


def _removeSanpeng(cards, needRemove):
    _removeItems(cards, [needRemove]*3)

def _removeTwo(cards):
    """去除两张相同的牌,用与判断龙七对用
    在原数组上删除
    """
    needRemove = None
    for card in cards:
        if cards.count(card) >= 2:
            needRemove = card
            break
    if needRemove != None:  
        _removeItems(cards, [needRemove, needRemove])
    return True if needRemove != None else False

def  _removeNext(cards):
    needRemove = None
    for index in range(len(cards)-1):
        #count1 = [ cards[index] ] * cards.count(cards[index])
        #count2 = [ cards[index+1] ] * cards.count(cards[index+1])
        #if len(count1) < 2 and len(count2) < 2:
        if (cards[index]/10 == cards[index+1]/10) and (abs(cards[index] - cards[index+1]) <= 2):
            needRemove = [ cards[index], cards[index+1] ]
            break
    if needRemove != None:
        _removeItems(cards, needRemove)
    return True if needRemove != None else False



def _removeItems(sets, items):
    for item in items:
        if item in sets:
            sets.remove(item)


if __name__ == "__main__":
    # 万：有1万，2万，3万，3万，3万，4万，5万，别人出3万
    # 判断能吃的话，返回的数组大小是3
    # 判断能碰/杠是既能碰也能杠
    # srcCards = [0,1,2,2,2,3,4]
    # card = 2
    # print "allCards ", srcCards[:], "  card", card
    # print judgePlayerAction(srcCards, card)
    # print "*"*60
    # 手牌
    # 万：1，2，3，5，5，5，
    # 筒：4，5，6，7
    # 出： 7筒
    # srcCards = [0,1,2,4,4,4, 21,22,23,24]
    # Cards = [
    #     # [2, 2, 2, 2, 1, 1, 10, 10, 16, 16, 3, 3, 5],
    #     # [3, 3, 3, 2, 2, 2, 14, 14, 14, 1, 1, 1, 5],
    #     [8, 9, 10, 7, 8, 9, 6, 6, 11, 11, 11, 12, 5],
    #     [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5],
    #     [2, 2, 2, 2, 1, 3, 10, 8, 20, 16, 7, 3, 5],
    #     [2, 1, 2, 3, 26, 8, 9, 9, 10, 27, 14, 14, 13],
    #     [1, 1, 1, 3, 3, 3, 4, 4, 5, 5, 6, 6, 6],
    #     [1, 2, 3, 4, 7, 8, 6, 9, 10, 27, 23, 2, 5],
    #     [3, 4, 5, 4, 6, 7, 7, 9, 9, 9, 10, 10, 10]
    # ]
    # card = 5
    # # print "allCards ", srcCards[:], "  card", card
    # # print judgePlayerAction(srcCards, card)
    # for srcCards in Cards:
    #     #print '-origin: {}, card {}'.format(sorted(srcCards), card)
    #     print _judgeWanneng(srcCards, card, 5)

    # """
    #                     1->9连续表示
    # 筒 * 9 * 4 = 36      [0,9)                     #[ [0,9), [9,18), [18, 27), [27,36) ] 
    # 条 * 9 * 4 = 36      [9,18)                    #[ [36,45), [45, 54), [54,63), [63,72) ]
    # 万 * 9 * 4 = 36      [18,27)                   #[ [72,81), [81, 90), [90, 99), [99, 108) ]
    # 中 * 4 = 4           31                        #[108,109,110,111]
    # 发 * 4 = 4           41                        #[112,113,114,115]
    # 白 * 4 = 4           51                        #[116,117,118,119]
    # 共 120 张
    # """
    cards = [15,15,7,8,18,18,23,24,26,27]
    #for card in ALLCARDS:
    print judgeWanneng(cards, 25, 15, [[],[],[]], True)