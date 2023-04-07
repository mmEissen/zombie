import flask
from zombie.server import logic

blueprint = flask.Blueprint("player", __name__, template_folder="templates", url_prefix="/player")


@blueprint.route("/")
def root():
    return flask.render_template("player_home.html")
