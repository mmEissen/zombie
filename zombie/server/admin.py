import flask


blueprint = flask.Blueprint("admin", __name__, template_folder="templates", url_prefix="/admin")


@blueprint.route("/")
def root():
    return flask.render_template("admin.html")
