import flask
from zombie.server import logic

blueprint = flask.Blueprint("admin", __name__, template_folder="templates", url_prefix="/admin")


@blueprint.route("/")
def root():
    games = logic.list_games()

    return flask.render_template("admin_home.html", games=games)

