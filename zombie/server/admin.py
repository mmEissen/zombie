import flask
from zombie.server import logic

blueprint = flask.Blueprint("admin", __name__, template_folder="templates", url_prefix="/admin")


@blueprint.route("/")
def root():
    games = logic.list_games()

    return flask.render_template("admin_home.html", games=games)


@blueprint.route("/game/<int:game_id>")
def game_details(game_id: int):
    return flask.render_template("admin_game.html", game_id=game_id)
