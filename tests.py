import unittest
import black_jack as bj


class TestBlackJackBasics(unittest.TestCase):
    """
    This group of tests check low-level mechanics, such as:
        objects creation, objects initialization, class methods working, class values counting.
    """
    def setUp(self) -> None:
        self.table = bj.GameTable(bj.Player('Dealer', 5000), bj.Player('Player', 1000))
        self.deck = bj.Deck(deck_type=52)
        self.deck.shuffle()

    def test_game_table_created(self):
        self.assertTrue(isinstance(self.table, bj.GameTable))

    def test_game_table_dealer_name(self):
        self.assertEqual(self.table.dealer.name, 'Dealer')

    def test_game_table_dealer_money(self):
        self.assertEqual(self.table.dealer.money, 5000)

    def test_game_table_player_name(self):
        self.assertEqual(self.table.player.name, 'Player')

    def test_game_table_player_money(self):
        self.assertEqual(self.table.player.money, 1000)

    def test_deck_length(self):
        self.assertEqual(len(self.deck), 52)

    def test_deck_contains_all_cards(self):
        full_deck = []
        for rank in bj.global_card_ranks:
            for suit in bj.global_card_suits:
                full_deck.append(bj.Card(suit, rank))

        while len(self.deck) > 0:
            card = self.deck.get_card()
            for i in range(len(full_deck)):
                if full_deck[i] == card:
                    full_deck.pop(i)
                    break

        for deck in [self.deck, full_deck]:
            with self.subTest(deck=deck):
                self.assertEqual(len(deck), 0)

    def test_deck_can_give_a_card(self):
        card = self.deck.get_card()

        self.assertNotIn(card, self.deck)


