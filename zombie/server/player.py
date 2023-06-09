import flask

blueprint = flask.Blueprint("player", __name__, template_folder="templates", url_prefix="/player")


@blueprint.route("/")
def root():
    uid = flask.request.args.get("uid")
    return flask.render_template("player_home.html", uid=uid)


@blueprint.route("/scores")
def scores_screen():
    return flask.render_template("scores_screen.html")
