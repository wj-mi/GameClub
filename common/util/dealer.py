# -*- coding:UTF-8 -*-
"""
负责发牌
"""

# 数据结构
# 0-12   # 红桃2-A
# 13-25  # 梅花2-A
# 26-38  # 黑桃2-A
# 39-51  # 方片2-A

import random

class Dealer(object):
	def __init__(self):
		self._initCards()

	def _initCards(self):
		#
		self._card = [ card for card in range(0, 13*4*2+2*2) ]
		self._shuffle()
		return
		self._card = []
		for i in range(13):
		    for j in range(8):
			self._card.append(i+13*j)
		self._card.append(104)
		self._card.append(105)
		self._card.append(106)
		self._card.append(107)


	def _shuffle(self):
		random.shuffle(self._card)	
		#self._card = [51, 34, 7, 5, 8, 35, 27, 47, 33, 46]

	def reinit(self):
		"""重新初始化一副牌
		"""
		self._initCards()


	def deal(self):
		"""发牌
		"""
		return self._card.pop()
