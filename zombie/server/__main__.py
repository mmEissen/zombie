import click
import environ

from zombie.server import db, config


@click.group()
def cli():
    conf = environ.to_config(config.AppConfig)
    db.set_db_config({
        "dbname": conf.db.name,
        "user": conf.db.user,
        "password": conf.db.password,
        "host": conf.db.host,
        "port": conf.db.port,
    })


@cli.command()
def init_db():
    db.init()


cli()
