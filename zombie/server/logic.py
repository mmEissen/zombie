from __future__ import annotations

import datetime
import pydantic
from zombie.server import queries
import psycopg2.errors


def get_active_game_id() -> int | None:
    game_id = queries.get_active_game_id()
    if not game_id:
        return None
    return game_id[0].game_id


def activate_game(game_id: int) -> None:
    queries.deactivate_game()
    queries.activate_game(game_id=game_id)


class Game(pydantic.BaseModel):
    id_: int
    when_created: datetime.datetime
    is_active: bool
    players: int
    status: str

    @classmethod
    def from_game_row(cls, row: queries.get_game_info.Row) -> Game:
        if row.round_number == 0:
            status = "Lobby"
        elif not row.round_ended:
            status = f"Round {row.round_number}"
        elif row.round_number < 3:
            status = f"Round {row.round_number} results"
        else:
            status = "Scores"
        return cls(
            id_=row.game_id,
            when_created=row.when_created,
            is_active=row.is_active,
            players=row.player_count,
            status=status,
        )


def list_games(before: datetime.datetime | None = None, count: int = 30) -> list[Game]:
    before = before or datetime.datetime.utcnow()
    game_ids = [row.game_id for row in queries.list_games(before=before, count=count)]
    return [Game.from_game_row(row) for row in queries.get_game_info(game_ids=game_ids)]


def get_game(game_id: int) -> Game | None:
    games = queries.get_game_info(game_ids=[game_id])
    if not games:
        return None
    return Game.from_game_row(games[0])


def new_game() -> Game:
    game_id = queries.insert_game()[0].game_id
    return Game.from_game_row(queries.get_game_info(game_ids=[game_id])[0])


class GameDetails(pydantic.BaseModel):
    class Player(pydantic.BaseModel):
        uid: str
        name: str

    id_: int
    when_created: datetime.datetime
    is_active: bool
    players: list[Player]
    status: str


def get_game_details(game_id: int) -> GameDetails | None:
    game = get_game(game_id)
    if game is None:
        return None
    return GameDetails(
        players=[],
        **game.dict(include=["id_", "when_created", "is_active", "status"])
    )


class Player(pydantic.BaseModel):
    game_id: int | None = None
    name: str | None = None


def get_player_in_active_game(uid: str) -> Player:
    players = queries.get_player_in_active_game(nfc_id=uid)
    if not players:
        return Player()
    player = players[0]
    return Player(
        game_id=player.game_id,
        name=player.name,
    )


class PlayerNameExistsError(Exception):
    pass


def create_player_in_active_game(name: str, nfc_id: str) -> None:
    try:
        queries.insert_player(name=name, nfc_id=nfc_id)
    except psycopg2.errors.UniqueViolation as e:
        raise PlayerNameExistsError() from e
