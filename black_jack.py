import random


# Unicode symbols for card suits.

HEARTS = chr(9829)
DIAMONDS = chr(9824)
SPADES = chr(9830)
CLUBS = chr(9827)


# Game statuses.

UNKNOWN = 0
PLAYER_WINS = 1
DEALER_WINS = 2
DRAW = 3


# Describe every card with it's value in Black Jack game.

global_card_suits = (HEARTS, DIAMONDS, SPADES, CLUBS)
global_card_ranks = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace')
global_card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                      'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = global_card_values[rank]

    def __str__(self):
        return f'{self.rank} {self.suit}'

    def __eq__(self, other):
        if self.suit == other.suit and self.rank == other.rank:
            return True
        else:
            return False

    def get_value(self):
        return self.value

    def toggle_ace_value(self):
        if self.rank == 'Ace' and self.value == 11:
            self.value = 1


class Deck:
    def __init__(self, deck_type=52):
        self.cards = []

        if deck_type == 0:
            return
        elif deck_type == 36:
            for suit in global_card_suits:
                for rank in global_card_ranks[4:]:
                    self.cards.append(Card(suit, rank))
        elif deck_type == 52:
            for suit in global_card_suits:
                for rank in global_card_ranks:
                    self.cards.append(Card(suit, rank))
        else:
            raise ValueError(f'Deck with deck_type={deck_type} cards is not supported.')

        self.shuffle()

    def __len__(self):
        return len(self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def get_card(self):
        return self.cards.pop()

    def __iter__(self):
        self.iter_pos = 0
        return self

    def __next__(self):
        if self.iter_pos >= len(self.cards):
            raise StopIteration
        else:
            self.iter_pos += 1
            return self.cards[self.iter_pos-1]


class Hand:
    def __init__(self):
        self.cards = []
        self.cards_closed = []

    def __len__(self):
        return len(self.cards) + len(self.cards_closed)

    def count_values(self):
        value = 0
        high_aces = 0

        for card in self.cards:
            if card.rank == 'Ace' and card.value == 11:
                high_aces += 1
            value += card.get_value()

        while value > 21 and high_aces > 0:
            for card in self.cards:
                if card.rank == 'Ace' and card.value == 11:
                    card.toggle_ace_value()
                    value -= 10
                    high_aces -= 1
                    break

        return value

    def open_card(self):
        if self.cards_closed:
            card = self.cards_closed.pop(0)
            self.cards.append(card)

    def take_card(self, card):
        self.cards_closed.append(card)

    def __str__(self):
        text = '(' + str(self.count_values()) + '): '
        for card in self.cards:
            text += '[' + str(card) + '] '
        for _ in self.cards_closed:
            text += '[#] '
        return text

    def __iter__(self):
        self._iter_pos = 0
        return self

    def __next__(self):
        if self._iter_pos < len(self.cards):
            self._iter_pos += 1
            return self.cards[self._iter_pos - 1]
        else:
            raise StopIteration


class Player:
    def __init__(self, name, money):
        self.name = name
        self.money = money
        self.hand = Hand()

    def __str__(self):
        return self.name + ' ( $ ' + self.money + ' )'

    def reset_hand(self):
        self.hand = Hand()


class GameTable:
    def __init__(self, dealer_object: '<class Player> object', player_object: '<class Player> object'):
        self.dealer = dealer_object
        self.player = player_object
        self.bank = 0
        self.game_status = UNKNOWN

    def make_a_bet(self, bet_amount: int):
        if self.player.money < bet_amount:
            raise ValueError('Вы не можете поставить больше, чем у Вас есть!')
        elif self.dealer.money < bet_amount:
            raise ValueError('Я в долг не играю!')
        elif bet_amount < 0:
            raise ValueError('Держи вора!')
        elif bet_amount == 0:
            raise ValueError('Бесплатно только кошки родятся!')
        else:
            self.player.money -= bet_amount
            self.dealer.money -= bet_amount
            self.bank += bet_amount * 2

    def reward_winner(self):
        if self.game_status == PLAYER_WINS:
            self.player.money += self.bank
        elif self.game_status == DEALER_WINS:
            self.dealer.money += self.bank
        elif self.game_status == DRAW:
            self.player.money += int(self.bank / 2)
            self.dealer.money += int(self.bank / 2)
        else:
            raise ValueError('Результат игры неопределён! Так кому же достанется банк?')
        self.bank = 0

    def reset_game_table(self):
        self.bank = 0
        self.game_status = UNKNOWN

    @staticmethod
    def clear_screen():
        print('\n' * 100)

    def print_game_table(self, clear_screen=True):
        if clear_screen:
            self.clear_screen()

        print('+' + '-'*78 + '+')

        print('|{:78}|'.format(' '))
        text = ' Игрок ' + self.dealer.name + ' ($' + str(self.dealer.money) + ')'
        print(f'|{text:78}|')
        print('|{:78}|'.format(' '))
        text = ' Карты игрока: ' + str(self.dealer.hand)
        print(f'|{text:78}|')
        print('|{:78}|'.format(' '))

        print('+{:-^78}+'.format(' Банк $' + str(self.bank) + ' '))

        print('|{:78}|'.format(' '))
        text = ' Игрок ' + self.player.name + ' ($' + str(self.player.money) + ')'
        print(f'|{text:78}|')
        print('|{:78}|'.format(' '))
        text = ' Карты игрока: ' + str(self.player.hand)
        print(f'|{text:78}|')
        print('|{:78}|'.format(' '))

        print('+{:-^78}+'.format('-'))


if __name__ == '__main__':

    # Приветствие и начало игры.

    print('\n*** Добро пожаловать в игру "Black Jack"! ***\n')
    print('Я - электронный дилер для игры в "21", также известную как "Black Jack".')
    bank = random.randint(500, 2500)
    print(f'Сегодня в банке ${str(bank)}.\n')

    name = input('С кем имею честь играть? ')
    money = int(input('Сколько у Вас наличных? '))
    if money <= 0:
        print('Приношу свои извинения, но у нас играют только на деньги. '
              'Охрана, покажите, пожалуйста, этому человеку, где у нас дверь.')
        exit(0)

    player = Player(name, money)
    dealer = Player('Дилер', bank)
    table = GameTable(dealer, player)


    # Начинаем играть, пока у игрока или у дилера остаются деньги.

    while player.money > 0 and dealer.money > 0:


        # Очистить игровой стол, сбросить карты с рук и взять новую колоду карт.
        table.reset_game_table()
        player.reset_hand()
        dealer.reset_hand()
        deck = Deck(deck_type=52)


        # Принять ставку

        for i in range(3):
            player_bet = int(input('Ваша ставка, любезнейший: '))
            if player_bet <= 0:
                print('Ваши шансы не настолько малы!')
            elif player_bet > player.money:
                print('Вы о себе слишком высокого мнения!')
            elif player_bet > dealer.money:
                print('Позвольте! Вы хотите оставить меня без штанов?')
            else:
                table.make_a_bet(player_bet)
                break
        else:
            print('Переговоры зашли в тупик... Охрана!..')
            break


        # Раздать по две карты дилеру и игроку. Одна карта дилера остаётся закрытой.

        for i in range(2):
            player.hand.take_card(deck.get_card())
            player.hand.open_card()

        for i in range(2):
            dealer.hand.take_card(deck.get_card())
            if i == 0:
                dealer.hand.open_card()


        # Ход игрока.

        while player.hand.count_values() <= 21:


            # Показать игровой стол.

            table.print_game_table()


            # Доступно несколько действий.

            print('Весь расклад на столе. Что планируете делать?')
            choice = input('[1] - Взять ещё одну карту.\n'
                               '[2] - Удвоить ставку и взять карту.\n'
                               '[ENTER] - Передать ход дилеру.\n'
                               'Ваш выбор: ')

            if choice in ['1', '2']:  # Игрок берёт ещё одну карту.
                player.hand.take_card(deck.get_card())
                player.hand.open_card()

                if choice == '2': # Игрок решил удвоить ставку.
                    try:
                        table.make_a_bet(int(table.bank / 2))
                    except ValueError as message:
                        print(message)

            else:  # Игрок завершает все свои действия и передаёт ход дилеру.
                break


        # Ход дилера

        if player.hand.count_values() > 21:
            print('Похоже, Вы перебрали!')
        else:

            # Дилер открывает карту.

            dealer.hand.open_card()


            # Дилер обязан брать карты, пока сумма его руки меньше 17.

            while dealer.hand.count_values() < 17:

                # Показать игровой стол.

                table.print_game_table()
                #input('Дилер собирается сделать ход. Нажмите [ENTER], чтобы продолжить...')

                # Дилер выбирает действие.

                if dealer.hand.count_values() < 17:
                    print('Дилер решил взять ещё одну карту...')
                    dealer.hand.take_card(deck.get_card())
                    dealer.hand.open_card()
                else:
                    print('Дилер завершает ход.')

                input('Для продолжения нажмите [ENTER]...')
                table.clear_screen()


        # Проверка результата и подведение итогов партии.

        player_score = player.hand.count_values()
        dealer_score = dealer.hand.count_values()

        if player_score > 21 or (21 >= dealer_score > player_score):    # Игрок проиграл партию.
            table.game_status = DEALER_WINS
            table.reward_winner()
            table.print_game_table()
            print('\n' + '*'*80)
            print(f'*\tПростите, {player.name}, но удача на моей стороне.')
            print('*'*80 + '\n')

        elif dealer.hand.count_values() > 21 or (21 >= player_score > dealer_score):   # Дилер проиграл партию.
            table.game_status = PLAYER_WINS
            table.reward_winner()
            table.print_game_table()
            print('\n' + '*'*80)
            print('*\tПоздравляю! Вы победили.')
            print('*'*80 + '\n')
        elif player_score == dealer_score <= 21:   # Ничья.
            table.game_status = DRAW
            table.reward_winner()
            table.print_game_table()
            print('\n' + '*'*80)
            print('*\tВ этот раз ничья! Каждый останется при своих.')
            print('*'*80 + '\n')
        else:   # Непредвиденная ошибка.
            table.game_status = UNKNOWN
            table.reward_winner()
            table.print_game_table()


        # Преложить сыграть ещё раз.

        if player.money > 0 and dealer.money > 0:
            choice = input('Хотите испытать удачу снова?\n[ENTER] - Да\n[No] - Нет\n')
            if choice.lower() in ['no', 'n', 'нет', 'н']:
                break
        else:
            print('Кажется, кто-то остался без штанов!')


    # Прощаемся с игроком.

    if player.money <= 0:
        print(f'Ну вот и всё, уважаемый {player.name}! '
              f'Ваши карманы пусты, а это значит, что мы с Вами встретимся в следующий раз!')
    else:
        print(f'Ну вот и всё, уважаемый {player.name}! Надеюсь, в следующий раз удача будет на моей стороне.')

    print('\n*** До новых встречь в игре "Black Jack"! ***\n')
