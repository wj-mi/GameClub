# coding:utf8

"""
打拱游戏牌的分析
"""

"""
牌的表示
[0-13)   方片3-方片2       # 5 10 K  ---> 2, 7, 10  
[13-26)  梅花3-梅花2
[26-39)  红桃3-红桃2  
[39-52)  黑桃3-黑桃2
[52-65)  
[65-78)  
[78-91)
[91-104)  
104       小王
105       小王 
106       大王
107       大王
"""
# 
SCORECARDS = []
for i in range(8):
    SCORECARDS.extend([2+13*i,7+13*i,10+13*i])

# 所有副510K
ALLOTHERKIND = []
#所有正510K
ALLSAMEKIND = []
for i in range(8):
    for j in range(8):
        for k in range(8):
            card = [2+13*i, 7+13*j, 7+13*k]
            if i != j or j != k or i != k:
                ALLOTHERKIND.append(card)
            else:
                ALLSAMEKIND.append(card)



def _judgeFourKing(cards):
    """四王
    """
    return set(cards) == set([104,105,106,107]), None
    

def _judgeSameCard(cards, sameNum):
    """判断同牌
    参数
    cards   需要判断的牌
    sameNum 相同的牌张数
    返回值
    ret     是否满足
    args    同牌的大小
    """
    if len(cards) != sameNum:   return False, None
    size = cards[0]%52%13
    for card in cards:
        if card < 104:
            if card%52%13 != size:
                return False, None
        else:
            if card != cards[0]:
                return False, None
    return (True,size) if cards[0] < 104 else (True,cards[0])

def _compareOneCard(card1, card2):
    """比较单张牌的情况
    考虑王和其他的情况的比较
    """
    compare1 = None
    compare2 = None
    if card1 >= 104 or card2 >= 104:
        if card1 >= 104 and card2 >= 104:
            compare1 = (card1-104)/2
            compare2 = (card2-104)/2
        else:
            compare1 = card1 
            compare2 = card2
    else:
        compare1 = card1%13
        compare2 = card2%13
    if compare1 == compare2:
        return 0
    elif compare1 > compare2:
        return 1
    return -1           

def _compareSameCard(cards1, cards2):
    """
    """
    if len(cards1[2]) != len(cards2[2]):    return -2
    return _compareOneCard(cards1[1], cards2[1])

def _judgeTwoSunOneMoon(cards):
    """判断大大小
    """
    return set(cards) == set([106,107,104]) \
           or set(cards) == set([106,107,105]) \
           , None

def _judgeTwoMoonOneSun(cards):
    """判断小小大
    """
    return set(cards) == set([104,105,106]) \
           or set(cards) == set([104,105,107]) \
           , None

def _judgeTwoSun(cards):
    """判断大大
    """
    return set(cards) == set([106,107]), None

def _judgeOneSunOneMoon(cards):
    """判断大小
    """
    return set(cards) == set([104,106]) \
           or set(cards) == set([104,107]) \
           or set(cards) == set([105,106]) \
           or set(cards) == set([105,107]) \
           , None

def _compareOneSunOneMoon(cards1, cards2):
    return 0

def _judgeTwoMoon(cards):
    """判断小小
    """
    return set(cards) == set([104,105]), None

def _judgeSameKind(cards):
    """判断正5 10 K(纯色)
    """
    ret = len(cards) == 3 and len( set([ card/13%4 for card in cards ]) ) == 1 \
           and set([card%13 for card in cards]) == set([2, 7, 10])
    return (ret, None) if not ret else (ret, cards[0]%52/13) 

def _compareSameKind(cards1, cards2):
    return 1 if cards1[1] > cards2[1] else -1   #_compareOneCard(cards1[2]/13, cards2[2]/13)

def _judgeOtherKind(cards):
    """判断副5 10 K(杂色)
    """
    return len(cards) == 3 and len( set([ card/13%4 for card in cards ]) ) > 1 \
           and set([card%13 for card in cards]) == set([2, 7, 10])  \
           , None

def _compareOtherKind(cards1, cards2):
    return 0

#
def _judgeDoubleStright(cards):
    """判断联对
    """
    size = [ card%13 for card in cards ]
    isPair = True
    for item in size:
        if size.count(item) < 2:
            isPair = False
            break
    if not isPair or len(cards)%2 != 0 or len(cards)/2 != len(set(size)):
        return False, None
    return _judgeStraight(list(set(size)), 2)

