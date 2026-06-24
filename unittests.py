from unittest import main as ut_main
from unittest import skip, TestCase

from card import OKCard, OKRank, OKSuit
from cardset import OKCardSet
from deck import OKDeck, OKDeckConsts
import gc
from hand import OKHand, OKPokerRank, OKDealerHand
from listutils import *
import multiprocessing as mp
import numpy as np
import pandas as pd
from pydealer import Card
from tqdm import tqdm

def batch(batch_size: int):
	d = OKDeck()
	pdd = {
		k : [] for k in ['card1', 'card2', 'suited', 'force', 'qualifies', 'hrank']
	}
	for _ in range(batch_size):
		dh = OKDealerHand(from_set=d.deal(5))
		cs = [dh[k] for k in range(2)]											#dh.get_cards(ordered=False)
		pdd['card1'] += [str(cs[0])]
		pdd['card2'] += [str(cs[1])]
		pdd['suited'] += [cs[0].suit == cs[1].suit]
		pdd['force'] += [dh.forcing()]

		dh.draw(from_deck=d)
		pdd['qualifies'] += [dh.qualifies()]
		pdd['hrank'] += [str(dh.rank())]
	return pdd

@skip
class TestCard(TestCase):
	def test_str(self):
		"""Test __str__"""
		with self.subTest("OKSuit.__str__"):
			for s in OKSuit:
				print(f"{s.name}\t{s}")
		with self.subTest("OKRank.__str__"):
			for r in OKRank:
				print(f"{r.name}\t{r}")
		self.assertTrue(True)

	def test_to_from_pdlr(self):
		"""Test correct conversion to a str that creates a pydealer Card"""
		with self.subTest("OKSuit.[to|from]_pdlr"):
			for s in OKSuit:
				c = Card("Two", s.to_pdlr())
				self.assertIsInstance(c, Card)
				self.assertEqual(s, OKSuit.from_pdlr(c.suit))
		with self.subTest("OKRank.[to|from]_pdlr"):
			for r in OKRank:
				c = Card(r.to_pdlr(), "Spades")
				self.assertIsInstance(c, Card)
				self.assertEqual(r, OKRank.from_pdlr(c.value))

	def test_add(self):
		"""Test OKRank.__add__"""
		for k in range(13):
			self.assertEqual(OKRank.TWO + k, OKRank(2 + k))	
		with self.assertRaises(ValueError):
			_ = OKRank.TWO + 13

@skip
class TestCardset(TestCase):
	def setUp(self):
		self.d = OKDeck()

	def test_cards(self):
		h = self.d.deal(5)
		with self.subTest("unordered cards"):
			print(" ".join([str(c) for c in h.get_cards(ordered=False)]))
			self.assertTrue(True)

		with self.subTest("ordered cards"):
			print(" ".join([str(c) for c in h.get_cards(ordered=True)]))
			self.assertTrue(True)

	def test_len(self):
		"""Ensure that OKCardSet.__len__ works"""
		self.d.deal_one()
		self.assertEqual(len(self.d), OKDeckConsts.DEFAULT_N_DECKS * 52 - 1)

	def test_n_wilds(self):	
		"""Ensure that OKCardSet.n_wilds works"""
		k = int(self.d.deal_one().is_wild())
		self.assertEqual(self.d.n_wilds(), OKDeckConsts.DEFAULT_N_DECKS * 4 - k)

	def test_deal(self):
		h = self.d.deal(5)
		"""Deal a hand; ensure that lengths of deck and hand are correct and that list members are instances of the expected classes"""
		with self.subTest("deal() yields OKCard"):
			self.assertIsInstance(h[0], OKCard)
		
		with self.subTest("len(self.h)"):
			self.assertEqual(len(h), 5)
		with self.subTest("len(deck)"):
			self.assertEqual(len(self.d), OKDeckConsts.DEFAULT_N_DECKS * 52 - 5)

	def test_by_rank(self):
		_d = self.d.by_rank()
		self.assertEqual(len(_d), 13)

	def test_by_suit(self):
		_d = self.d.by_suit()
		self.assertEqual(len(_d), 4)

	def test_add(self):
		okcs = OKCardSet()
		with self.subTest("adding pydealer.card.Cards"):
			okcs.add_cards([Card("2", "Diamonds")])
			self.assertEqual(len(okcs), 1)
		with self.subTest("adding Cards"):
			okcs.add_cards([OKCard(OKSuit.SPADES, OKRank.TWO)])
			self.assertEqual(okcs.n_wilds(), 2)
		with self.subTest("creating new OKCardSets with list"):
			okcs2 = okcs.add_cards(okcs.cards, inplace=False)
			okcs3 = okcs.add_cards(okcs.get_cards(), inplace=False)
			self.assertEqual(len(okcs), 2)
			self.assertEqual(len(okcs2), 4)
			self.assertEqual(len(okcs3), 4)
			okcs4 = okcs.add_cards(okcs.get_cards(), inplace=True)
			self.assertEqual(len(okcs3), 4)
			self.assertEqual(len(okcs4), len(okcs))

