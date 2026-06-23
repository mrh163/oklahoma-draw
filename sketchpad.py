from pydealer.card import Card
from cardset import OKCardSet
from deck import OKDeck
from hand import OKDealerHand

if __name__ == "__main__":
    dh = OKDealerHand.from_str("C2D22H2S2")
    print(f"forcing = {dh.forcing()}")
    # print(f"*** old hand ***\n{dh}")
    # d = OKDeck()
    # dh.draw(from_deck=d)
    # print(f"\n*** new hand ***\n{dh}")