from __future__ import annotations

from cardset import OKCardSet
from enum import IntEnum
from pydealer.tools import build_cards
from random import randint

class OKDeckConsts(IntEnum):
	DEFAULT_N_DECKS = 8

class OKDeck(OKCardSet):
	def __init__(self, n_decks: int = OKDeckConsts.DEFAULT_N_DECKS):
		self.card_list = []
		for _ in range(n_decks):
			self.card_list += build_cards()
		super().__init__()
		self.should_shuffle = True
		self.shuffle_after = None

	def build(self):
		"""Rebuild self.cards and insert a shuffle card"""
		self.cards = self.card_list
		self.shuffle_after = randint(self.initial_n_cards() // 3, 2 * self.initial_n_cards() // 3)
		self.should_shuffle = False

	def initial_n_cards(self) -> int:
		return len(self.card_list)

	def deal(self, n_cards: int) -> OKCardSet:
		if self.should_shuffle:
			self.build()
			self.shuffle()
		
		dealt = super().deal(n_cards)
		self.should_shuffle = (len(self) < self.shuffle_after)
		return dealt

	def deal_one(self) -> OKCard:
		return self.deal(1)[0]

if __name__ == "__main__":
	d = OKDeck()
	print("[Printing deck ...]")
	print(d)
	print("\n[Printing hand ...]")
	h = d.deal(13)
	print(h)
#	print(h.by_rank())
#	print(h.by_suit())
