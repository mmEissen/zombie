import enum

from zombie.server import queries


class GameState(enum.Enum):
    NO_GAME = enum.auto()
    REGISTRATION = enum.auto()
    ROUND_1 = enum.auto()


def get_game_state() -> GameState:
    pass
