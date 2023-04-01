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
    queries.activate_game(game_id=queries.insert_game()[0].game_id)


class TestDeactivateGame:
    def test_happy_path(self, active_game_id):
        queries.deactivate_game(game_id=active_game_id)


class TestInsertPlayer:
    @pytest.fixture
    def name(self):
        return "some_player_name"
    
    @pytest.fixture
    def nfc_id(self):
        return "some_nfc_id"

    def test_happy_path(self, active_game_id, name, nfc_id):
        queries.insert_player(name=name, nfc_id=nfc_id)

    def test_with_no_active_game(self, inactive_game_id, name, nfc_id):
        with pytest.raises(psycopg2.errors.NotNullViolation):
            queries.insert_player(name=name, nfc_id=nfc_id)[0]
