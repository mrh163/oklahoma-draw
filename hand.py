from __future__ import annotations

from card import OKCard, OKRank, OKSuit
from cardset import OKCardSet
from deck import OKDeck
from enum import IntEnum
from listutils import *
import json
from typing import Optional

class OKPokerRank(IntEnum):
	HIGH_CARD = 0
	ONE_PAIR = 1
	TWO_PAIR = 2
	THREE_OF_A_KIND = 3
	STRAIGHT = 4
	FLUSH = 5
	FULL_HOUSE = 6
	FOUR_OF_A_KIND = 7
	STRAIGHT_FLUSH = 8
	ROYAL_FLUSH = 9
	FIVE_OF_A_KIND = 10
	FOUR_DEUCES = 11
	FIVE_DEUCES = 12

	def __str__(self):
		return self.name.replace("_", " ").lower().title()

class OKHand(OKCardSet):
	def __init__(self, from_set: Optional[OKCardSet] = None):
		from_list = from_set.pdlr_cards(ordered=False) if from_set is not None else []
		super().__init__(from_list)

	def search(self, terms, inverse: bool = False) -> list[int]:
		L = super().find(term=terms, sort=True)
		L.reverse()
		if inverse:
			return invert_list(L)
		return L

	def search_wilds(self, inverse: bool = False) -> list[int]:
		return self.search("2", inverse=inverse)

	def natural_pairs_or_better(self, include_singletons: bool = False) -> dict[OKRank]:
		"""Return dictionary mapping any ranks with natural pair or better to their # of cards."""
		byr = self.by_rank()
		d = {}
		for r in byr:
			lr = len(byr[r])
			if r == OKRank.TWO or (not include_singletons and lr < 2)
				continue
			d.update({r : lr})
		return d

	def natural_pairs_or_better_lens(self) -> list[int]:
		npob = sorted(list(self.natural_pairs_or_better().values()))
		npob.reverse()
		return npob

	def has_natural_pair_or_better(self) -> bool:
		return len(self.natural_pairs_or_better_lens()) > 0

	def npob_by_length(self) -> dict:
		npob = self.natural_pairs_or_better(include_singletons=True)
		return {npob[k] : k for k in sorted(npob, key = lambda k: 100 * npob[k] + k.value, reverse = True)}

	def highest_rank(self) -> OKRank:
		"""Return highest rank in hand"""
		byr = self.by_rank()
		return max([r for r in byr if len(byr[r]) > 0])

	def lowest_rank(self) -> OKRank:
		"""Return lowest non-deuce rank in hand"""
		byr = self.by_rank()
		return min([r for r in byr if (r != OKRank.TWO and len(byr[r]) > 0)])

	def range(self) -> int:
		return self.highest_rank().value - self.lowest_rank().value
		
	def straight(self) -> Optional[OKRank]:
		"""Return rank of high card in straight, if any, otherwise None"""
		if self.range() > 4 or self.has_natural_pair_or_better():
			return None	
		return OKRank(min([self.lowest_rank().value + 4, OKRank.ACE.value]))

	def flush(self) -> Optional[OKSuit]:
		"""Return suit of flush, if any, otherwise None"""
		bys = self.by_suit()
		for s in bys:
			cards_of_suit = OKCardSet(from_list=[OKCard(s, r) for r in bys[s]])	
			if len(cards_of_suit) + self.n_wilds() == 5 + cards_of_suit.n_wilds():
				return s
		return None

	def rank(self) -> OKPokerRank:
		nw = self.n_wilds()
		if nw == 5:
			return OKPokerRank.FIVE_DEUCES
		elif nw == 4:
			return OKPokerRank.FOUR_DEUCES

		sf_mask = 2*int(self.flush() is not None) + 1*int(self.straight() is not None)
		sf_d = {
			0 : OKPokerRank.HIGH_CARD,
			1 : OKPokerRank.STRAIGHT,
			2 : OKPokerRank.FLUSH,
			3 : OKPokerRank.STRAIGHT_FLUSH
		}

		lens = self.natural_pairs_or_better_lens()
		npob_dist = [nw]
		if len(lens) > 0:
			npob_dist[0] += lens[0]
			npob_dist += lens[1:]
		else:
			npob_dist[0] += 1
	
		npob_rank = OKPokerRank.HIGH_CARD
		if npob_dist == [5]:
			return OKPokerRank.FIVE_OF_A_KIND
		elif npob_dist == [4]:
			npob_rank = OKPokerRank.FOUR_OF_A_KIND
		elif npob_dist == [3, 2]:
			npob_rank = OKPokerRank.FULL_HOUSE
		elif npob_dist == [3]:
			npob_rank = OKPokerRank.THREE_OF_A_KIND
		elif npob_dist == [2, 2]:
			npob_rank = OKPokerRank.TWO_PAIR
		elif npob_dist == [2]:
			npob_rank = OKPokerRank.ONE_PAIR

		sf_rank = sf_d[sf_mask]
		if sf_rank == OKPokerRank.STRAIGHT_FLUSH and self.straight() == OKRank.ACE:
			sf_rank = OKPokerRank.ROYAL_FLUSH

		return max([sf_rank, npob_rank])

	def qualifies(self) -> bool:
		r = self.rank()
		if r > OKPokerRank.ONE_PAIR:
			return True
		elif r < OKPokerRank.ONE_PAIR or self.highest_rank() < OKRank.ACE:
			return False
		elif self.n_wilds() > 0:
			return True
	
		config = json.load(open("config.json", "r"))
		lowest_qualifying_kicker = OKRank(config["lowest_qualifying_kicker"])
		kickers = [c for c in self.get_cards() if c.r >= lowest_qualifying_kicker and c.r != OKRank.ACE]
		return len(kickers) > 0

	def replace(self, ixL: list[int], from_deck: OKDeck):
		self -= ixL
		self.add_cards(from_list = from_deck.deal(len(ixL)), inplace=True)

	@classmethod
	def from_str(cls, s: str) -> OKHand:
		return OKHand(from_set=OKCardSet.from_str(s))
	
	def __sub__(self, ixL: list[int]):
		"""Return new hand with cards at given indices removed."""
		newokh = OKHand(from_set=self)
		for ix in sorted(ixL, reverse=True):
			del newokh.cards[ix]
		return newokh
	
	def __isub__(self, ixL: list[int]):
		"""Remove cards at given indices from hand."""
		for ix in sorted(ixL, reverse=True):
			del self.cards[ix]
		return self

	def __lt__(self, right: OKHand):
		if self.rank() < right.rank():
			return True

		npob_bl = self.npob_by_length()
		npob_bl2 = right.npob_by_length()
	
	
	
