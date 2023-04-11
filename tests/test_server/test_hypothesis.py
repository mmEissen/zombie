import dataclasses
import datetime
import environ
from hypothesis.stateful import (
    Bundle,
    RuleBasedStateMachine,
    rule,
    run_state_machine_as_test,
    invariant,
    precondition,
)
from hypothesis import settings
import hypothesis.strategies as st

import psql2py_core
import pg_docker

from zombie.server import conf, entrypoint, db
import urllib.parse


@dataclasses.dataclass(frozen=True)
class Player:
    name: str
    nfc_id: str


@dataclasses.dataclass
class Score:
    name: str
    points: str
    is_zombie: bool
    is_infected: bool


class ZombieGameModel:
    def __init__(self) -> None:
        self.known_nfc_ids: set[str] = set()
        self.players: set[Player] = set()
        self.players_by_name: dict[str, Player] = {}
        self.players_by_nfc_id: dict[str, Player] = {}
        self.points: dict[Player, int] = {}
        self.zombies: set[Player] = set()
        self.infected: set[Player] = set()
        self.round = 0
        self.is_round_started = False
        self.touched_this_round: set[Player] = set()
        self.is_game_started = False

    def add_player(self, name: str, nfc_id: str) -> None:
        if (
            len(name) < 3
            or self.is_game_started
            or len(nfc_id) < 1
            or "\0" in name
            or "\0" in nfc_id
            or name in self.players_by_name
        ):
            return
        if nfc_id in nfc_id in self.players_by_nfc_id:
            existing = self.players_by_nfc_id[nfc_id]
            del self.players_by_nfc_id[nfc_id]
            del self.players_by_name[existing.name]
            self.players -= {existing}
            self.zombies -= {existing}
            self.infected -= {existing}
        player = Player(name, nfc_id)
        self.players.add(player)
        self.players_by_nfc_id[nfc_id] = player
        self.players_by_name[name] = player
        self.points[player] = 0

    def toggle_zombie(self, name: str) -> None:
        if self.is_game_started:
            return
        try:
            player = self.players_by_name[name]
        except KeyError:
            return

        if player in self.zombies:
            self.zombies.remove(player)
            self.infected.remove(player)
        else:
            self.zombies.add(player)
            self.infected.add(player)

    def touch(self, left_nfc_id: str, right_nfc_id: str) -> None:
        if not self.is_round_started or self.is_round_ended:
            return

        left_player = self.players_by_nfc_id[left_nfc_id]
        right_player = self.players_by_nfc_id[right_nfc_id]

        if left_player in self.infected and right_player not in self.infected:
            self.infected.add(right_player)
            self.points[right_player] = 0

        if right_player in self.infected and left_player not in self.infected:
            self.infected.add(left_player)
            self.points[left_player] = 0

        if left_player not in self.infected and right_player not in self.infected:
            self.points[left_player] += 2
            self.points[right_player] += 1
            self.touched_this_round.add(left_player)
            self.touched_this_round.add(right_player)

    def start_game(self) -> None:
        self.is_game_started = True

    def start_next_round(self) -> None:
        if not self.is_game_started or self.is_round_started or self.round >= 3:
            return
        self.is_round_started = True
        self.round += 1

    def end_round(self) -> None:
        if not self.is_round_started:
            return
        self.is_round_started = False
        untouched = self.players - self.touched_this_round - self.infected
        self.infected |= untouched
        self.touched_this_round = set()

    def get_scores(self) -> list[Score]:
        return sorted(
            [
                Score(
                    name=player.name,
                    points=self.points[player],
                    is_zombie=player in self.zombies,
                    is_infected=player in self.infected,
                )
                for player in self.players
            ],
            key=lambda score: (int(score.is_zombie) or score.points, score.name),
            reverse=True,
        )


class ZombieStateMachine(RuleBasedStateMachine):
    def __init__(self, pg_database_pool: pg_docker.DatabasePool) -> None:
        super().__init__()
        self._db_manager = pg_database_pool.database()
        db_config = self._db_manager.__enter__()
        config = environ.to_config(
            conf.AppConfig,
            {
                "APP_DB_HOST": db_config.host,
                "APP_DB_NAME": db_config.dbname,
                "APP_DB_USER": db_config.user,
                "APP_DB_PORT": db_config.port,
                "APP_DB_PASSWORD": db_config.password,
                "APP_ENV": "test",
            },
        )

        app = entrypoint.create_app(config)

        self.player_id_by_name: dict[str, int] = {}

        self.client = app.test_client()
        response = self.client.put("/api/game")

        self.game_id = response.json["id_"]
        self.client.put("/api/active-game", json={"game_id": self.game_id})

        self.model = ZombieGameModel()

    def start_game(self):
        self.model.start_game()
        self.client.post(f"/api/games/{self.game_id}/start")

    def start_next_round(self):
        self.model.start_next_round()
        self.client.post(f"/api/games/{self.game_id}/start-round")

    def end_round(self):
        self.model.end_round()
        self.client.post(f"/api/games/{self.game_id}/end-round")

    def register_player(self, name: str, nfc_id: str):
        self.model.add_player(name, nfc_id)
        response = self.client.put(
            "/api/active-game/player", json={"name": name, "nfc_id": nfc_id}
        )
        if response.status_code == 201:
            response = self.client.get(
                f"/api/active-game/player/{urllib.parse.quote_plus(nfc_id)}"
            )
            assert response.status_code == 200
            player_id = response.json["player_id"]
            self.player_id_by_name[name] = player_id

    def toggle_zombie(self, name: str):
        player_id = self.player_id_by_name.get(name, 999_999)
        self.model.toggle_zombie(name)
        self.client.post("/api/toggle-zombie", json={"player_id": player_id})

    def touch(self, left_nfc_id: str, right_nfc_id: str):
        self.model.touch(left_nfc_id, right_nfc_id)
        self.client.put(
            "/api/touch", json={"left_uid": left_nfc_id, "right_uid": right_nfc_id}
        )

    def score_boards_match(self):
        model_scores = self.model.get_scores()
        real_scores = self.client.get("/api/active-game/leader-board").json
        assert len(model_scores) == len(real_scores)
        for model_entry, real_entry in zip(model_scores, real_scores):
            assert model_entry.name == real_entry["name"]
            assert model_entry.points == real_entry["points"]
            assert model_entry.is_zombie == real_entry["is_initial_zombie"]
            assert model_entry.is_infected == real_entry["is_zombie"]

    def teardown(self):
        self._db_manager.__exit__(None, None, None)


def test_player_registration(pg_database_pool: pg_docker.DatabasePool):
    class StateMachine(ZombieStateMachine):
        def __init__(self) -> None:
            super().__init__(pg_database_pool)

        names = Bundle("names")
        nfc_ids = Bundle("nfc_ids")

        @rule(target=names, name=st.text())
        def add_name(self, name: str):
            return name

        @rule(target=nfc_ids, nfc_id=st.text())
        def add_nfc_id(self, nfc_id: str):
            return nfc_id

        @rule()
        def start_game(self):
            super().start_game()

        @rule(name=names)
        def toggle_zombie(self, name: str):
            return super().toggle_zombie(name)

        @rule(name=names, nfc_id=nfc_ids)
        def register_player(self, name: str, nfc_id: str):
            super().register_player(name, nfc_id)

        @invariant()
        def score_boards_match(self):
            super().score_boards_match()

        def teardown(self):
            self._db_manager.__exit__(None, None, None)

    run_state_machine_as_test(
        StateMachine,
        settings=settings(
            max_examples=50,
            deadline=datetime.timedelta(seconds=1),
            stateful_step_count=20,
        ),
    )
