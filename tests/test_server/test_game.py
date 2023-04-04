import pytest
from zombie.server import logic


class TestNewGame:
    def test_with_no_games(self):
        game_ = logic.new_game()

        assert game_.players == 0
        assert game_.status == "Lobby"


@pytest.fixture
def new_game():
    return logic.new_game()


class TestListGames:
    def test_with_no_games(self):
        games = logic.list_games()

        assert games == []

    def test_with_new_game(self, new_game):
        games = logic.list_games()

        assert games == [new_game]
