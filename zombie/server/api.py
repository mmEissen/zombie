from typing import Generic, TypeVar
import flask
import pydantic
import urllib.parse
from zombie.server import logic
import logging

log = logging.getLogger(__name__)

blueprint = flask.Blueprint("api", __name__, url_prefix="/api")




class PageInfo(pydantic.BaseModel):
    current: str
    next: str | None
    previous: str | None


_T = TypeVar("_T", bound=pydantic.BaseModel)


class PaginatedPage(Generic[_T], pydantic.BaseModel):
    page_info: PageInfo
    data: list[_T]


@blueprint.put(
    "/game",
)
def put_game():
    game = logic.new_game()
    return (
        flask.jsonify(game.dict()),
        201,
    )


class PutActiveGame(pydantic.BaseModel):
    game_id: int


@blueprint.put(
    "/active-game"
)
def put_active_game():
    active_game = PutActiveGame(**flask.request.json)
    logic.activate_game(active_game.game_id)
    return "", 204


@blueprint.get(
    "/active-game",
)
def get_active_game():
    game_id = logic.get_active_game_id()
    if game_id is None:
        return "Not Found", 404
    game_details = logic.get_game_details(game_id)
    if game_details is None:
        return "Not Found", 404
    return flask.jsonify(game_details.dict())


@blueprint.get(
    "/game/<int:game_id>",
)
def get_game(game_id: int):
    game_details = logic.get_game_details(game_id)
    if game_details is None:
        return "Not Found", 404
    return flask.jsonify(game_details.dict())


@blueprint.get(
    "/game/list",
)
def list_games():
    games = logic.list_games()
    page = PaginatedPage(
        page_info=PageInfo(
            current="",
            next=None,
            previous=None,
        ),
        data=games
    )
    return flask.jsonify(page.dict())


class PutPlayer(pydantic.BaseModel):
    name: str
    nfc_id: str


@blueprint.put(
    "/active-game/player",
)
def put_player():
    player = PutPlayer(**flask.request.json)
    logic.create_player_in_active_game(player.name, player.nfc_id)
    return "", 201


@blueprint.get(
    "active-game/player/<uid>",
)
def get_player_in_active_game(uid: str):
    uid = urllib.parse.unquote_plus(uid)
    player = logic.get_player_in_active_game(uid)
    return flask.jsonify(player.dict())


class PutTouchData(pydantic.BaseModel):
    left_uid: str
    right_uid: str


@blueprint.put(
    "/touch",
)
def put_touch():
    data = PutTouchData(**flask.request.json)
    log.warning(str(data))

    logic.make_touch(data.left_uid, data.right_uid)

    return "", 201


class PutPotionChugData(pydantic.BaseModel):
    nfc_id: str


@blueprint.put(
    "/potion_chug",
)
def put_potion_chug():
    data = PutPotionChugData(**flask.request.json)

    logic.drink_potion(data.nfc_id)

    return "", 201


@blueprint.post(
    "/games/<int:game_id>/start",
)
def start_game(game_id: int):
    logic.start_game(game_id)

    return "", 201


class MakeZombiesData(pydantic.BaseModel):
    number_zombies: int

@blueprint.post(
    "/games/<int:game_id>/make-zombies",
)
def make_zombies(game_id: int):
    data = MakeZombiesData(**flask.request.json)
    logic.make_zombies(game_id, data.number_zombies)

    return "", 201


class ToggleZombiesData(pydantic.BaseModel):
    player_id: int


@blueprint.post(
    "/toggle-zombie",
)
def toggle_zombie():
    data = ToggleZombiesData(**flask.request.json)
    logic.toggle_zombie(data.player_id)

    return "", 201


@blueprint.post(
    "/games/<int:game_id>/start-round",
)
def start_round(game_id: int):
    logic.start_round(game_id)

    return "", 201


@blueprint.post(
    "/games/<int:game_id>/end-round",
)
def end_round(game_id: int):
    logic.end_round(game_id)

    return "", 201


@blueprint.get(
    "active-game/leader-board-anonymized"
)
def get_anonymous_leader_board():
    leader_board = logic.get_leader_board()
    for entry in leader_board:
        entry.name = ""

    return flask.jsonify([entry.dict() for entry in leader_board])


@blueprint.get(
    "active-game/leader-board"
)
def get_leader_board():
    leader_board = logic.get_leader_board()
    
    return flask.jsonify([entry.dict() for entry in leader_board])