def _compareDoubleStright(cards1, cards2):
    return _compareStraight(cards1, cards2)

#
def _judgeStraight(cards, minCard=3):
    """判断顺子
    minCard表示至少几张牌
    """
    size = [card%13 for card in cards]
    if len(set(cards)) < minCard  or (11 in size and 12 in size) or len(set(cards) & set([104,105,106,107]))>0:    # A 和 2 不能同时出现
        return False,None 
    size.sort()
    if size[-1] == 12:  # 2
        size.insert(0,-1)
        size.remove(12)
    for i in range(len(size)-1):
        if size[i] + 1 != size[i+1]:
            return False, None
    return True, size[-1]

def _compareStraight(cards1, cards2):
    """
    """
    len1, len2 = len(cards1[2]), len(cards2[2])
    if len1 != len2:
        return -2
    if cards1[1] > cards2[1]:
        return 1
    elif cards1[1] == cards2[1]:
        return 0
    else:
        return -1

_judgeCardTypeOrder = ( \
        (_judgeStraight,None),              # 0
        (_judgeDoubleStright,None),
        (_judgeSameCard,(1,)),
        (_judgeSameCard,(2,)),
        (_judgeSameCard,(3,)),
        (_judgeSameCard,(4,)),              # 5
        (_judgeOtherKind,None),
        (_judgeSameCard,(5,)),
        (_judgeSameKind,None),
        (_judgeSameCard,(6,)),
        (_judgeTwoMoon,None),               # 10
        (_judgeOneSunOneMoon,None),
        (_judgeTwoSun,None),
        (_judgeTwoMoonOneSun,None),
        (_judgeTwoSunOneMoon,None),
        (_judgeSameCard,(7,)),              # 15
        (_judgeSameCard,(8,)),
        (_judgeFourKing, None)
    )

_compareSameCardType = (    \
        _compareStraight,
        _compareDoubleStright,
        _compareSameCard,
        _compareSameCard,
        _compareSameCard,
        _compareSameCard,
        _compareOtherKind,
        _compareSameCard,
        _compareSameKind,
        _compareSameCard,
        None,
        _compareOneSunOneMoon,
        None,
        None,
        None,
        _compareSameCard,
        _compareSameCard,
        None
    )

############ 提示功能 ############


def _findBiggerStraight(curCardType, allCards):
    curLen = len(curCardType[2])
    cards = list(set([ card%13 for card in allCards if card < 104 ]))
    if len(cards) < curLen: return -1, None
    choose = None
    for i in range(0, len(cards) - curLen):
        judgeCards = cards[i:i+curLen]
        cardType = judgeCardType(judgeCards)
        if cardType[0] == curCardType[0] and _compareStraight(cardType, curCardType) > 0:
            choose = judgeCards
            break
    if choose is None:  return -1, None
    usefulCard = []
    for card in choose:
        for tmp in allCards:
            if tmp < 104 and tmp%13 == card:
                usefulCard.append(tmp)
                break
    return 0, usefulCard

def _findBiggerDoubleStraight(curCardType, allCards):
    allSize = [ card%13 for card in allCards if card < 104 ]
    cards = list(set([ card%13 for card in allCards if card < 104 and allSize.count(card%13) >= 2 ]))
    usefulCardType = judgeCardType(list(set([card%13 for card in curCardType[2]])))
    ret, choose = _findBiggerStraight(usefulCardType, cards)
    if ret != 0: return -1, None
    usefulCard = []
    for card in choose:
        hadChoose = 0
        for tmp in allCards:
            if tmp < 104 and tmp%13 == card and hadChoose < 2:
                hadChoose += 1
                usefulCard.append(tmp)
            if hadChoose >= 2:
                break
    return 0, usefulCard


