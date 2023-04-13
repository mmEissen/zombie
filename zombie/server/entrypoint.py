import flask
import psql2py_core

from zombie.server import conf, db, admin, api, player, logic


def create_app(config: conf.AppConfig):
    app = flask.Flask(__name__)

    db.set_db_config(config.db)
    psql2py_core.set_connection_manager(db.connection)

    app.config.from_mapping(
        SECRET_KEY=config.flask.secret_key,
        DEBUG=config.env in ("dev", "test"),
        TESTING=config.env == "test",
    )

    app.register_blueprint(admin.blueprint)
    app.register_blueprint(api.blueprint)
    app.register_blueprint(player.blueprint)

    app.register_error_handler(logic.UserFacingError, handle_user_facing_error)
    app.register_error_handler(ValueError, handle_value_error)

    return app


def handle_user_facing_error(exception: logic.UserFacingError):
    return flask.jsonify({"error": exception.message}), 400


def handle_value_error(exception: ValueError):
    if str(exception) != "A string literal cannot contain NUL (0x00) characters.":
        raise exception
    
    return flask.jsonify({"error": "Detected NUL (0x00) in input."}), 400