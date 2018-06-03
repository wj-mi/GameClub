#-*-coding:utf8-*-

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

ALLCARDS = [ 1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,31,41,51 ]

def _genAllCardSizeAndType(cards):
    info = {}
    for card in cards:
        cardType = card/10 
        cardSize = card%10
        info[card] = [cardSize, cardType]
    return info

ALLCARDSSIZEANDTYPE = _genAllCardSizeAndType(ALLCARDS)

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


def _sameType(cards, laizi, pengGangChi):
    """
    清一色
    :param cards: 除去万能牌之后的牌
    :return: true/False
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

def judgeWanneng(srcCards, card, laizi, pengGangChi, selfGet):
    return _judgeWanneng(srcCards, card, laizi, pengGangChi, selfGet)


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
                #print item
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

def _removeLaizi(srcCards, laizi):
    """从牌srcCards中移除癞子
    返回值 移除后的牌和癞子的个数
    """
    cards = srcCards[:]
    laiziCount = cards.count(laizi)
    _removeItems(cards, [laizi]*laiziCount)
    return cards, laiziCount


def _removeItems(sets, items):
    for item in items:
        if item in sets:
            sets.remove(item)


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
    # needJudge = [ _judgeQidui, _loopCheckLian , _loopCheckSanpeng ]
    #
    ret = 0
    ret = _judgeQidui(cardRemoveLaizi[:], laiziCount)
    if ret == 0:
        srcCardsCopy = srcCards[:]
        #print "normal ", srcCardsCopy, laizi
        ret = _judgeNormalHu(srcCardsCopy, laizi)


    #for item in needJudge:
    #    ret = item(cardRemoveLaizi[:], laiziCount) 
    #    if ret != 0: break
    isQing = 0 
    if ret != 0:
        isQing = _sameType(srcCards, laizi, pengGangChi)
    return [ret, isQing]

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

def _judgeNormalHu(cards, laizi):
    cardCount, laiziIndex = _countCards(cards, laizi)
    #print cardCount, laiziIndex
    #print cardCount ,"    ", laiziIndex
    return 2 if get_hu_info(cardCount, laiziIndex) else 0


def _countCards(cards, laizi):
    """ """
    cards_num = [0]*34
    laizi_index = 34
    for card in cards:
        index = (card/10*9+card%10) if card < 30 else (card/10+29)
        index -= 1
        cards_num[index] += 1
        laizi_index = index if card == laizi else laizi_index
    return cards_num, laizi_index


def get_hu_info(hand_cards, gui_index):
    cards = hand_cards[:]
    #if cur_card != 34:
    #    cards[cur_card] = cards[cur_card] + 1
    gui_num = 0
    if gui_index != 34:
        gui_num = cards[gui_index]
        cards[gui_index] = 0
    totalItem = 0
    for item in cards:
        totalItem += item
    if totalItem == 0:
        return True

    eyes = []
    empty = -1
    for i in range(0,34):
        n = cards[i]
        if n == 0:
            empty = i
        elif n == 1 and gui_num >= 1:
            eyes.append(i)
        else:
            eyes.append(i)

    if gui_num > 2:
        eyes.append(empty)
        
    hu = False
    cache = [0,0,0,0]
    for i in eyes:
        if i == empty:
            hu = foreach_eye(cards, gui_num - 2, gui_num, 1000, cache)
        else:
            n = cards[i]
            color = i/9
            if n == 1:
                cards[i] = 0
                hu = foreach_eye(cards, gui_num - 1, gui_num, color, cache)
            else:
                cards[i] = cards[i] - 2
                hu = foreach_eye(cards, gui_num,gui_num,color,cache)
            cards[i] = n
        if hu:
            break
            
    if gui_num > 0:
        cards[gui_index] = gui_num
            
    return hu
    
def foreach_eye(cards, gui_num, max_gui, eye_color, cache):
    left_gui = gui_num
    for i in range(0, 3):
        cache_index = -1
        if eye_color != i:
            cache_index = i
 
        need_gui = check_normal(cards, i*9, max_gui, cache_index, cache)
        if cache_index >= 0:
            cache[cache_index] = need_gui+1
        left_gui = left_gui - need_gui
        if left_gui < 0:
            return False

    cache_index = -1
    if eye_color != 3: 
       cache_index = 3
    need_gui = check_zi(cards, max_gui, cache_index, cache)
    if cache_index> 1:
        cache[3] = need_gui + 1
    return left_gui >= need_gui

def check_zi(cards,  max_gui, cache_index, cache):
    if cache_index >= 1:
        n = cache[cache_index]
        if n > 0:
           return n - 1

    need_gui = 0
    
    for i in range(27, 34):
        c = cards[i]
        if c == 1 or c == 4:
            need_gui = need_gui + 2
        elif c == 2:
            need_gui = need_gui + 1
        if need_gui > max_gui:
           return need_gui
    return need_gui

def check_normal(cards, begin, max_gui, cache_index, cache):
    if cache_index >= 1:
        n = cache[cache_index]
        if n > 0:
           return n - 1

    n = 0
    for i in range(begin, begin+9):
        n = n * 10 + cards[i]
    
    if n == 0:
       return 0
    return next_split(n, 0, max_gui)


def next_split(n, need_gui, max_gui):
    c = 0
    while True:
        if n == 0:
           return need_gui
        
        while (n > 0):
            c = n % 10
            n = n / 10
            if c != 0:
               break
        if c == 1 or c == 4:
            return one(n, need_gui, max_gui)
        elif c == 2:
            return two(n, need_gui, max_gui)
    return need_gui

def one(n, need_gui, max_gui):
    c1 = n % 10
    c2 = (n % 100) / 10

    if c1 == 0:
        need_gui = need_gui + 1
    else:
        n = n - 1

    if c2 == 0:
       need_gui = need_gui + 1
    else:
       n = n - 10

    if n == 0:
       return need_gui

    if need_gui > max_gui :
       return need_gui

    return next_split(n, need_gui, max_gui)

def two(n, need_gui, max_gui):
    c1 = n % 10
    c2 = (n % 100) / 10
    c3 = (n % 1000) / 100
    c4 = (n % 10000) / 1000
    
    choose_ke = True
    if c1 == 0:
        pass
    elif c1 == 1:
        if c2 == 0 or c2 == 1:
            pass
        elif c2 == 2:
            if c3 == 2:
                if c4 == 2:
                    choose_ke = False
            elif c3 == 3:
                if c4 != 2:
                    choose_ke = False
            else:
                choose_ke = False
        elif c2 == 3:
            if c3 == 0 or c3 == 2 or c3 == 1 or c3 == 4:
                choose_ke = False
        elif c2 == 4:
            if c3 == 2:
                if c4 == 2 or c4 == 3 or c4 == 4:
                    choose_ke = False
            elif c3 == 3:
                choose_ke = False
    elif c1 == 2:
        choose_ke = False
    elif c1 == 3:
        if c2 == 2:
            if c3 == 1 or c3 == 4:
                choose_ke = False
            elif c3 == 2:
                if c4 != 2:
                    choose_ke = False
        if c2 == 3:
            choose_ke = False
        elif c2 == 4:
            if c3 == 2:
                choose_ke = False
    elif c1 == 4:
        if c2 == 2 and c3 != 2:
            choose_ke = False
        elif c2 == 3:
            if c3 == 0 or c3 == 1 or c3 == 2:
                choose_ke = False
        elif c2 == 4:
            if c3 == 2:
                choose_ke = False


    if choose_ke:
        need_gui = need_gui + 1
    else:
        if c1 < 2:
            need_gui = need_gui + (2 - c1)
            n = n - c1
        else: 
            n = n - 2

        if c2 < 2:
            need_gui = need_gui + (2 - c2)
            n = n - c2
        else:
            n = n - 20

    if n == 0:
       return need_gui

    if need_gui > max_gui:
       return need_gui

    return next_split(n, need_gui, max_gui)


# 
if __name__ == "__main__":
    cards = [5,6,7,7,24,25,12,13,14,14,15,16, 11]   
    #28 21
    #cards = [15,15,7,8,18,18,23,24,26,27]
    #for card in ALLCARDS:
    #print _checkHu([5,5], 5,[[],[],[]])
    #print _judgeNormalHu([5,15], 5)
    print _judgeWanneng(cards, 4, 11, [[],[],[]], True)
    # cards = [
    #     0,0,0,0,0,2,0,0,0,  # 
    #     1,1,1,0,0,0,0,0,0,
    #     0,1,0,1,1,1,0,1,0,
    #     0,0,0,0,0,0,0]
    #   #[6,6,11,12,13,22,24,25,26,28]  25, 6
    # #for card in ALLCARDS:
   # print get_hu_info(cards, 22 , 5) #, [[],[],[]], True)
