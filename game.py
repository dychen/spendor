import random


class IllegalMove(Exception):
    pass


class GameState():
    __TIERS = [1, 2, 3]
    __TIER_SIZE = 4
    __GEMS = ['w', 'u', 'g', 'r', 'b']
    __P_GEM_LIMIT = 10
    __T2_GEM_LIMIT = 4
    __GOLD_LIMIT = 5
    __P_RESERVE_LIMIT = 3

    def __load_cards(self):
        d = { t: [] for t in self.__TIERS }
        with open('gamedata.tsv') as f:
            for line in f:
                t, w_c, u_c, g_c, r_c, b_c, v, p = line.split('\t')
                d[int(t)].append([int(w_c), int(u_c), int(g_c), int(r_c), int(b_c), v, int(p)])
        return d

    def __shuffle(self):
        for t, cards in self.cards.items():
            random.shuffle(cards)

    def __draw(self, t):
        if self.cards[t]:
            return self.cards[t].pop(0)

    def __draw_initial(self):
        board = { t: [] for t in self.__TIERS }
        for t in self.__TIERS:
            for _ in range(self.__TIER_SIZE):
                board[t].append(self.__draw(t))
        return board

    def __initialize_gems(self, num_players):
        n = 7
        if num_players == 2:
            n = 4
        elif num_players == 3:
            n = 5
        return [n for _ in range(len(self.__GEMS))]

    def __initialize_players(self, num_players):
        return { i: { 'gems': [0, 0, 0, 0, 0], 'cards': [], 'reserved': [], 'gold': 0 }
                 for i in range(num_players) }

    def __init__(self, num_players=2):
        """
        self.cards: { [tier]: [[w_cost, u_cost, g_cost, r_cost, b_cost, value_color, points]] }
        self.board: { [tier]: [[w_cost, u_cost, g_cost, r_cost, b_cost, value_color, points]] }
        self.gems: [w_count, u_count, g_count, r_count, b_count]
        self.gold: 5
        self.players: { [player]: {
            gems: [w_count, u_count, g_count, r_count, b_count],
            cards: [[w_cost, u_cost, g_cost, r_cost, b_cost, value_color, points]],
            reserved: [[w_cost, u_cost, g_cost, r_cost, b_cost, value_color, points]],
            gold: 0
        }}
        """
        self.cards = self.__load_cards()
        self.__shuffle()
        self.board = self.__draw_initial()
        self.gems = self.__initialize_gems(num_players)
        self.gold = self.__GOLD_LIMIT
        self.players = self.__initialize_players(num_players)
        self.meta = {
            'num_players': num_players,
            'turn': 1
        }

    def get_points(self, player):
        return sum([x[-1] for x in self.players[player]['cards']])

    def get_total_gems(self, player):
        return [x + y for x, y in zip(self.players[player]['gems'], self.get_card_gems(player))]

    def get_card_gems(self, player):
        indices = [self.__GEMS.index(x[5]) for x in self.players[player]['cards']]
        return [indices.count(i) for i in range(len(self.__GEMS))]

    def __check_player_gem_count(self, player, data):
        if not (sum(self.players[player]['gems']) + sum(data) <= self.__P_GEM_LIMIT):
            raise IllegalMove('Player would exceed 10 gems')

    def __check_board_gem_count(self, player, data):
        if not (len([True for x, y in zip(self.gems, data) if x - y < 0]) == 0):
            raise IllegalMove('Gem stack would go below zero')

    def __check_take_3_valid(self, player, data):
        if not (len(data) == 5 and set(data) == set([0, 1]) and sum(data) <= 3):
            raise IllegalMove('Invalid take 3 input')

    def __check_take_2_valid(self, player, data):
        if not (len(data) == 5 and set(data) == set([0, 2]) and data.count(2) == 1):
            raise IllegalMove('Invalid take 2 input')

    def __check_take_2_stack_size(self, player, data):
        if not (self.gems[data.index(2)] >= self.__T2_GEM_LIMIT):
            raise IllegalMove('Stack too low to take 2 gems')

    def __check_reserve_valid(self, data):
        if len(data) != 2 or not data[0] in self.board:
            raise IllegalMove('Invalid reserve input')

    def __check_board_gold_count(self):
        if not (self.gold > 0):
            raise IllegalMove('Gold stack would go below zero')

    def __check_player_reserve_count(self, player):
        if not (len(self.players[player]['reserved']) < self.__P_RESERVE_LIMIT):
            raise IllegalMove('Player has already reserved the max amount of cards')

    def __check_buy_valid(self, data):
        if (len(data) != 3
            or not data[0] in self.board and not data[2]): # Not buying from reserve
            raise IllegalMove('Invalid buy input')

    def __check_card_exists(self, card_list, index):
        try:
            card_list[index]
        except Indexerror:
            raise IllegalMove('Target card doesn\'t exist')

    def __check_player_can_buy(self, player, target_costs):
        """Player can buy if sum(max_each(costs - pgems, 0)) <= player_gold"""
        if not (sum([max(x - y, 0) for x, y in zip(target_costs, self.get_total_gems(player))])
                <= self.players[player]['gold']):
            raise IllegalMove('Not enough gems to buy card')

    def move_take_3(self, player, data):
        self.__check_take_3_valid(player, data)
        self.__check_board_gem_count(player, data)
        self.__check_player_gem_count(player, data)
        for i in range(len(data)):
            self.gems[i] -= data[i]
            self.players[player]['gems'][i] += data[i]

    def move_take_2(self, player, data):
        self.__check_take_2_valid(player, data)
        self.__check_board_gem_count(player, data)
        self.__check_player_gem_count(player, data)
        self.__check_take_2_stack_size(player, data)
        for i in range(len(data)):
            self.gems[i] -= data[i]
            self.players[player]['gems'][i] += data[i]

    def move_reserve(self, player, data):
        self.__check_reserve_valid(data)
        self.__check_board_gold_count()
        self.__check_player_reserve_count(player)
        tier, index = data
        card_list = self.board[tier]
        self.__check_card_exists(card_list, index)
        # Take and draw
        card = card_list.pop(index)
        self.players[player]['reserved'].append(card)
        card_list.append(self.__draw(tier))
        # Take gold
        self.players[player]['gold'] += 1

    def move_buy(self, player, data):
        def check(card_list, index):
            self.__check_card_exists(card_list, index)
            target = card_list[index]
            self.__check_player_can_buy(player, target[:5])
            return target
        def pay(card):
            cost_arr = [max(x - y, 0) for x, y in zip(card[:5], self.get_card_gems(player))]
            new_pgems = [x - y for x, y in zip(self.players[player]['gems'], cost_arr)]
            gold_cost = abs(sum([x for x in new_pgems if x < 0]))
            new_pgems = [max(x, 0) for x in new_pgems]
            self.players[player]['gems'] = new_pgems
            self.players[player]['gold'] -= gold_cost
        def take(card_list, index):
            card = card_list.pop(index)
            self.players[player]['cards'].append(card)

        self.__check_buy_valid(data)
        tier, index, from_reserve = data
        if from_reserve:
            card_list = self.players[player]['reserved']
            card = check(card_list, index)
            pay(card)
            take(card_list, index)
        else:
            card_list = self.board[tier]
            card = check(card_list, index)
            pay(card)
            take(card_list, index)
            card_list.append(self.__draw(tier)) # Replace card

    def move(self, player, action, data):
        if action == 't3':
            self.move_take_3(player, data)
            print('>> Player {} took 3 gems: {}'.format(player, data))
        elif action == 't2':
            self.move_take_2(player, data)
            print('>> Player {} took 2 gems: {}'.format(player, data))
        elif action == 'r':
            self.move_reserve(player, data)
            print('>> Player {} reserved a card: {}'.format(player, data))
        elif action == 'b':
            self.move_buy(player, data)
            print('>> Player {} bought a card: {}'.format(player, data))
        else:
            raise IllegalMove('Invalid action - must be one of [t3/t2/r/b]')

    def print_state(self):
        print('=====NEW STATE=====')
        for tier, bstate in self.board.items():
            print('=TIER {}='.format(tier))
            for card in bstate:
                print(card)
        print('=GEMS=')
        print(self.gems)
        for i, pstate in self.players.items():
            print('=PLAYER {}='.format(i))
            print('  POINTS: {}'.format(self.get_points(i)))
            print('  NORM GEMS: {} GOLD: {}'.format(pstate['gems'], pstate['gold']))
            print('  CARD GEMS: {}'.format(self.get_card_gems(i)))
            print('  TOTL GEMS: {} GOLD: {}'.format(self.get_total_gems(i), pstate['gold']))
            for card in pstate['cards']:
                print('    CARD: {}'.format(card))
            for card in pstate['reserved']:
                print('    RESERVED: {}'.format(card))
        print('========END========')

    def run(self):
        def make_move(i):
            try:
                print('==PLAYER ' + str(i) + '==')
                move_str = raw_input('Move? [t3/t2/r/b] [data]: ').split(' ')
                action, data = move_str[0], [int(x) for x in move_str[1:]]
                self.move(i, action, data)
                self.print_state()
            except IllegalMove as e:
                print('==ILLEGAL MOVE: {}=='.format(e))
                make_move(i)

        self.print_state()
        while True:
            print('\n\n==TURN ' + str(self.meta['turn']) + '==')
            for i in range(self.meta['num_players']):
                make_move(i)
            self.meta['turn'] += 1

GameState().run()
