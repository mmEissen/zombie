import enum

from zombie.server import queries


class GameState(enum.Enum):
    LOBY = enum.auto()
    ROUND_1 = enum.auto()
    ROUND_1_SCORE = enum.auto()
    ENDED = enum.auto()


def get_active_game_id() -> int | None:
    game_id = queries.get_active_game_id()
    if not game_id:
        return None
    return game_id[0].game_id

