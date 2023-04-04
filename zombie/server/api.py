from typing import Generic, TypeVar
import flask
import pydantic
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
        {"Location": flask.url_for("api.get_game", game_id=game.id_)},
    )


@blueprint.get(
    "/game/<int:game_id>",
)
def get_game(game_id: int):
    game = logic.get_game(game_id)
    if game is None:
        return "Not Found", 404
    return flask.jsonify(game.dict())


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
