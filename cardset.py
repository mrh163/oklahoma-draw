from __future__ import annotations

from card import OKCard, OKRank, OKSuit
from pydealer.card import Card
from pydealer.stack import Stack
import re
from typing import Optional, Union

class OKCardSet(Stack):
	def __init__(self, from_list: Union[list[Card], list[OKCard]] = []):
		super().__init__()
		if len(from_list) > 0 and type(from_list[0]) is OKCard:	
			from_list = [c.to_pdlr() for c in from_list]
		self.cards = from_list

	def pdlr_cards(self, ordered: bool = True) -> list[Card]:
		"""Return list of pydealer.card.Cards"""
		st = Stack()
		st.add(self.cards)
		if ordered:
			st.sort()
		L = st.cards
		L.reverse()
		return L

	def get_cards(self, ordered: bool = True) -> list[OKCard]:
		"""Return list of OKCards"""
		return [OKCard.from_pdlr(c) for c in self.pdlr_cards(ordered=ordered)]

	def __len__(self):
		return len(self.cards)

	def n_wilds(self) -> int:
		return sum([1 if c.is_wild() else 0 for c in self.get_cards()])

	def __getitem__(self, k: int) -> OKCard:
		return OKCard.from_pdlr(self.cards[k])

	def deal(self, n_cards: int) -> OKCardSet:
		return OKCardSet(from_list = super().deal(n_cards))

	def deal_one(self) -> OKCard:
		return self.deal(1)[0]

	def by_rank(self) -> dict[OKRank]:
		return {
			r : [OKCard.from_pdlr(self.cards[j]).s for j in self.find(r.to_pdlr(), sort=True)]
			for r in OKRank
		}

	def by_suit(self) -> dict[OKSuit]:
		return {
			s : [OKCard.from_pdlr(self.cards[j]).r for j in self.find(s.to_pdlr(), sort=True)]
			for s in OKSuit
		}

	def add_cards(self, from_list: Union[list[Card], list[OKCard]], inplace: bool = True) -> OKCardSet:
		if len(from_list) > 0 and type(from_list[0]) is OKCard:
			from_list = [c.to_pdlr() for c in from_list]
		if inplace:
			self.cards += from_list
			return self
		else:
			okcs = OKCardSet(from_list = self.cards)
			return okcs.add_cards(from_list)

	def non_wilds(self) -> list[OKCard]:
		return [c for c in self.get_cards() if not c.is_wild()]
		
	@classmethod
	def from_str(cls, s: str) -> OKCardSet:
		s = s.lower()
		R = re.compile('c(?P<Clubs>[tjqka\\d]*)d(?P<Diamonds>[tjqka\\d]*)h(?P<Hearts>[tjqka\\d]*)s(?P<Spades>[tjqka\\d]*)')
		m = R.match(s)
		if m is None:
			raise Exception(f"'{s}' could not be parsed as an OKCardSet")
		d = m.groupdict()
		cards = []
		ranks = '  23456789tjqka'
		for suit in d:
			try:
				rs = d[suit]
				rix = [ranks.index(c) for c in d[suit]]
				cards += [OKCard(OKSuit[suit.upper()], OKRank(ix)) for ix in rix]
			except ValueError:
				raise Exception(f"The string passed for {suit}, '{rs}', contains characters that do not correspond to any OKRank") from None
		return OKCardSet(from_list=OKCardSet(cards))
	
	def __str__(self):
		bys = self.by_suit()
		x = ""
		for s in bys:
			x += f"{s}: "
			if len(bys[s]) == 0:
				x += "-"
			else:
				for r in bys[s]:
					x += f"{r}"
			x += "\n"
		return x
