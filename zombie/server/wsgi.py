import environ
from zombie.server import conf, entrypoint

app = entrypoint.create_app(environ.to_config(conf.AppConfig))
