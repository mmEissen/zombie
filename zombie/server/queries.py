# Generated by psql2py

import datetime

import psql2py_core as core
import dataclasses


class _activate_game:
    _STATEMENT = r"""
/*
Columns:
    null: null
*/
UPDATE games 
SET is_active = true
WHERE game_id = %(game_id)s
RETURNING null AS null
"""
    @dataclasses.dataclass
    class Row:
        null: None


    def __call__(
        self,
        *,
        game_id: int,
    ) -> list[Row]:
        """Columns:
        null: null"""
        params = {
            "game_id": game_id,
        }
        return [self.Row(*row) for row in core.execute(self._STATEMENT, params)]

activate_game = _activate_game()

class _deactivate_game:
    _STATEMENT = r"""
/*
Columns:
    null: null
*/
UPDATE games 
SET is_active = false
WHERE game_id = (SELECT game_id FROM games WHERE is_active)
RETURNING null AS null
"""
    @dataclasses.dataclass
    class Row:
        pass
        null: None


    def __call__(
        self,
    ) -> list[Row]:
        """Columns:
        null: null"""
        params = {
        }
        return [self.Row(*row) for row in core.execute(self._STATEMENT, params)]

deactivate_game = _deactivate_game()

class _end_round:
    _STATEMENT = r"""
/*
Columns:
    round_id: bigint
*/
UPDATE rounds SET when_ended = now()
WHERE game_id = %(game_id)s
AND when_ended IS NULL
RETURNING round_id
"""
    @dataclasses.dataclass
    class Row:
        round_id: int


    def __call__(
        self,
        *,
        game_id: int,
    ) -> list[Row]:
        """Columns:
        round_id: bigint"""
        params = {
            "game_id": game_id,
        }
        return [self.Row(*row) for row in core.execute(self._STATEMENT, params)]

end_round = _end_round()

class _get_active_game_id:
    _STATEMENT = r"""
SELECT game_id
FROM games
WHERE is_active
"""
    @dataclasses.dataclass
    class Row:
        pass
        game_id: int


    def __call__(
        self,
    ) -> list[Row]:
        """"""
        params = {
        }
        return [self.Row(*row) for row in core.execute(self._STATEMENT, params)]

get_active_game_id = _get_active_game_id()

class _get_game_info:
    _STATEMENT = r"""
SELECT 
    games.game_id as game_id,
    games.when_created as when_created,
    games.is_active as is_active,
    count(players.player_id) as player_count,
    coalesce(max(rounds.round_number), 0) as round_number,
    CASE
        WHEN coalesce(max(rounds.round_number), 0) = 0 THEN true
        ELSE bool_and(rounds.when_ended IS NOT NULL)
    END AS round_ended
FROM games
LEFT OUTER JOIN players ON players.game_id = games.game_id
LEFT OUTER JOIN rounds ON rounds.game_id = games.game_id
WHERE games.game_id = ANY(%(game_ids)s)
GROUP BY games.game_id
"""
    @dataclasses.dataclass
    class Row:
        game_id: int
        when_created: datetime.datetime
        is_active: bool
        player_count: int
        round_number: int
        round_ended: bool


    def __call__(
        self,
        *,
        game_ids: list[int],
    ) -> list[Row]:
        """"""
        params = {
            "game_ids": game_ids,
        }
        return [self.Row(*row) for row in core.execute(self._STATEMENT, params)]

get_game_info = _get_game_info()

class _get_player_in_active_game:
    _STATEMENT = r"""
SELECT 
    games.game_id AS game_id,
    players.name AS name
FROM games
JOIN players ON players.game_id = games.game_id AND players.nfc_id = %(nfc_id)s
WHERE games.is_active
"""
    @dataclasses.dataclass
    class Row:
        game_id: int
        name: str


    def __call__(
        self,
        *,
        nfc_id: str,
    ) -> list[Row]:
        """"""
        params = {
            "nfc_id": nfc_id,
        }
        return [self.Row(*row) for row in core.execute(self._STATEMENT, params)]

get_player_in_active_game = _get_player_in_active_game()

class _insert_game:
    _STATEMENT = r"""
/*
Columns:
    game_id: bigint
*/
INSERT INTO games DEFAULT VALUES RETURNING game_id
"""
    @dataclasses.dataclass
    class Row:
        pass
        game_id: int


    def __call__(
        self,
    ) -> list[Row]:
        """Columns:
        game_id: bigint"""
        params = {
        }
        return [self.Row(*row) for row in core.execute(self._STATEMENT, params)]

insert_game = _insert_game()

class _insert_player:
    _STATEMENT = r"""
/*
Columns:
    player_id: bigint
*/
INSERT INTO players (game_id, name, nfc_id) 
VALUES ((SELECT game_id FROM games WHERE is_active), %(name)s, %(nfc_id)s)
ON CONFLICT (game_id, nfc_id) DO UPDATE SET name = %(name)s
RETURNING player_id
"""
    @dataclasses.dataclass
    class Row:
        player_id: int


    def __call__(
        self,
        *,
        name: str,
        nfc_id: str,
    ) -> list[Row]:
        """Columns:
        player_id: bigint"""
        params = {
            "name": name,
            "nfc_id": nfc_id,
        }
        return [self.Row(*row) for row in core.execute(self._STATEMENT, params)]

insert_player = _insert_player()

class _list_games:
    _STATEMENT = r"""
SELECT 
    games.game_id AS game_id,
    games.when_created AS when_created
FROM games
WHERE when_created <= %(before)s
ORDER BY games.when_created DESC
LIMIT %(count)s
"""
    @dataclasses.dataclass
    class Row:
        game_id: int
        when_created: datetime.datetime


    def __call__(
        self,
        *,
        before: datetime.datetime,
        count: int,
    ) -> list[Row]:
        """"""
        params = {
            "before": before,
            "count": count,
        }
        return [self.Row(*row) for row in core.execute(self._STATEMENT, params)]

list_games = _list_games()

class _start_round:
    _STATEMENT = r"""
/*
Columns:
    round_id: bigint
*/
INSERT INTO rounds (game_id, round_number)
VALUES (%(game_id)s, (SELECT coalesce(max(rounds.round_number), 0) + 1 FROM rounds WHERE game_id = %(game_id)s))
RETURNING round_id
"""
    @dataclasses.dataclass
    class Row:
        round_id: int


    def __call__(
        self,
        *,
        game_id: int,
    ) -> list[Row]:
        """Columns:
        round_id: bigint"""
        params = {
            "game_id": game_id,
        }
        return [self.Row(*row) for row in core.execute(self._STATEMENT, params)]

start_round = _start_round()

