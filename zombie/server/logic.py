from __future__ import annotations
import collections
import dataclasses

import datetime
import itertools
import pydantic
from zombie.server import queries
import psycopg2.errors


class GameException(Exception):
    pass


class UserFacingError(GameException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


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
    is_started: bool
    players: int
    status: str
    link: str = ""

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
            is_started=row.is_started,
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


class GameDetailsPlayer(pydantic.BaseModel):
    player_id: int
    uid: str
    name: str
    is_initial_zombie: bool


class GameDetailsRound(pydantic.BaseModel):
    round_id: int
    round_number: int
    when_started: datetime.datetime
    when_ended: datetime.datetime | None


class GameDetails(pydantic.BaseModel):
    id_: int
    when_created: datetime.datetime
    is_active: bool
    is_started: bool
    players: list[GameDetailsPlayer]
    rounds: list[GameDetailsRound]
    status: str


def get_game_details(game_id: int) -> GameDetails | None:
    game = get_game(game_id)
    if game is None:
        return None
    players = queries.list_players_in_game(game_id=game_id)
    rounds = queries.list_rounds_in_game(game_id=game_id)
    return GameDetails(
        players=[
            GameDetailsPlayer(
                player_id=player.player_id,
                uid=player.nfc_id,
                name=player.name,
                is_initial_zombie=player.is_initial_zombie,
            )
            for player in players
        ],
        rounds=[
            GameDetailsRound(
                round_id=round_.round_id,
                round_number=round_.round_number,
                when_started=round_.when_started,
                when_ended=round_.when_ended,
            )
            for round_ in rounds
        ],
        **game.dict(
            include={"id_", "when_created", "is_active", "status", "is_started"}
        ),
    )


class Player(pydantic.BaseModel):
    player_id: int | None = None
    game_id: int | None = None
    game_is_started: bool = True
    name: str | None = None
    round_number: int | None = None
    round_ended: bool = True


def get_player_in_active_game(uid: str) -> Player:
    players = queries.get_player_in_active_game(nfc_id=uid)
    if not players:
        return Player()
    player = players[0]

    player_in_game = Player(
        player_id=player.player_id,
        game_id=player.game_id,
        game_is_started=player.is_started,
        name=player.name,
    )

    if player.game_id is None:
        return player_in_game

    games = queries.get_game_info(game_ids=[player.game_id])
    if not games:
        return player_in_game

    game = games[0]

    player_in_game.round_number = game.round_number
    player_in_game.round_ended = game.round_ended

    return player_in_game


def create_player_in_active_game(name: str, nfc_id: str) -> None:
    if len(name) < 3:
        raise UserFacingError("Name too short!")
    if len(nfc_id) < 1:
        raise UserFacingError("NFC ID too short!")
    try:
        queries.insert_player(name=name, nfc_id=nfc_id)
    except psycopg2.errors.UniqueViolation:
        raise UserFacingError("Name already taken!")
    except psycopg2.errors.NotNullViolation:
        raise UserFacingError("There is no game to add the player to.")


class BadTouchError(Exception):
    """Sweat baby, sweat baby"""


def make_touch(left_nfc: str, right_nfc: str) -> None:
    try:
        queries.insert_touch(left_player_nfc=left_nfc, right_player_nfc=right_nfc)
    except psycopg2.errors.IntegrityError:
        raise BadTouchError()


def start_game(game_id: int) -> None:
    queries.start_game(game_id=game_id)


def make_zombies(game_id: int, number_zombies: int) -> None:
    queries.make_random_zombie(game_id=game_id, number_zombies=number_zombies)


def toggle_zombie(player_id: int) -> None:
    try:
        queries.toggle_zombie(player_id=player_id)
    except psycopg2.errors.RaiseException as e:
        raise UserFacingError("Can't toggle zombie after game is started")


def start_round(game_id: int) -> None:
    try:
        queries.start_round(game_id=game_id)
    except psycopg2.errors.ExclusionViolation as e:
        raise UserFacingError("Can't start a new round, another round is already running!")
    except psycopg2.errors.CheckViolation as e:
        raise UserFacingError("Can't start a new round, already in last round!")


def end_round(game_id: int) -> None:
    queries.end_round(game_id=game_id)


class LeaderBoardEntry(pydantic.BaseModel):
    name: str
    points: int
    is_zombie: bool
    is_initial_zombie: bool


def get_leader_board() -> list[LeaderBoardEntry]:
    active_game_id = get_active_game_id()
    if activate_game is None:
        return []
    rounds = queries.list_rounds_in_game(game_id=active_game_id)
    touches = queries.list_touches(game_id=active_game_id)
    players = queries.list_players_in_game(game_id=active_game_id)
    player_ids = {player.player_id for player in players}
    initial_zombie_ids = {
        player.player_id for player in players if player.is_initial_zombie
    }

    human_points = calculate_human_points(
        touches, player_ids, initial_zombie_ids, len(rounds)
    )

    entries = [
        LeaderBoardEntry(
            name=player.name,
            points=human_points.get(player.player_id, 0),
            is_zombie=player.player_id not in human_points,
            is_initial_zombie=player.player_id in initial_zombie_ids,
        )
        for player in players
    ]

    return sorted(entries, key=lambda e: (int(e.is_initial_zombie) or e.points, e.name), reverse=True)


def calculate_human_points(
    touches: list[queries.list_touches.Row],
    player_ids: set[int],
    initial_zombie_ids: set[int],
    rounds: int,
) -> dict[int, int]:
    zombies = set(initial_zombie_ids)
    humans = player_ids - zombies

    touch_events = sorted(touches, key=lambda touch: touch.when_touched)

    points = collections.defaultdict(int)
    when_turned_zombie = {
        zombie: datetime.datetime(datetime.MINYEAR, 1, 1) for zombie in zombies
    }

    rounds_and_touches = [
        (round_, [touch for touch in touch_events if touch.round_number == round_])
        for round_ in range(1, rounds + 1)
    ]

    for round_, touches_in_round in rounds_and_touches:
        untouched = set(humans)
        for touch in touches_in_round:
            points[touch.left_player_id] += 1
            points[touch.right_player_id] += 1
            participants = {touch.left_player_id, touch.right_player_id}
            if touch.left_player_id in zombies or touch.right_player_id in zombies:
                zombies |= participants
                when_turned_zombie[touch.left_player_id] = (
                    when_turned_zombie.get(touch.left_player_id) or touch.when_touched
                )
                when_turned_zombie[touch.right_player_id] = (
                    when_turned_zombie.get(touch.right_player_id) or touch.when_touched
                )
            untouched -= participants
        zombies |= untouched
        for player_id in untouched:
            when_turned_zombie[player_id] = when_turned_zombie.get(
                player_id
            ) or datetime.datetime(datetime.MINYEAR, 1, 1)
        humans -= zombies

    return {human_id: points[human_id] for human_id in humans}