@skip
class TestDeck(TestCase):
	def test_shuffleright(self):
		d = OKDeck()
		N = d.initial_n_cards()
		n_trials = 1000
		L = []
		for nt in tqdm(range(n_trials), desc="Reshuffles", colour="#00DD44", ncols=80):
			L += [0]
			d.deal_one()
			while not d.should_shuffle:
				d.deal_one()
				L[-1] += 1
		mu = N / 2
		sigma = np.sqrt((N ** 2) / (108 * n_trials))
		z = (np.mean(L) - mu) / sigma
		print(f"z = {z}")
		self.assertTrue(-2 < z and z < 2)
			
@skip
class TestHand(TestCase):
	def test_rank_freq(self):
		base_n_per_rank = 14
		rd = {
			r : base_n_per_rank - r.value for r in OKPokerRank
		}
		hd = {
			r : [] for r in OKPokerRank
		}
		nd = {
			r : 0 for r in OKPokerRank
		}
		d = OKDeck()
		total_n_ranks = len(rd)
		total_n_hands = 0
		while any([rd[k] > 0 for k in rd]):
			h = OKHand(from_set=d.deal(5))
			total_n_hands += 1
			r = h.rank()
			nd[r] += 1
			if rd[r] > 0:
				hd[r] += [h]
				rd[r] -= 1
				if rd[r] == 0:
					finished_n_ranks = sum([1 for k in rd if rd[k] == 0])
					print(f"{finished_n_ranks} / {total_n_ranks} ranks complete")
			if r == OKPokerRank.FIVE_DEUCES:
				print(f"Remaining five-deuce hands to find: {rd[r]} / {base_n_per_rank - OKPokerRank.FIVE_DEUCES.value}")
		
		with open("data/sample_hands.txt", "w") as fp:
			for r in OKPokerRank:
				print(f"{r}:", file=fp)
				for h in hd[r]:
					print(f"{h}", file=fp)
				print("\n", file=fp)
		
		df = pd.DataFrame.from_dict(nd, orient="index", columns=["n_hands"])
		with open("data/rank_stats.csv", "w") as fp:
			df.to_csv(fp, sep="\t")
		
		self.assertTrue(True)
	
	def test_draw(self):
		d = OKDeck()
		with open("data/draws.txt", "w") as fp:
			for n in range(100):
				dh = OKDealerHand(from_set=d.deal(5))
				print(f"[[Hand {n}]]\nBefore draw:\n{dh}\n[{dh.rank()}]\n", file=fp)
				dh.draw(from_deck=d)
				print(f"After draw:\n{dh}\n[{dh.rank()}]\n\n", file=fp)
		self.assertTrue(True)
	
	def test_dealer(self):
		gc.enable()
		df = pd.DataFrame()
		ncpus = mp.cpu_count() - 1
		n_hands = 5 * (10 ** 4)
		batch_size = 10 ** 3

		print(f"*** test_dealer: using {ncpus} CPUs ... ***")
		with mp.Pool(processes=ncpus) as P:
			L = [P.apply_async(batch, (batch_size, )) for _ in range(n_hands // batch_size)]
			for x in tqdm(L):
				df = pd.concat([df, pd.DataFrame.from_dict(x.get())])
				with open("data/dealer_stats.csv", "w") as fp:
					df.to_csv(fp, sep="\t")
		self.assertTrue(True)

class TestListUtils(TestCase):
	def test_listutils(self):
		A = [1, 2, 3]
		B = [3, 4]
		C = [0, 3, 4]
		D = []

		with self.subTest("add_lists"):
			self.assertTrue(add_lists([A, B]) == [1, 2, 3, 4])
			self.assertTrue(add_lists([A, D]) == A)
			self.assertTrue(add_lists([A, B, C, D]) == list(range(5)))

		with self.subTest("int_lists"):
			self.assertTrue(int_lists([A, B]) == [3])
			self.assertTrue(int_lists([A, B, C]) == [3])
			self.assertTrue(int_lists([A, D]) == D)

		with self.subTest("invert_list"):
			self.assertTrue(invert_list(A) == [0, 4])
			self.assertTrue(invert_list(D) == list(range(5)))
		
		with self.subTest("cmp_lists"):
			self.assertTrue(cmp_lists(A, B) == -1)
			self.assertTrue(cmp_lists(A, C) == -1)
		
if __name__ == "__main__":
	ut_main(verbosity=3)	