class OKDealerHand(OKHand):
	def __init__(self, from_set: Optional[OKCardSet] = None):
		super().__init__(from_set=from_set)

	def draw(self, from_deck: OKDeck):
		wilds = self.search_wilds()
		nonwilds_to_keep = []
		nw = len(wilds)
		current_r = self.rank()

		if nw == 5:
			return
		elif nw == 4:
			pass
		elif nw >= 2:
			if current_r >= OKPokerRank.STRAIGHT_FLUSH:
				return
			else:
				pass
		elif current_r >= OKPokerRank.STRAIGHT and current_r != OKPokerRank.FOUR_OF_A_KIND:
			return
		elif not self.has_natural_pair_or_better():
			drawn = False
			bys = self.by_suit()
			for s in bys:
				byss = bys[s]
				if len(byss) >= 4:
					nonwilds_to_keep = self.search(s.to_pdlr(), inverse=False)
					drawn = True
					break
			if not drawn:
				byr = sorted(self.by_rank())
				for r in byr:
					if r == OKRank.TWO:
						continue
					card_ix = self.search(r.to_pdlr())
					wo_card = self - card_ix
					if wo_card.range() == 3:
						nonwilds_to_keep = self.search(r.to_pdlr(), inverse=True)
						drawn = True
						break
				if not drawn:
					if self.highest_rank() == OKRank.ACE:
						ace_ix = self.search("Ace")
						king_ix = self.search("King")
						queen_ix = self.search("Queen")
						kicker_ix = king_ix if len(king_ix) > 0 else queen_ix
						nonwilds_to_keep = add_lists([ace_ix, kicker_ix])

		npob = self.natural_pairs_or_better().keys()
		L = []
		for r in npob:
			L.append(self.search(r.to_pdlr(), inverse=False))
		nonwilds_to_keep += add_lists(L)

		self.replace(invert_list(add_lists([wilds, nonwilds_to_keep])), from_deck=from_deck)

	def forcing(self) -> int:
		dealer_cards = [self[k] for k in range(2)]
		#print(type(dealer_cards[0]))	OKCard
		if dealer_cards[0].is_wild():
			return 1
		elif dealer_cards[1].is_wild():
			return 2
		elif dealer_cards[0].r == dealer_cards[1].r:
			return 2
		elif min([dealer_cards[0].r, dealer_cards[1].r]) >= OKRank.QUEEN:
			return 2
		elif min([dealer_cards[0].r, dealer_cards[1].r]) >= OKRank.TEN and (dealer_cards[0].s == dealer_cards[1].s):
			return 2
		return 0
		
	@classmethod
	def from_str(cls, s: str) -> OKDealerHand:
		return OKDealerHand(from_set=OKCardSet.from_str(s))