def _findBiggerSameCard(curCardType, allCards, num):
    allCardSize = []
    for card in allCards:
            allCardSize.append(card%13 if card < 104 else card)
    choose = None
    for card in allCardSize:
        if card >= 104:
            usefulCard = [ tmp for tmp in allCards if tmp == card ]
        else:
            usefulCard = [ tmp for tmp in allCards if tmp%13 == card and tmp < 104 ]
        if len(usefulCard) != num: continue
        cardType = judgeCardType(usefulCard)
        if _compareSameCard(cardType, curCardType) > 0:
            choose = usefulCard
            break
    return (-1, None) if choose is None else (0, usefulCard)
    #return (0, usefulCard) if choose >= 104 else (0, [ card for card in allCards if card%13 == choose ])

def _findBiggerOtherKind(curCardType, allCards):
    if curCardType is not None: return -1, None
    findCard = None
    for card in ALLOTHERKIND:
        useful = True
        for item in card:
            if item not in allCards:
                useful = False
                break
        if useful: 
            findCard = card
            break
    return (-1, None) if findCard is None else (0, findCard)


def _findBiggerSameKind(curCardType, allCards):
    findCard = None
    for card in ALLSAMEKIND:
        useful = True
        for item in card:
            if item not in allCards:
                useful = False
                break
        if useful:
            cardType = judgeCardType(card)
            assert(cardType[0] == curCardType[0])
            if curCardType is not None and _compareSameKind(cardType, curCardType[2]) < 0:
                continue
            else:
                findCard = card
                break
    return (-1, None) if findCard is None else (0, findCard)



def _findBiggerTwoMoon(curCardType, allCards):
    if curCardType is not None: return -1, None
    twoMoon = [104, 105]
    return (-1,None) if (twoMoon[0] not in allCards or twoMoon[1] not in allCards) else (0, twoMoon)

def _findBiggerOneSunOneMoon(curCardType, allCards):
    if curCardType is not None: return -1, None
    twoSun  = [106,107]
    findSun = __findCard(twoSun, allCards)
    if findSun is None:    return -1, None 
    twoMoon = [104,105]
    findMoon = __findCard(twoMoon, allCards)
    if findMoon is None:   return -1, None
    return [findMoon, findSun]

def _findBiggerTwoSun(curCardType, allCards):
    if curCardType is not None: return -1, None
    twoSun = [106,107]
    return (-1,None) if (twoSun[0] not in allCards or twoSun[1] not in allCards) else (0, twoSun)

def _findBiggerTwoMoonOneSun(curCardType, allCards):
    if curCardType is not None: return -1, None
    twoMoon = [104,105]
    if (twoMoon[0] not in allCards or twoMoon[1] not in allCards): return -1,None 
    twoSun  = [106,107]
    findCard = __findCard(twoSun, allCards)
    return (-1, None) if findCard is None else (0, [findCard, 104,105])


def _findBiggerTwoSunOneMoon(curCardType, allCards):
    if curCardType is not None: return -1, None
    twoSun  = [106,107]
    if (twoSun[0] not in allCards or twoSun[1] not in allCards):return -1,None
    twoMoon = [104,105]
    findCard = __findCard(twoMoon, allCards)
    return (-1, None) if findCard is None else (0, [ 106,107, findCard ])


def _findBiggerFourKing(curCardType, allCards):
    if curCardType is not None: return -1, None
    fourKing = [104,105,106,107]
    for king in fourKing:
        if king not in allCards:   return -1, None
    return 0, fourKing

def __findCard(needFind, allCards):
    """需要在needFind中找到另外一张没有在hadShow中出现的牌
    """
    for card in needFind:
        if card in allCards:
            return card 
    return None
    # for card in needFind:
    #     if card not in hadShow or hadShow is None: return card 
    # return None

hintOrder = (   \
        (_findBiggerStraight,None),              # 0
        (_findBiggerDoubleStraight,None),
        (_findBiggerSameCard,(1,)),
        (_findBiggerSameCard,(2,)),
        (_findBiggerSameCard,(3,)),
        (_findBiggerSameCard,(4,)),              # 5
        (_findBiggerOtherKind,None),
        (_findBiggerSameCard,(5,)),
        (_findBiggerSameKind,None),
        (_findBiggerSameCard,(6,)),
        (_findBiggerTwoMoon,None),               # 10
        (_findBiggerOneSunOneMoon,None),
        (_findBiggerTwoSun,None),
        (_findBiggerTwoMoonOneSun,None),
        (_findBiggerTwoSunOneMoon,None),
        (_findBiggerSameCard,(7,)),              # 15
        (_findBiggerSameCard,(8,)),
        (_findBiggerFourKing, None)
    )

