from __future__ import annotations

from enum import auto, IntEnum
from pydealer.card import Card

class OKSuit(IntEnum):
	"""Enum representing a card suit."""
	CLUBS = auto()
	DIAMONDS = auto()
	HEARTS = auto()
	SPADES = auto()

	def __str__(self):
		if self == OKSuit.CLUBS:
			return "\u2663"
		elif self == OKSuit.DIAMONDS:
			return "\u2662"
		elif self == OKSuit.HEARTS:
			return "\u2661"
		elif self == OKSuit.SPADES:
			return "\u2660"
		assert False, f"Suit not found"

	def to_pdlr(self) -> str:
		"""Convert to string used for initializing a pydealer Card."""
		_d = {
			OKSuit.CLUBS: "Clubs",
			OKSuit.DIAMONDS: "Diamonds",
			OKSuit.HEARTS: "Hearts",
			OKSuit.SPADES: "Spades"
		}
		return _d[self]

	@classmethod
	def from_pdlr(cls, suit: str) -> OKSuit:
		_d = {
			"clubs": OKSuit.CLUBS,
			"diamonds": OKSuit.DIAMONDS,
			"hearts": OKSuit.HEARTS,
			"spades": OKSuit.SPADES
		}
		if suit.lower() not in _d:
			suits = ", ".join([f"'{s}'" for s in _d])
			raise Exception(f"'{suit}' is not a valid string corresponding to an OKSuit (valid strings: {suits})")

		return _d[suit.lower()]

class OKRank(IntEnum):
	"""Enum representing a card rank."""
	TWO = 2
	THREE = 3
	FOUR = 4
	FIVE = 5
	SIX = 6
	SEVEN = 7
	EIGHT = 8
	NINE = 9
	TEN = 10
	JACK = 11
	QUEEN = 12
	KING = 13
	ACE = 14
	
	def __str__(self):
		if self.value < 10:
			return str(self.value)
		return self.name[0]

	def to_pdlr(self) -> str:
		"""Convert to string used for initializing a pydealer Card."""
		if self.value < 10:
			return str(self)
		elif self.value == 10:
			return "10"
		return self.name[0] + self.name[1:].lower()

	@classmethod
	def from_pdlr(cls, value: str):
		_d = {
			"2": OKRank.TWO,
			"3": OKRank.THREE,
			"4": OKRank.FOUR,
			"5": OKRank.FIVE,
			"6": OKRank.SIX,
			"7": OKRank.SEVEN,
			"8": OKRank.EIGHT,
			"9": OKRank.NINE,
			"10": OKRank.TEN,
			"Jack": OKRank.JACK,
			"Queen": OKRank.QUEEN,
			"King": OKRank.KING,
			"Ace": OKRank.ACE
		}
		return _d[value]

	def __add__(self, right: int) -> OKRank:
		return OKRank(self.value + right)

class OKCard(Card):
	"""Superclass of pydealer Card."""
	def __init__(self, s: OKSuit, r: OKRank):
		super().__init__(r.to_pdlr(), s.to_pdlr())
		self.s = s
		self.r = r

	def __str__(self):
		return f"{self.s}{self.r}"

	def is_wild(self) -> bool:
		return self.r == OKRank.TWO

	def to_pdlr(self) -> Card:
		"""Obtain (copy of) underlying pydealer Card."""
		return Card(self.r.to_pdlr(), self.s.to_pdlr())		

	@classmethod
	def from_pdlr(cls, c: Card) -> OKCard:
		"""Obtain OKCard from pydealer Card."""
		return cls(OKSuit.from_pdlr(c.suit), OKRank.from_pdlr(c.value))

	@classmethod
	def card_it(cls):
		"""Iterator for OKCard."""
		return OKCards()
			
class OKCards:
	"""Iterator for OKCard."""
	def __iter__(self):
		self.its = iter(OKSuit)
		self.itr = iter(OKRank)
		self.s = self.r = None
		return self

	def __next__(self):
		if self.r == OKRank.ACE:
			self.itr = iter(OKRank)
		self.r = next(self.itr)
		if self.r == OKRank.TWO:
			if self.s == OKSuit.SPADES:	
				raise StopIteration
			self.s = next(self.its)
		return OKCard(self.s, self.r)

if __name__ == "__main__":
	okcs = OKCards()
	for c in okcs:
		print(c)
