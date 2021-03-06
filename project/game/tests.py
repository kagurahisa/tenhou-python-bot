# -*- coding: utf-8 -*-
import logging
import unittest

import game.game_manager
from game.client import LocalClient
from game.game_manager import GameManager
from utils.tests import TestMixin
from utils.settings_handler import settings


class GameManagerTestCase(unittest.TestCase, TestMixin):

    def tearDown(self):
        settings.FIVE_REDS = True
        settings.OPEN_TANYAO = True

    # def test_debug(self):
    #     settings.FIVE_REDS = True
    #
    #     game.game_manager.shuffle_seed = lambda: 0.36533953824308185
    #
    #     clients = [LocalClient(previous_ai=False) for _ in range(0, 4)]
    #     # clients = [LocalClient(use_previous_ai_version=True) for _ in range(0, 3)]
    #     # clients += [LocalClient(use_previous_ai_version=False)]
    #     manager = GameManager(clients)
    #     manager.replay.init_game('123')
    #     manager.init_game()
    #     manager.set_dealer(1)
    #     manager._unique_dealers = 6
    #     manager.round_number = 6
    #     manager.init_round()
    #
    #     result = manager.play_round()
    #
    #     manager.replay.end_game()

    def test_init_game(self):
        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()

        self.assertTrue(manager.dealer in [0, 1, 2, 3])

    def test_init_round(self):
        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()

        self.assertEqual(len(manager.dead_wall), 14)
        self.assertEqual(len(manager.dora_indicators), 1)
        self.assertIsNotNone(manager.current_client_seat)
        self.assertEqual(manager.round_number, 0)
        self.assertEqual(manager.honba_sticks, 0)
        self.assertEqual(manager.riichi_sticks, 0)
        self.assertEqual([i.player.scores for i in manager.clients], [25000, 25000, 25000, 25000])

        for client in clients:
            self.assertEqual(len(client.player.tiles), 13)

        self.assertEqual(len(manager.tiles), 70)

    def test_init_dealer(self):
        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.set_dealer(0)
        manager.init_round()

        self.assertTrue(manager.clients[0].player.is_dealer)
        self.assertFalse(manager.clients[1].player.is_dealer)
        self.assertFalse(manager.clients[2].player.is_dealer)
        self.assertFalse(manager.clients[3].player.is_dealer)

        manager.set_dealer(1)
        manager.init_round()

        self.assertTrue(manager.clients[1].player.is_dealer)
        self.assertFalse(manager.clients[0].player.is_dealer)
        self.assertFalse(manager.clients[2].player.is_dealer)
        self.assertFalse(manager.clients[3].player.is_dealer)

        manager.set_dealer(2)
        manager.init_round()

        self.assertTrue(manager.clients[2].player.is_dealer)
        self.assertFalse(manager.clients[0].player.is_dealer)
        self.assertFalse(manager.clients[1].player.is_dealer)
        self.assertFalse(manager.clients[3].player.is_dealer)

        manager.set_dealer(3)
        manager.init_round()

        self.assertTrue(manager.clients[3].player.is_dealer)
        self.assertFalse(manager.clients[0].player.is_dealer)
        self.assertFalse(manager.clients[1].player.is_dealer)
        self.assertFalse(manager.clients[2].player.is_dealer)

    def test_init_scores_and_recalculate_position(self):
        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.set_dealer(3)

        clients[0].player.scores = 24000
        clients[1].player.scores = 23000
        clients[2].player.scores = 22000
        clients[3].player.scores = 21000

        manager.recalculate_players_position()

        self.assertEqual(clients[0].player.scores, 24000)
        self.assertEqual(clients[0].player.position, 1)
        self.assertEqual(clients[1].player.scores, 23000)
        self.assertEqual(clients[1].player.position, 2)
        self.assertEqual(clients[2].player.scores, 22000)
        self.assertEqual(clients[2].player.position, 3)
        self.assertEqual(clients[3].player.scores, 21000)
        self.assertEqual(clients[3].player.position, 4)

        clients[0].player.scores = 24000
        clients[1].player.scores = 24000
        clients[2].player.scores = 22000
        clients[3].player.scores = 22000

        manager.recalculate_players_position()

        self.assertEqual(clients[0].player.scores, 24000)
        self.assertEqual(clients[0].player.position, 1)
        self.assertEqual(clients[1].player.scores, 24000)
        self.assertEqual(clients[1].player.position, 2)
        self.assertEqual(clients[2].player.scores, 22000)
        self.assertEqual(clients[2].player.position, 3)
        self.assertEqual(clients[3].player.scores, 22000)
        self.assertEqual(clients[3].player.position, 4)

    def test_call_riichi(self):
        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()

        client = clients[0]
        self.assertEqual(manager.riichi_sticks, 0)
        self.assertEqual(client.player.scores, 25000)
        self.assertEqual(client.player.in_riichi, False)

        manager.call_riichi(client)

        self.assertEqual(manager.riichi_sticks, 1)
        self.assertEqual(client.player.scores, 24000)
        self.assertEqual(client.player.in_riichi, True)

        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()

        manager.call_riichi(clients[0])

        self.assertEqual(clients[0].player.in_riichi, True)
        self.assertEqual(clients[1].player.in_riichi, False)
        self.assertEqual(clients[2].player.in_riichi, False)
        self.assertEqual(clients[3].player.in_riichi, False)

        for client in clients:
            client.player.in_riichi = False

        manager.call_riichi(clients[1])

        self.assertEqual(clients[0].player.in_riichi, False)
        self.assertEqual(clients[1].player.in_riichi, True)
        self.assertEqual(clients[2].player.in_riichi, False)
        self.assertEqual(clients[3].player.in_riichi, False)

        for client in clients:
            client.player.in_riichi = False

        manager.call_riichi(clients[2])

        self.assertEqual(clients[0].player.in_riichi, False)
        self.assertEqual(clients[1].player.in_riichi, False)
        self.assertEqual(clients[2].player.in_riichi, True)
        self.assertEqual(clients[3].player.in_riichi, False)

        for client in clients:
            client.player.in_riichi = False

        manager.call_riichi(clients[3])

        self.assertEqual(clients[0].player.in_riichi, False)
        self.assertEqual(clients[1].player.in_riichi, False)
        self.assertEqual(clients[2].player.in_riichi, False)
        self.assertEqual(clients[3].player.in_riichi, True)

    def test_play_round(self):
        game.game_manager.shuffle_seed = lambda: 0.8689851662263914

        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()
        manager.set_dealer(3)
        manager._unique_dealers = 4
        manager.round_number = 5

        manager.play_round()

        self.assertNotEqual(manager.round_number, 0)

    def test_scores_calculations_after_retake(self):
        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()

        manager.process_the_end_of_the_round([], None, None, None, False)

        self.assertEqual(clients[0].player.scores, 25000)
        self.assertEqual(clients[1].player.scores, 25000)
        self.assertEqual(clients[2].player.scores, 25000)
        self.assertEqual(clients[3].player.scores, 25000)

        clients[0].player.in_tempai = True
        manager.process_the_end_of_the_round([], None, None, None, False)

        self.assertEqual(clients[0].player.scores, 28000)
        self.assertEqual(clients[1].player.scores, 24000)
        self.assertEqual(clients[2].player.scores, 24000)
        self.assertEqual(clients[3].player.scores, 24000)

        for client in clients:
            client.player.scores = 25000

        clients[0].player.in_tempai = True
        clients[1].player.in_tempai = True
        manager.process_the_end_of_the_round([], None, None, None, False)

        self.assertEqual(clients[0].player.scores, 26500)
        self.assertEqual(clients[1].player.scores, 26500)
        self.assertEqual(clients[2].player.scores, 23500)
        self.assertEqual(clients[3].player.scores, 23500)

        for client in clients:
            client.player.scores = 25000

        clients[0].player.in_tempai = True
        clients[1].player.in_tempai = True
        clients[2].player.in_tempai = True
        manager.process_the_end_of_the_round([], None, None, None, False)

        self.assertEqual(clients[0].player.scores, 26000)
        self.assertEqual(clients[1].player.scores, 26000)
        self.assertEqual(clients[2].player.scores, 26000)
        self.assertEqual(clients[3].player.scores, 22000)

        for client in clients:
            client.player.scores = 25000

        clients[0].player.in_tempai = True
        clients[1].player.in_tempai = True
        clients[2].player.in_tempai = True
        clients[3].player.in_tempai = True
        manager.process_the_end_of_the_round([], None, None, None, False)

        self.assertEqual(clients[0].player.scores, 25000)
        self.assertEqual(clients[1].player.scores, 25000)
        self.assertEqual(clients[2].player.scores, 25000)
        self.assertEqual(clients[3].player.scores, 25000)

    def test_retake_and_honba_increment(self):
        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()

        # no one in tempai, so honba stick should be added
        manager.process_the_end_of_the_round([], None, None, None, False)
        self.assertEqual(manager.honba_sticks, 1)

        manager.honba_sticks = 0
        manager.set_dealer(0)
        clients[0].player.in_tempai = False
        clients[1].player.in_tempai = True

        self.assertEqual(manager._unique_dealers, 3)
        # dealer NOT in tempai
        # dealer should be moved and honba should be added
        manager.process_the_end_of_the_round([], None, None, None, False)
        self.assertEqual(manager.honba_sticks, 1)
        self.assertEqual(manager._unique_dealers, 4)

        clients[0].player.in_tempai = True
        manager.set_dealer(0)

        # dealer in tempai, so honba stick should be added
        manager.process_the_end_of_the_round([], None, None, None, False)
        self.assertEqual(manager.honba_sticks, 2)

    def test_win_by_ron_and_scores_calculation(self):
        settings.FIVE_REDS = False

        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()
        manager.set_dealer(0)
        manager.dora_indicators = [0]

        winner = clients[0]
        winner.player.discards = [1, 2]
        loser = clients[1]

        # 1500 hand
        tiles = self._string_to_136_array(sou='123567', pin='12345', man='11')
        win_tile = self._string_to_136_tile(pin='6')
        manager.process_the_end_of_the_round(tiles, win_tile, winner, loser, False)
        self.assertEqual(winner.player.scores, 26500)
        self.assertEqual(loser.player.scores, 23500)

        winner.player.scores = 25000
        winner.player.dealer_seat = 1
        loser.player.scores = 25000
        manager.riichi_sticks = 2
        manager.honba_sticks = 2

        tiles = self._string_to_136_array(sou='123567', pin='12345', man='11')
        win_tile = self._string_to_136_tile(pin='6')
        manager.process_the_end_of_the_round(tiles, win_tile, winner, loser, False)
        self.assertEqual(winner.player.scores, 28600)
        self.assertEqual(loser.player.scores, 23400)
        self.assertEqual(manager.riichi_sticks, 0)
        self.assertEqual(manager.honba_sticks, 0)

        winner.player.scores = 25000
        winner.player.dealer_seat = 0
        loser.player.scores = 25000
        manager.honba_sticks = 2

        # if dealer won we need to increment honba sticks
        tiles = self._string_to_136_array(sou='123567', pin='12345', man='11')
        win_tile = self._string_to_136_tile(pin='6')
        manager.process_the_end_of_the_round(tiles, win_tile, winner, loser, False)
        self.assertEqual(winner.player.scores, 27100)
        self.assertEqual(loser.player.scores, 22900)
        self.assertEqual(manager.honba_sticks, 3)

        settings.FIVE_REDS = True

    def test_win_by_tsumo_and_scores_calculation(self):
        settings.FIVE_REDS = True

        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.init_game()
        manager.init_round()
        manager.riichi_sticks = 1
        manager.honba_sticks = 1

        winner = clients[0]
        manager.set_dealer(0)
        manager.dora_indicators = [100]
        # to avoid ura-dora, because of this test can fail
        winner.player.in_riichi = False
        winner.player.discards = [1, 2]

        tiles = self._string_to_136_array(sou='123567', pin='12345', man='11')
        win_tile = self._string_to_136_tile(pin='6')
        manager.process_the_end_of_the_round(tiles, win_tile, winner, None, True)

        # 8100 + riichi stick (1000) = 9100
        # 2600 from each other player + 100 honba payment
        self.assertEqual(winner.player.scores, 34100)
        self.assertEqual(clients[1].player.scores, 22300)
        self.assertEqual(clients[2].player.scores, 22300)
        self.assertEqual(clients[3].player.scores, 22300)

        for client in clients:
            client.player.scores = 25000

        winner = clients[0]
        manager.set_dealer(1)
        winner.player.in_riichi = False
        manager.riichi_sticks = 0
        manager.honba_sticks = 0

        tiles = self._string_to_136_array(sou='123567', pin='12345', man='11')
        win_tile = self._string_to_136_tile(pin='6')
        manager.process_the_end_of_the_round(tiles, win_tile, winner, None, True)

        # 2600 from dealer and 1300 from other players
        self.assertEqual(winner.player.scores, 30200)
        self.assertEqual(clients[1].player.scores, 23700)
        self.assertEqual(clients[2].player.scores, 22400)
        self.assertEqual(clients[3].player.scores, 23700)

        settings.FIVE_REDS = False

    def test_ron_and_furiten(self):
        clients = [LocalClient() for _ in range(0, 4)]
        client = clients[0]
        manager = GameManager(clients)

        client.player.init_hand(self._string_to_136_array(pin='12345677', sou='23456'))

        # to make furiten
        tile = self._string_to_136_tile(sou='1')
        client.player.draw_tile(tile)
        client.player.discard_tile(tile)

        # to set in_tempai flag
        client.player.draw_tile(self._string_to_136_tile(honors='1'))
        client.player.discard_tile()

        win_tile = self._string_to_136_tile(sou='1')
        result = manager.can_call_ron(client, win_tile)
        self.assertEqual(result, False)

    def test_change_dealer_after_end_of_the_round(self):
        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.set_dealer(0)
        manager.init_round()

        # retake. dealer is NOT in tempai, let's move a dealer position
        manager.process_the_end_of_the_round(list(range(0, 13)), None, None, None, False)
        self.assertEqual(manager.dealer, 1)

        # retake. dealer is in tempai, don't move a dealer position
        clients[1].player.in_tempai = True
        manager.process_the_end_of_the_round(list(range(0, 13)), 0, None, None, False)
        self.assertEqual(manager.dealer, 1)

        # dealer win by ron, don't move a dealer position
        manager.process_the_end_of_the_round(list(range(0, 13)), 0, None, None, False)
        self.assertEqual(manager.dealer, 1)

        # dealer win by tsumo, don't move a dealer position
        manager.process_the_end_of_the_round(list(range(0, 13)), 0, None, None, False)
        self.assertEqual(manager.dealer, 1)

        # NOT dealer win by ron, let's move a dealer position
        manager.process_the_end_of_the_round(list(range(0, 13)), 0, clients[3], clients[2], False)
        self.assertEqual(manager.dealer, 2)

        # NOT dealer win by tsumo, let's move a dealer position
        manager.process_the_end_of_the_round(list(range(0, 13)), 0, clients[1], None, True)
        self.assertEqual(manager.dealer, 3)

    def test_is_game_end_by_negative_scores(self):
        settings.FIVE_REDS = False

        clients = [LocalClient() for _ in range(0, 4)]
        manager = GameManager(clients)
        manager.set_dealer(0)
        manager.init_round()

        winner = clients[0]
        loser = clients[1]
        manager.dora_indicators = [100]
        loser.player.scores = 0

        tiles = self._string_to_136_array(sou='123567', pin='12345', man='11')
        win_tile = self._string_to_136_tile(pin='6')
        # discards to erase renhou
        winner.player.discards = [1, 2]

        result = manager.process_the_end_of_the_round(tiles, win_tile, winner, loser, False)
        self.assertEqual(loser.player.scores, -1500)
        self.assertEqual(result['is_game_end'], True)

        settings.FIVE_REDS = True

    def test_is_game_end_by_eight_winds(self):
        clients = [LocalClient() for _ in range(0, 4)]

        current_dealer = 0
        manager = GameManager(clients)
        manager.init_game()
        manager.set_dealer(current_dealer)
        manager.init_round()
        manager._unique_dealers = 1

        for x in range(0, 7):
            # to avoid honba
            result = manager.process_the_end_of_the_round([], 0, None, None, True)
            self.assertEqual(result['is_game_end'], False)
            self.assertNotEqual(manager.dealer, current_dealer)
            current_dealer = manager.dealer

        result = manager.process_the_end_of_the_round(list(range(0, 13)), 0, clients[0], None, True)
        self.assertEqual(result['is_game_end'], True)