##############################################33
#
# cards:传入数组
#
def judgeCardType(cards):
    """对牌型进行分析
    返回值格式(牌型，牌型相关的数据，原牌)
    """
    err = False
    data = None
    for index, judge in enumerate(_judgeCardTypeOrder):
        #judge = _judgeStraight[]
        if judge[1] is None:
            err, data = judge[0](cards)
        else:
            err, data = judge[0](cards, *judge[1])
        if err:
            return (index, data, cards)
    return (-1, None, cards)

def compareCard(cards1, cards2):
    """牌型比较
    cards1 > cards2 = 1
    cards1 == cards2 = 0
    cards1 < cards2 = -1
    无效的比较 -2
    # [4,17)以上为炸，大于[0,4)的任何牌
    # [0,4)没大小之分，只能同牌型去比较大小
    """
    cardType1, cardType2 = cards1[0], cards2[0]
    if cardType1 == -1 or cardType2 == -1:
        return -2
    if cardType1 == cardType2:
        return _compareSameCardType[cardType1](cards1, cards2)
    else:
        minType, maxType = (cardType1, cardType2) if cardType1 < cardType2 else (cardType2, cardType1)
        if minType < 4 and maxType < 4:
            return -2
        else:
            if cardType1 > cardType2:
                return 1
            elif cardType1 == cardType2:
                return 0
            elif cardType1 < cardType2:
                return -1
            #return _compareOneCard(cardType1, cardType2)

def hintCard(curCardType, allCards):
    """用来完成提示功能
    优先匹配同等级的牌，如果没有，则依次向上查找匹配
    """
    startType = 0 if curCardType is None else curCardType[0]
    for i in range(startType, len(hintOrder)):
        comp = hintOrder[i]
        ret, args = comp[0](curCardType, allCards) if comp[1] is None else comp[0](curCardType, allCards, *comp[1])
        if ret == 0:
            return ret, args
    return -1, None

def sortCard(card1, card2):
    """对牌进行有效排序
    """
    return _compareOneCard(card1, card2)