class TestBlackJackGame(unittest.TestCase):
    """
    This group of tests check game logic.
    """
    def setUp(self) -> None:
        self.table = bj.GameTable(bj.Player('Dealer', 5000), bj.Player('Player', 1000))
        self.deck = bj.Deck(deck_type=52)
        self.deck.shuffle()

    def test_make_a_bet(self):
        self.table.make_a_bet(500)
        with self.subTest('player.money'):
            self.assertEqual(self.table.player.money, 500)
        with self.subTest('dealer.money'):
            self.assertEqual(self.table.dealer.money, 4500)
        with self.subTest('bank'):
            self.assertEqual(self.table.bank, 1000)

    def test_make_a_bet_more_than_cash(self):
        with self.assertRaises(ValueError):
            self.table.make_a_bet(1001)

    def test_make_a_bet_more_than_bank(self):
        self.table.player.money += 10_000
        with self.assertRaises(ValueError):
            self.table.make_a_bet(5001)

    def test_make_a_zero_bet(self):
        with self.assertRaises(ValueError):
            self.table.make_a_bet(0)

    def test_make_a_negative_bet(self):
        with self.assertRaises(ValueError):
            self.table.make_a_bet(-1)

    def test_game_table_reset(self):
        self.table.game_status = bj.PLAYER_WINS
        self.table.bank = 500
        self.table.reset_game_table()
        with self.subTest(msg='game_status'):
            self.assertEqual(self.table.game_status, bj.UNKNOWN)
        with self.subTest(msg='bank'):
            self.assertEqual(self.table.bank, 0)

    def test_game_table_reward_player(self):
        start_player_money = self.table.player.money
        start_dealer_money = self.table.dealer.money
        self.table.game_status = bj.PLAYER_WINS
        self.table.bank = 200
        self.table.reward_winner()
        with self.subTest('player.money'):
            self.assertEqual(self.table.player.money, start_player_money + 200)
        with self.subTest('dealer.money'):
            self.assertEqual(self.table.dealer.money, start_dealer_money)

    def test_game_table_reward_dealer(self):
        start_player_money = self.table.player.money
        start_dealer_money = self.table.dealer.money
        self.table.game_status = bj.DEALER_WINS
        self.table.bank = 200
        self.table.reward_winner()
        with self.subTest('player.money'):
            self.assertEqual(self.table.player.money, start_player_money)
        with self.subTest('dealer.money'):
            self.assertEqual(self.table.dealer.money, start_dealer_money + 200)

    def test_game_table_reward_draw(self):
        start_player_money = self.table.player.money
        start_dealer_money = self.table.dealer.money
        self.table.game_status = bj.DRAW
        self.table.bank = 200
        self.table.reward_winner()
        with self.subTest('player.money'):
            self.assertEqual(self.table.player.money, start_player_money + 100)
        with self.subTest('dealer.money'):
            self.assertEqual(self.table.dealer.money, start_dealer_money + 100)

    def test_game_table_reward_unknown(self):
        self.table.game_status = bj.UNKNOWN
        self.table.bank = 200
        with self.assertRaises(ValueError):
            self.table.reward_winner()

    def test_game_taking_a_card(self):
        card = self.deck.get_card()
        self.table.player.hand.take_card(card)
        with self.subTest('how many cards has a player'):
            self.assertEqual(len(self.table.player.hand.cards_closed), 1)
        with self.subTest('which card has a player'):
            self.assertEqual(self.table.player.hand.cards_closed[0], card)
        with self.subTest('how many cards left in the deck'):
            self.assertEqual(len(self.deck), 51)

        card = self.deck.get_card()
        self.table.dealer.hand.take_card(card)
        with self.subTest('how many cards has a dealer'):
            self.assertEqual(len(self.table.dealer.hand.cards_closed), 1)
        with self.subTest('which card has a dealer'):
            self.assertEqual(self.table.dealer.hand.cards_closed[0], card)
        with self.subTest('how many cards left in the deck'):
            self.assertEqual(len(self.deck), 50)

    def test_game_open_a_card(self):
        card = self.deck.get_card()
        self.table.player.hand.take_card(card)
        self.table.player.hand.open_card()
        with self.subTest('how many cards has a player'):
            self.assertEqual(len(self.table.player.hand.cards), 1)
        with self.subTest('which card has a player'):
            self.assertEqual(self.table.player.hand.cards[0], card)
        with self.subTest('how many cards left in the deck'):
            self.assertEqual(len(self.deck), 51)

        card = self.deck.get_card()
        self.table.dealer.hand.take_card(card)
        self.table.dealer.hand.open_card()
        with self.subTest('how many cards has a dealer'):
            self.assertEqual(len(self.table.dealer.hand.cards), 1)
        with self.subTest('which card has a dealer'):
            self.assertEqual(self.table.dealer.hand.cards[0], card)
        with self.subTest('how many cards left in the deck'):
            self.assertEqual(len(self.deck), 50)

    def test_game_open_a_card_order(self):
        card1 = self.deck.get_card()
        card2 = self.deck.get_card()
        self.table.player.hand.take_card(card1)
        self.table.player.hand.take_card(card2)
        self.table.player.hand.open_card()
        with self.subTest('how many cards has a player in blind hand'):
            self.assertEqual(len(self.table.player.hand.cards_closed), 1)
        with self.subTest('how many cards has a player in open hand'):
            self.assertEqual(len(self.table.player.hand.cards), 1)
        with self.subTest('which card has a player in open hand'):
            self.assertEqual(self.table.player.hand.cards[0], card1)
        with self.subTest('how many cards left in the deck'):
            self.assertEqual(len(self.deck), 50)

    def test_hand_count_values_20(self):
        cards = [bj.Card(bj.global_card_suits[0], '2'), bj.Card(bj.global_card_suits[0], '3'),
                 bj.Card(bj.global_card_suits[0], '4'), bj.Card(bj.global_card_suits[0], '5'),
                 bj.Card(bj.global_card_suits[0], '6')]
        for card in cards:
            self.table.player.hand.take_card(card)
            self.table.player.hand.open_card()

        self.assertEqual(self.table.player.hand.count_values(), 20)

    def test_hand_count_values_54(self):
        cards = [bj.Card(bj.global_card_suits[0], '2'), bj.Card(bj.global_card_suits[0], '3'),
                 bj.Card(bj.global_card_suits[0], '4'), bj.Card(bj.global_card_suits[0], '5'),
                 bj.Card(bj.global_card_suits[0], '6'), bj.Card(bj.global_card_suits[0], '7'),
                 bj.Card(bj.global_card_suits[0], '8'), bj.Card(bj.global_card_suits[0], '9'),
                 bj.Card(bj.global_card_suits[0], '10')]
        for card in cards:
            self.table.player.hand.take_card(card)
            self.table.player.hand.open_card()

        self.assertEqual(self.table.player.hand.count_values(), 54)

    def test_hand_count_values_2(self):
        cards = [bj.Card(bj.global_card_suits[0], '2')]
        for card in cards:
            self.table.player.hand.take_card(card)
            self.table.player.hand.open_card()

        self.assertEqual(self.table.player.hand.count_values(), 2)

    def test_hand_count_values_0(self):
        cards = []
        for card in cards:
            self.table.player.hand.take_card(card)
            self.table.player.hand.open_card()

        self.assertEqual(self.table.player.hand.count_values(), 0)

    def test_hand_count_values_21(self):
        cards = [bj.Card(bj.global_card_suits[0], '10'), bj.Card(bj.global_card_suits[0], '9'), bj.Card(bj.global_card_suits[0], '2')]
        for card in cards:
            self.table.player.hand.take_card(card)
            self.table.player.hand.open_card()

        self.assertEqual(self.table.player.hand.count_values(), 21)

    def test_hand_count_values_Jack(self):
        self.table.player.hand.take_card(bj.Card(bj.global_card_suits[0], 'Jack'))
        self.table.player.hand.open_card()
        self.assertEqual(self.table.player.hand.count_values(), 10)

    def test_hand_count_values_Queen(self):
        self.table.player.hand.take_card(bj.Card(bj.global_card_suits[0], 'Queen'))
        self.table.player.hand.open_card()
        self.assertEqual(self.table.player.hand.count_values(), 10)

    def test_hand_count_values_King(self):
        self.table.player.hand.take_card(bj.Card(bj.global_card_suits[0], 'King'))
        self.table.player.hand.open_card()
        self.assertEqual(self.table.player.hand.count_values(), 10)

    def test_hand_count_values_Ace(self):
        self.table.player.hand.take_card(bj.Card(bj.global_card_suits[0], 'Ace'))
        self.table.player.hand.open_card()
        self.assertEqual(self.table.player.hand.count_values(), 11)

    def test_hand_count_values_ace_20(self):
        cards = [bj.Card(bj.global_card_suits[0], '9'), bj.Card(bj.global_card_suits[0], 'Ace')]
        for card in cards:
            self.table.player.hand.take_card(card)
            self.table.player.hand.open_card()

        self.assertEqual(self.table.player.hand.count_values(), 20)

    def test_hand_count_values_ace_21(self):
        cards = [bj.Card(bj.global_card_suits[0], '10'), bj.Card(bj.global_card_suits[0], 'Ace')]
        for card in cards:
            self.table.player.hand.take_card(card)
            self.table.player.hand.open_card()

        self.assertEqual(self.table.player.hand.count_values(), 21)

    def test_hand_count_values_ace_22(self):
        cards = [bj.Card(bj.global_card_suits[0], '5'), bj.Card(bj.global_card_suits[0], '6'), bj.Card(bj.global_card_suits[0], 'Ace')]
        for card in cards:
            self.table.player.hand.take_card(card)
            self.table.player.hand.open_card()

        self.assertEqual(self.table.player.hand.count_values(), 12)

    def test_hand_count_values_ace_37(self):
        cards = [bj.Card(bj.global_card_suits[0], '9'), bj.Card(bj.global_card_suits[0], '6'),
                 bj.Card(bj.global_card_suits[0], 'Ace'), bj.Card(bj.global_card_suits[0], '10'), ]
        for card in cards:
            self.table.player.hand.take_card(card)
            self.table.player.hand.open_card()

    def test_hand_count_values_with_closed_card(self):
        cards = [bj.Card(bj.global_card_suits[0], 'Ace'), bj.Card(bj.global_card_suits[0], '5')]
        self.table.player.hand.take_card(cards[0])
        with self.subTest('One card blind.'):
            self.assertEqual(self.table.player.hand.count_values(), 0)

        self.table.player.hand.take_card(cards[1])
        self.table.player.hand.open_card()
        with self.subTest('One card blind and one card opened.'):
            self.assertEqual(self.table.player.hand.count_values(), 11)

        self.table.player.hand.open_card()
        with self.subTest('Two cards opened.'):
            self.assertEqual(self.table.player.hand.count_values(), 16)


if __name__ == '__main__':
    unittest.main()