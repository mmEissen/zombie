import click
import environ

from zombie.server import conf, db

import traceback

@click.group()
def cli():
    config = environ.to_config(conf.AppConfig)
    db.set_db_config(config.db)


@cli.command()
def init_db():
    try:
        db.init()
    except Exception:
        traceback.print_exc()


cli()
