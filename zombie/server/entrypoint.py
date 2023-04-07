import flask
import psql2py_core

from zombie.server import conf, db, admin, api, player


def create_app(config: conf.AppConfig):
    app = flask.Flask(__name__)

    db.set_db_config(config.db)
    psql2py_core.set_connection_manager(db.connection)

    app.config.from_mapping(
        SECRET_KEY=config.flask.secret_key,
    )

    app.register_blueprint(admin.blueprint)
    app.register_blueprint(api.blueprint)
    app.register_blueprint(player.blueprint)

    return app
