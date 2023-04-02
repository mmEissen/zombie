import click
import environ

from zombie.server import conf, db


@click.group()
def cli():
    config = environ.to_config(conf.AppConfig)
    db.set_db_config(config.db)


@cli.command()
def init_db():
    db.init()


cli()
