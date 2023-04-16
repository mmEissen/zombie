import datetime

from zombie.server import db


class MustSetTimeFirst(Exception):
    pass


class FakeDbTime:
    def __init__(self) -> None:
        self.current_time = None

    def set_time(self, mock_time: datetime.datetime) -> None:
        self.current_time = mock_time
        with db.connection() as connection, connection.cursor() as cursor:
            cursor.execute("""
                CREATE OR REPLACE FUNCTION utc_now() 
                RETURNS TIMESTAMP WITHOUT TIME ZONE AS $$
                BEGIN
                    RETURN %(mock_time)s;
                END;
                $$ LANGUAGE plpgsql;
            """, vars= {"mock_time": self.current_time})
    
    def tick_time(self, time_delta=datetime.timedelta(minutes=1)) -> None:
        if self.current_time is None:
            raise MustSetTimeFirst()
        self.set_time(self.current_time + time_delta)