if __name__ == "__main__":
    #
    cards = [ 2, 2+13,3+13,3+26,4,4+13,5,5+13 ]
    print judgeCardType(cards)
    #
    card1 = [104]
    card2 = [12,25]
    cardType1 = judgeCardType(card1)
    cardType2 = judgeCardType(card2)
    print judgeCardType(card2)
    print compareCard(cardType1, cardType2)

    #
    cards = [  5, 5+13, 5+13*2, 5+13*4, 2 ]
    print judgeCardType(cards)
    #

    def _testHint():



        print "-------------------------- test helper ----------------------"
        print "##### test specal #######"
        print "---> hint sameCard 1"
        curCards = [ 104 ]
        allCards = [ 0,1,2,3,4,5,6,55, 105, 106, 107 ]
        curCardType = judgeCardType(curCards)
        print "curCards", curCards, "allCards", allCards
        print "ret is ", _findBiggerSameCard(curCardType, allCards,1)
        curCards = [10]
        allCards = [ 5,6, 105, 106, 107, 55 ,25 ]
        allCards.sort(sortCard)
        curCardType = judgeCardType(curCards)
        print "curCards", curCards, "allCards", allCards
        print "ret is ", _findBiggerSameCard(curCardType, allCards,1)
        
        print "-----> hint sameCard 2"
        curCards = [ 4,17 ]
        allCards = [2,3,5,13,15,18,19,104,105,106,107]
        allCards.sort(sortCard)
        curCardType = judgeCardType(curCards)
        print "curCards", curCards, "allCards", allCards
        print "ret is ", _findBiggerSameCard(curCardType, allCards,2)

        print "-----> hint straight"
        curCards = [ 5,6,7,8,9 ]   # [ 8,9,10,j,Q ]
        allCards = [ 6+13, 7+13*2,8+13,9+13,10,11,12, 104,105,106,107 ]         # [ 9,10,j,q,k,A ]
        allCards.sort(sortCard)
        curCardType = judgeCardType(curCards)
        print "curCards", curCards, "curCardType", curCardType, "  allCards", allCards
        print "ret is ", _findBiggerStraight(curCardType, allCards)

        print "-----> hint double straight"
        curCards = [0,1,2,3,12,13,14,15,16,25]   # [ 22, 33,44,55,66 ]
        allCards = [ 2+13*2,3+13*2,4,5,6,7, 2+13*3, 3+13*3, 4+13*5, 5+13*6, 6+13*3, 7+13*3 ]         # [55,66,77,88,99,10 10]
        #28, 41, 29, 42, 4, 69, 5, 83
        allCards.sort(sortCard)
        curCardType = judgeCardType(curCards)
        print "curCards", curCards, "curCardType", curCardType, "  allCards", allCards
        print "ret is ", _findBiggerDoubleStraight(curCardType, allCards)

        print "------> hint one sun one Moon"
        curCards = None   # [ 22, 33,44,55,66 ]
        allCards = [ 104,105,106,107 ]         # [55,66,77,88,99,10 10]
        allCards.sort(sortCard)
        curCardType = None
        print "curCards", curCards, "curCardType", curCardType, "  allCards", allCards
        print "ret is ", _findBiggerOneSunOneMoon(curCardType, allCards)

        print "------> hint two sun"
        curCards = None
        allCards = [ 104,105,106,107 ] 
        allCards.sort(sortCard)
        curCardType = None
        print "curCards", curCards, "curCardType", curCardType, "  allCards", allCards
        print "ret is ", _findBiggerTwoSun(curCardType, allCards)

        print "------> hint two moon one sun"
        curCards = None
        allCards = [ 104,105,106,107 ]  
        allCards.sort(sortCard)
        curCardType = None
        print "curCards", curCards, "curCardType", curCardType, "  allCards", allCards
        print "ret is ", _findBiggerTwoMoonOneSun(curCardType, allCards)

        print "------> hint two sun one moon"
        curCards = None
        allCards = [ 104,105,106,107 ] 
        allCards.sort(sortCard)
        curCardType = None
        print "curCards", curCards, "curCardType", curCardType, "  allCards", allCards
        print "ret is ", _findBiggerTwoSunOneMoon(curCardType, allCards)

        print "------> hint four king"
        curCards = None
        allCards = [ 104,105,106,107 ] 
        allCards.sort(sortCard)
        curCardType = None
        print "curCards", curCards, "curCardType", curCardType, "  allCards", allCards
        print "ret is ", _findBiggerFourKing(curCardType, allCards)

    def _testCardType():
        print "-------------------------test cardType -------------------------"
        print "##### special ######"
        _cardTypeName = (   \
                "顺子",
                "双对",
                "单张",
                "对子",
                "3张",
                "4张",
                "副510K",
                "5张",
                "正510k",
                "6张",
                "两小王",
                "一大一小王",
                "两大王",
                "两小一大王",
                "两大一小王",
                "7张",
                "8张",
                "4王",
            )
        # 测试牌的类型
        cards = (
            [0,1,2,3,4,5,6,7],             # 0
            [0,1,2,3,12,13,14,15,16,25],
            [106],
            [0,13],
            [1,14,27],
            [1,14,27,53],                 # 5
            [2,7,23],
            [1,14,27,40,53],
            [2,7,10],
            [1,14,27,40,53,66],
            [104,105],                     # 10
            [106,104],
            [106,107],
            [104,105,106],
            [106,107,104],
            [1,14,27,40,53,66,79],        # 15
            [1,14,27,40,53,66,79,92],
            [104,105,106,107]
        )
        for index, card in enumerate(cards):
            print "want %d ret is %s" % (index, str(judgeCardType(card)))
        print "######  random #####"
        import random
        for i in range(0):
            num = random.randint(0,8)
            cards = []
            for j in range(num):
                cards.append(random.randint(0,107))
            cardType = judgeCardType(cards)
            if cardType[0] > 3:
                print "ret is %s, name: %s" %(str(cardType), _cardTypeName[cardType[0]])





#########################################################3
    #_testHint()

"""
四王炸            17
8同牌             
7同牌             
大大小            
小小大            
大大              
大小              
小小              10
6同牌             
正5 10 K          
5同牌             
副5 10 K          
4同牌             5
3同牌             4  # boom
对子              
单张              
联对              
顺子              0
"""
