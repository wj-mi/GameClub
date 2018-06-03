# coding:utf-8

import random
"""
                    1->9连续表示
筒 * 9 * 4 = 36      [0,9)   #[ [0,9), [9,18), [18, 27), [27,36) ] 
条 * 9 * 4 = 36      [9,18)  #[ [36,45), [45, 54), [54,63), [63,72) ]
万 * 9 * 4 = 36      [18,27) #[ [72,81), [81, 90), [90, 99), [99, 108) ]
中 * 4 = 4           [27,28,29,30] #[108,109,110,111]
发 * 4 = 4           [31,32,33,34] #[112,113,114,115]
白 * 4 = 4           [35,36,37,38] #[116,117,118,119]
共 120 张
"""

class GameDealer(object):
    def __init__(self):
        self._initCards()


    def _initCards(self):
        self._card = GameDealer.genNewCards()
        random.shuffle(self._card)  
        #random.shuffle(self._card)  
        random.shuffle(self._card)  
        #random.shuffle(self._card)  
        #random.shuffle(self._card)  
        # self._shuffle()
        # self._shuffle()
        # self._shuffle()
        #
        # hu
        # self._card = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 21 ]
        # self._card.extend([ 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 22 ])
        # self._card.extend([ 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 22 ])
        # self._card.extend([ 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 22 ])
        # self._card.extend([21,21,21])
        # self._card.extend([23, 24, 25, 26, 27, 28, 29, 23, 24, 25, 26, 27, 28, 29, 14,15,16,17,18,19,14,15,16,17,18,19])
        # self._card.extend([])
        #
        # tmp = [27, 12, 15, 18, 19, 24, 30, 3, 6, 11, 39]
        # for i in range(11):
        #   self._card[-(i+1)] = tmp[i]
    @staticmethod
    def genNewCardsAll():
        cards = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29] * 4
        cards.extend([31, 41, 51]*4)
        return cards

    @property 
    def notUseCards(self): return self._card

    def _shuffle(self):
        random.shuffle(self._card)  
        #self._card = [51, 34, 7, 5, 8, 35, 27, 47, 33, 46]
        pass
    @staticmethod
    def genNewCards():
        cards = [31, 41, 51]*4
        card1 = [ 1,22,13, 5,14,26, 18, 27,9 ]
        card2 = [11,2,23, 4,25,16, 7, 28, 19]
        card3 = [21,12,3, 24,15,6, 17, 8, 29]
        tmp = [ card1, card2, card3 ]
        for i in range(4):
            random.shuffle(tmp)
            tmp0, tmp1, tmp2 = tmp[0], tmp[1], tmp[2]
            #random.shuffle(tmp0)
            #random.shuffle(tmp1)
            #random.shuffle(tmp2)
            for index in range(len(tmp0)):
                cards.append(tmp0[index])
                cards.append(tmp1[index])
                cards.append(tmp2[index])


        #for i in range(3):
        #    random.shuffle(cards)
        # normal
        #cards = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29] * 4
        #cards.extend([31, 41, 51]*4)
        #
        #
        # # gang
        # cards = [1,1,1, 2,2,2, 3,3,3, 4,4,4, 5,5,5, 6,6,6, 7,7,7, 8,8,8, 9,9,9]
        # cards.extend([11,11,11, 12,12,12, 13,13,13, 14,14,14, 15,15,15, 16,16,16, 17,17,17, 18,18,18, 19,19,19])
        # cards.extend([1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18,19])
        # cards.extend([21,21,21,21, 22,22,22,22, 23,23,23,23, 24,24,24,24, 25,25,25,25, 26,26,26,6, 27,27,27,27, 28,28,28,28, 29,29,29,29])
        # cards.extend([31, 41, 51]*4)
        # cards.reverse()
        # # hu
        # cards = [28,28,28]
        # cards.extend([1,1,1,1, 2,2,2,2, 3,3,3,3, 4 ]) #,4,4,4, 5,5,5,5, 6,6,6,6, 7,7,7,7, 8,8,8,8, 9,9,9,9]
        # cards.extend([11,11,11,11, 12,12,12,12, 13,13,13,13, 14 ]) #14,14,14, 15,15,15,15, 16,16,16,16, 17,17,17,17, 18,18,18,18, 19,19,19,19])
        # cards.extend([21,21,21,21, 22,22,22,22, 23,23,23,23, 24]) #,24,24,24, 25,25,25,25, 26,26,26,6, 27,27,27,27, 28,28,28,28, 29,29,29,29])
        # cards.extend([25,25,25,25, 26,26,26,6, 27,27,27,27, 28])
        # # qianggang 
        # cards = [9,5, 28,26,27,5, 5]
        # cards.extend([6,7, 12,12,12, 13,13,13, 14,14,14, 15, 15])  # B 
        # cards.extend([1,1,1, 2,2,2, 3,3,3, 4,4,4, 5])   # A 
        # cards.extend([26,26,26, 27,27,27, 29,29,29, 8,8,8, 41])  # D
        # cards.extend([21,21,21, 22,22,22, 23,23,23, 24,24,24, 25])  # C 
        # card1 = [6, 13, 31, 1, 41, 22, 26, 51, 4, 8, 7, 5, 29]
        # card2 = [3, 13, 4, 51, 21, 51, 6, 29, 18, 9, 24, 15, 28]
        # card3 = [1, 12, 15, 1, 21, 11, 2, 41, 22, 16, 9, 12, 9]
        # card4 = [3, 17, 24, 27, 31, 29, 18, 28, 13, 19, 7, 23, 24]
        # cards1 = 28
        # cards2 = 
        
        return cards

    def reinit(self):
        """重新初始化一副牌
        """
        self._initCards()

    def getLaizi(self):
        return self._card[ random.randint(0, len(self._card)-1) ]

    def deal(self):
        """发牌
        """
        #card = self._card.pop()
        #if len(self._card) > 1:
        #    self._card.insert(0, self._card.pop())
        #return card
        return self._card.pop()

if __name__ == "__main__":
    dealer = GameDealer();
    dealer.reinit()
    print dealer.notUseCards




    # 26, 26, 1, 11, 14, 19, 19, 16, 2, 5, 7, 8, 29, 16
