from typing import Generic, TypeVar
import flask
import pydantic
import urllib.parse
from zombie.server import logic

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
    try:
        logic.create_player_in_active_game(player.name, player.nfc_id)
    except logic.PlayerNameExistsError:
        flask.abort(409)
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

    try:
        logic.make_touch(data.left_uid, data.right_uid)
    except logic.BadTouchError:
        flask.abort(400)

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
