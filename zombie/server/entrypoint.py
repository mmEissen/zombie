import flask

from zombie.server import conf, db, admin


def create_app(config: conf.AppConfig):
    app = flask.Flask(__name__)

    db.set_db_config(config.db)

    app.config.from_mapping(
        SECRET_KEY=config.flask.secret_key,
    )

    app.register_blueprint(admin.blueprint)

    return app
