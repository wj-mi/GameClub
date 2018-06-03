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
                    1->9连续表示
筒 * 9 * 4 = 36      [0,9)                     #[ [0,9), [9,18), [18, 27), [27,36) ] 
条 * 9 * 4 = 36      [9,18)                    #[ [36,45), [45, 54), [54,63), [63,72) ]
万 * 9 * 4 = 36      [18,27)                   #[ [72,81), [81, 90), [90, 99), [99, 108) ]
中 * 4 = 4           27                        #[108,109,110,111]
发 * 4 = 4           28                        #[112,113,114,115]
白 * 4 = 4           29                        #[116,117,118,119]
共 120 张
"""

from gameDealer import GameDealer
import time


def time_count(func):
    def wrap(*args, **kwargs):
        begin = time.time()
        rest = func(*args, **kwargs)
        print 'run time: ', time.time() - begin
        return rest
    return wrap

server2client = {
    0:1,   1:2,   2:3, 3:4, 4:5, 5:6, 6:7, 7:8, 8:9,
    9:11,  10:12, 11:13, 12:14, 13:15, 14:16, 15:17, 16:18, 17:19,
    18:21, 19:22, 20:23, 21:24, 22:25, 23:26, 24:27, 25:28, 26:29,
    27:31,
    28:41,
    29:51
}

client2server = {
    1:0,  2:1,  3:2,  4:3,  5:4, 6:5,  7:6,  8:7,  9:8,
    11:9, 12:10, 13:11, 14:12, 15:13, 16:14, 17:15, 18:16, 19:17,
    21:18, 22:19, 23:20, 24:21, 25:22, 26:23, 27:24, 28:25, 29:26,
    31:27,
    41:28,
    51:29 
}

def changeServerclient(serverCard, changeType):
    """
    type == 0: server2client
    type == 1: client2server
    """
    findChange = None
    if changeType == 0:
        findChange = server2client
    else:
        findChange = client2server
    if type([]) == type(serverCard):
        return [ findChange[card] for card in serverCard ]
    else:
        return findChange[serverCard]


def _genAllCardSizeAndType(cards):
    info = {}
    for card in cards:
        cardType = card/9 if card < 27 else ((card - 27) + 27/9)
        cardSize = card%9 if card < 27 else 0
        info[card] = [cardSize, cardType]
    return info

ALLCARDSSIZEANDTYPE = _genAllCardSizeAndType(GameDealer.genNewCards())


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
    if size >= 2:
        findRet.append([cardInfo[1]*9+size-1, cardInfo[1]*9+size-2])
    # 前后各一张
    if size >= 1 and size <= 7:
        findRet.append([cardInfo[1]*9+size-1, cardInfo[1]*9+size+1])
    # after 2
    if size <= 6:
        findRet.append([cardInfo[1]*9+size+1, cardInfo[1]*9+size+2])
    return findRet

def _judgeCanChi(srcCards, card):
    """判断srcCards能否吃card牌
    如果card不是中发白,找card的 前2张|前后各1张|后2张
    3种情况满足其中的一种就可以
    """
    if card >= 27:
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

def judgeWanneng(srcCards, card, laizi):
    return _judgeWanneng(srcCards, card, laizi)

@time_count
def _judgeWanneng(srcCards, card, laizi):
    """
    万能牌
    :param srcCards:
    :param card:
    :param laizi: 万能牌
    :return: [] 0: 不能胡，　1：七对　２：3n+2 3:清一色
    """
    cards = srcCards[:]
    cards.append(card)
    # 癞子牌的张数
    laizi_count = 0 if laizi not in cards else cards.count(laizi)
    if laizi_count:
        for item in range(0, laizi_count):
            cards.remove(laizi)
    # 7对
    result = _all_double(cards, laizi_count)
    if result:
        return [result, _sameType(cards)]
    else:
        result = _judge_can_hu(cards, laizi_count)
        if result:
            return [result, _sameType(cards)]
        return [result, 0]


def _judge_can_hu(srcCards, count):
    """

    :param srcCards: 除去万能牌后的牌
    :param count:拥有万能牌张数
    :return:
    """
    result = 0
    cards = srcCards[:]
    tmp_match = {}
    need_num = 0  # 胡牌需要的万能牌张数

    for item in srcCards:
        if item not in cards:
            continue
        if cards.count(item) == 2:
            tmp_match[item] = 2
            __numric_remove(cards, item, 2)
        elif cards.count(item) == 3:
            tmp_match[item] = 3
            __numric_remove(cards, item, cards.count(item))
        elif cards.count(item) in [1, 4]:
            result = _judge_can_match(item, cards)
            if result:
                cards.remove(item)
    #print "after fist match cards: {}, tmp_match: {}, count={}".format(cards, tmp_match, count)
    # if tmp_match:   # 筛选，tmp_match里全是对子
    double_count = _count_double(tmp_match)
    if count == 0:
        if not cards and len(tmp_match) == 1 and double_count == 1:   # TODO
            return 2
        elif count > (len(cards) +double_count-1) and (count - len(cards) - double_count+1) % 2 == 0:
            result = 2
        else:
            return 0
    else:
        backup_cards = cards[:]
        for item in backup_cards:
            if item not in cards:
                continue
            result = _judge_can_match(item, tmp_match)
            if result:
                cards.remove(item)
            else:  # 若不能胡
                need_num += max_match(item, cards, tmp_match)
            if count < need_num:
                result = 0
                return result
        if not _count_double(tmp_match):  # 没有将牌
            if count < 2:
                return 2
            else:
                tmp_match[1] = 2
                count -= 2
        for k, v in tmp_match.items():
            if v in [1, 4]:
                cards.append(k)
                _remove_card(k, tmp_match)
        double_count = _count_double(tmp_match)
        if cards and (count-need_num) > 0:
            result = cycle_match(cards, tmp_match, count-need_num)
        elif not cards and (count-need_num-double_count+1)%2 == 0:
            result = 2
        else:
            result = 0
    return result


def _count_double(tmp_match):
    """返回对子的个数"""
    double_count = 0
    for k, v in tmp_match.items():
        if v == 2:
            double_count += 1
    return double_count


def _all_double(srcCards, count):
    """
    七对判断
    :param cards:
    :param count:
    :return:　０，１
    """
    double_count = 0
    cards = srcCards[:]
    for item in set(cards):
        if cards.count(item) >= 2:
            cards.remove(item)
            cards.remove(item)
            double_count += 1
        else:
            return 0
    if not count:
        if double_count == 7:
            return 1
        else:
            return 0
    else:
        if count < len(cards):
            result = 0
        elif (count - len(cards)) %2==0:
            result = 1
        else:
            result = 0
    return result


def cycle_match(cards, tmp_match,  count):
    need_num = 0
    backup_cards = cards[:]
    for item in backup_cards:
        if item not in cards:
            continue
        result = _judge_can_match(item, cards)
        if result:
            cards.remove(item)
        else:  # 若不能胡
            need_num += max_match(item, cards, tmp_match)
        if count < need_num:
            result = 0
            return result
    if not _count_double(tmp_match):  # 没有将牌
        if count < 2:
            return 2
        else:
            tmp_match[1] = 2
            count -= 2
    for k, v in tmp_match.items():
        if v in [1, 4]:
            cards.append(k)
            _remove_card(k, tmp_match)
    double_count = _count_double(tmp_match)
    if not cards and double_count == 1:  # TODO
        result = 2
    elif not cards and (count - need_num - double_count + 1) % 2 == 0:
        result = 2
    else:
        result = 0
    return result

def max_match(item, cards, tmp_match):
    """
    最大匹配，优先匹配单牌
    :param item:
    :param cards: []
    :param tmp_match: ｛｝
    :return:
    """
    # double_flag = _count_double(tmp_match)
    need_count = _conut_needed_cards(item, cards, tmp_match)
    if need_count[0] < 2:  # 需要一个牌
        result = need_count
        need_list = result[1]
        flag = False
        for needed in need_list:
            if needed in tmp_match:
                flag = True
                _remove_card(needed, tmp_match)
                break
        if flag:
            result = result[0] - 1
        else:
            result = result[0]
    else:
        need_count = _conut_needed_cards(item, tmp_match, tmp_match)
        if need_count[0] < 2:  # 需要一个牌
            result = need_count
            need_list = result[1]
            flag = False
            for needed in need_list:
                if needed in tmp_match:
                    flag = True
                    _remove_card(needed, tmp_match)
                    break
            if flag:
                result = result[0] - 1
            else:
                result = result[0]
        else:
            result = need_count[0]
    cards.remove(item)
    return result


def _conut_needed_cards(item, cards, tmp_match):
    """

    :param item:
    :param cards:
    :param tmp_match:
    :return: 本轮需要的万能牌张数
    """
    # inner.extend(tmp_match)
    inner_set = set(cards) if isinstance(cards, list) else tmp_match
    need_cards = 0
    wish_card = []  # 期望的牌
    flag = _count_double(tmp_match)
    if item > 27:
        if not flag:   # 没有对子
            need_cards += 1
            tmp_match[item] = 2
        else:
            need_cards += 2
    elif item % 9 == 8:
        if item - 1 in inner_set:
            need_cards += 1
            _remove_card(item-1, cards)
            wish_card.append(item - 2)
        elif item - 2 in inner_set:
            need_cards += 1
            _remove_card(item - 2, cards)
            wish_card.append(item - 1)
        else:
            need_cards += 2
    elif item % 9 == 0:
        if item + 1 in inner_set:
            need_cards += 1
            _remove_card(item + 1, cards)
            wish_card.append(item+2)
        elif item + 2 in inner_set:
            need_cards += 1
            _remove_card(item+2, cards)
            wish_card.append(item +1)
        else:
            need_cards += 2
    elif item % 9 == 7 or (item % 9) == 1:
        if item+1 in inner_set:
            need_cards += 1
            _remove_card(item+1, cards)
            wish_card.append(item-1)
        elif item - 1 in inner_set:
            need_cards += 1
            _remove_card(item -1, cards)
            wish_card.append(item+1)
        else:
            if (item % 9) == 7:
                if item - 2 in inner_set:
                    need_cards += 1
                    _remove_card(item - 1, cards)
                    wish_card.append(item-1)
                else:
                    need_cards += 2
            elif (item % 9) == 1:
                if item + 2 in inner_set:
                    need_cards += 1
                    _remove_card(item + 2, cards)
                    wish_card.append(item+1)
                else:
                    need_cards += 2
            else:
                need_cards += 2
    else:
        if item-2 in inner_set and item-1 not in inner_set:
            need_cards += 1
            _remove_card(item-2, cards)
            wish_card.append(item-1)
            # result = item-2
            # _remove_card_both(item - 1, cards, tmp_match)
        elif item-1 in inner_set and item+1 not in inner_set:
                need_cards += 1
                _remove_card(item - 1, cards)
                wish_card.append(item+1)
                wish_card.append(item+2)
                # result = item-1
        elif item + 1 in inner_set:
                need_cards += 1
                _remove_card(item + 1, cards)
                wish_card.append(item - 1)
                wish_card.append(item + 2)
                # result = item+1
        elif item + 2 in inner_set:
                need_cards += 1
                _remove_card(item + 2, cards)
                wish_card.append(item+1)
                # result = item+2
        else:
            if not _count_double(tmp_match):
                need_cards += 1
                tmp_match[item] = 2
            else:
                need_cards += 2
    return need_cards, wish_card


def _judge_can_match(card, cards):
    """
    单牌尝试匹配
    :param card:
    :param cards:
    :param tmp_match:
    :return:
    """
    result = False
    # inner = cards[:]
    inner_set = set(cards) if isinstance(cards, list) else cards
    if card > 27:       # 中发白
        return False
    if (card % 9) > 7 or (card % 9) < 1:
        result = False
    elif (card % 9) == 1 or (card % 9) == 7:
        if (card-1) in inner_set and (card+1) in inner_set:
            _remove_card(card-1, cards)
            _remove_card(card+1, cards)
            # result = card-1, card+1
            result = True
        elif (card%9) == 1 and (card+1) in inner_set and (card+2) in inner_set:
            _remove_card(card+1, cards)
            _remove_card(card+2, cards)
            result = True
        elif (card % 9) == 7 and (card - 1) in inner_set and (card - 2) in inner_set:
            _remove_card(card - 1, cards)
            _remove_card(card - 2, cards)
            result = True
        else:
            result = False

    else:
        if (card-2) in inner_set and (card-1) in inner_set:
            _remove_card(card-2, cards)
            _remove_card(card-1, cards)
            # result = card-2, card-1
            result = True
        elif (card-1) in inner_set and (card+1) in inner_set:
            _remove_card(card-1, cards)
            _remove_card(card+1, cards)
            # result = card-1, card+1
            result = True
        elif (card+1) in inner_set and (card+2) in inner_set:
            _remove_card(card+1, cards)
            _remove_card(card+2, cards)
            # result = card+1, card+2
            result = True
        else:
            result = False
    return result


def _remove_card(card, cards):
    try:
        cards.remove(card)
    except: # AttributeError as e:
        cards[card] -= 1
        if cards[card] <= 0:
            del cards[card]


def __numric_remove(cards, card, num):
   while num:
       cards.remove(card)
       num -= 1


def _sameType(cards):
    """
    清一色
    :param cards: 除去万能牌之后的牌
    :return: true/false
    """
    inner_cards = cards[:]
    one_type = -1
    for item in inner_cards:
        if one_type == -1:
            one_type = item / 9
        elif one_type != item / 9:
            return 0
    return 1



# def _judgeCanHu(srcCards):
#     """判断srcCards能否胡card牌
#     0:不能胡 | 1: 7对  |  2: 3n+2  |  ,  是否是清一色
#     2*7 | 3n+2两种牌型
#     """
#     cards = srcCards[:]
#     # cards.append(card)
#     allCardsInfo = [ALLCARDSSIZEANDTYPE[tmp] for tmp in cards]
#     # 7 pair
#     if len(cards) == 14:
#         allPair = True
#         for cardInfo in allCardsInfo:
#             if allCardsInfo.count(cardInfo) % 2 != 0:
#                 allPair = False; break;
#         if allPair: return 1
#     # normal
#     if len(cards) == 2:  # 只有两张牌
#         return cards[0] == cards[1]
#     # 先排序
#     cards.sort()
#     # 找到可以做将牌的牌
#     allSize = set(cards)
#     for tmp in allSize:
#         tmpCards = cards[:]
#         if tmpCards.count(tmp) >=2:
#             print "---jing ", tmp
#             tmpCards.remove(tmp)
#             tmpCards.remove(tmp)
#             if _judgeHu(tmpCards):
#                 return 2
#     return 0
#
#
def _judgeHu(cards):
    # 递归结束条件
    if len(cards) == 0: return True
    #print "+++ compare cards ", cards
    firstCard = cards[0]
    if cards.count(firstCard) == 3:    # 组成克子
        cards.remove(firstCard)
        cards.remove(firstCard)
        cards.remove(firstCard)
        return _judgeHu(cards)
    else:                   # 组成顺子
        if firstCard > 27 or firstCard % 9 >= 7:
            return False
        if (firstCard+1) in cards and (firstCard+2) in cards:
            cards.remove(firstCard)
            cards.remove(firstCard+1)
            cards.remove(firstCard+2)
            return _judgeHu(cards)
        return False


def judgePlayerAction(srcCards, card):
    info = {"peng":0, "gang":0, "chi":0, "hu":0}
    ret = _judgeCanGangOrPeng(srcCards, card)
    if ret == 1:
        info["peng"] = 1
    elif ret == 3:
        info["peng"] = 1
        info["gang"] = 1
    if len(_judgeCanChi(srcCards, card)) > 0:
        info["chi"] = 1
    if info["peng"] == 0 and info["gang"] == 0 and info["chi"] == 0 and info["hu"] == 0:
        return None
    info["hu"] = _judgeCanHu(srcCards, card)
    return info


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

    card1 = [41, 22, 15, 41, 18, 25, 25, 15, 19, 21, 24, 41, 11]

    card2 = [15, 51, 1, 21, 8, 8, 14, 16, 9, 15, 4, 11, 11]

    card3 = [29, 51, 12, 25, 4, 26, 14, 22, 19, 29, 13, 41, 22]

    print _judgeWanneng(card1, 15, -1)
    print _judgeWanneng(card2, 15, -1)
    print _judgeWanneng(card3, 15, -1)

