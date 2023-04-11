import environ


@environ.config(prefix="APP")
class AppConfig:
    @environ.config
    class DB:
        name = environ.var("zombie")
        host = environ.var("postgres")
        port = environ.var(5432, converter=int)
        user = environ.var("zombie")
        password = environ.var("password")
    
    db = environ.group(DB)

    @environ.config
    class Flask:
        secret_key = environ.var("dev")

    flask = environ.group(Flask)

    env = environ.var("prod")
