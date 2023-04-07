import datetime
import pytest
from zombie.server import queries

import psycopg2.errors


class TestInsertGame:
    def test_happy_path(self):
        game_id = queries.insert_game()[0].game_id

        assert game_id


@pytest.fixture
def inactive_game_id():
    return queries.insert_game()[0].game_id


class TestActivateGame:
    def test_happy_path(self, inactive_game_id):
        queries.activate_game(game_id=inactive_game_id)


@pytest.fixture
def active_game_id():
    game_id = queries.insert_game()[0].game_id
    queries.activate_game(game_id=game_id)
    return game_id


class TestDeactivateGame:
    def test_happy_path(self, active_game_id):
        queries.deactivate_game()


class TestGetActiveGame:
    def test_happy_path(self, active_game_id, inactive_game_id):
        game_id = queries.get_active_game_id()[0].game_id

        assert game_id == active_game_id
    
    def test_no_active_game(self, inactive_game_id):
        game_ids = queries.get_active_game_id()

        assert game_ids == []


@pytest.fixture
def player_name():
    return "some_player_name"


@pytest.fixture
def nfc_id():
    return "some_nfc_id"


class TestInsertPlayer:
    def test_happy_path(self, active_game_id, player_name, nfc_id):
        queries.insert_player(game_id=active_game_id, name=player_name, nfc_id=nfc_id)


@pytest.fixture
def player_id(active_game_id, player_name, nfc_id):
    return queries.insert_player(game_id=active_game_id, name=player_name, nfc_id=nfc_id)[0].player_id


class TestStartRound:
    def test_happy_path(self, active_game_id):
        rows = queries.start_round(game_id=active_game_id)

        assert rows[0].round_id
    
    def test_only_one_round_can_start(self, active_game_id):
        queries.start_round(game_id=active_game_id)

        with pytest.raises(psycopg2.errors.ExclusionViolation):
            queries.start_round(game_id=active_game_id)


@pytest.fixture()
def first_round_id(active_game_id):
    return queries.start_round(game_id=active_game_id)[0].round_id


class TestEndRound:
    def test_happy_path(self, active_game_id, first_round_id):
        rows = queries.end_round(game_id=active_game_id)

        assert rows[0].round_id


@pytest.fixture()
def first_round_ended(active_game_id, first_round_id):
    return queries.end_round(game_id=active_game_id)


@pytest.fixture()
def second_round_id(active_game_id, first_round_ended):
    return queries.start_round(game_id=active_game_id)[0].round_id


class TestGetGameInfo:
    def test_new_game_info(self, active_game_id):
        rows = queries.get_game_info(game_ids=[active_game_id])

        assert len(rows) == 1
        game = rows[0]
        assert game.game_id == active_game_id
        assert game.is_active is True
        assert game.player_count == 0
        assert game.round_number == 0
        assert game.round_ended is True
    
    def test_game_with_one_player(self, active_game_id, player_id):
        rows = queries.get_game_info(game_ids=[active_game_id])

        assert len(rows) == 1
        game = rows[0]
        assert game.player_count == 1
    
    def test_inactive(self, inactive_game_id):
        rows = queries.get_game_info(game_ids=[inactive_game_id])

        assert len(rows) == 1
        game = rows[0]
        assert game.is_active is False
    
    def test_game_in_first_round(self, active_game_id, first_round_id):
        rows = queries.get_game_info(game_ids=[active_game_id])

        assert len(rows) == 1
        game = rows[0]
        assert game.round_number == 1
        assert game.round_ended is False
    
    def test_game_after_first_round_ended(self, active_game_id, first_round_ended):
        rows = queries.get_game_info(game_ids=[active_game_id])

        assert len(rows) == 1
        game = rows[0]
        assert game.round_number == 1
        assert game.round_ended is True
    
    def test_game_in_second_round(self, active_game_id, second_round_id):
        rows = queries.get_game_info(game_ids=[active_game_id])

        assert len(rows) == 1
        game = rows[0]
        assert game.round_number == 2
        assert game.round_ended is False


class TestListGames:
    def test_happy_path(self, active_game_id, inactive_game_id):
        rows = queries.list_games(before=datetime.datetime.now(), count=2)

        assert {row.game_id for row in rows} == {active_game_id, inactive_game_id}
