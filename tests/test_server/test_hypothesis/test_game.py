from __future__ import annotations

import dataclasses
import datetime
from typing import Callable
from hypothesis.stateful import (
    Bundle,
    rule,
    invariant,
    precondition,
    initialize,
    multiple,
)
from hypothesis import Verbosity, settings, reproduce_failure
import hypothesis.strategies as st


import urllib.parse

from .state_machine import RuleBasedStateMachineWithClient


_PLAYERS = [(f"player_v{i+1}", f"nfc_id_v{i+1}") for i in range(5)]


@dataclasses.dataclass
class Player:
    name: str
    nfc_id: str
    time_func: Callable[[], datetime.datetime]
    is_initial_zombie: bool = False
    is_zombie: bool = False
    points: int = 0
    when_zombified: tuple[datetime.datetime, int] | None = None
    _touched_this_round: set[str] = dataclasses.field(default_factory=set)
    _did_touch_humans_this_round: bool = False
    _did_drink_potion: bool = False
    _round_number: int = 1

    def _get_touched_by(self, other: Player) -> None:
        if self.is_zombie or other.nfc_id in self._touched_this_round:
            return
        self._touched_this_round.add(other.nfc_id)
        if other.is_zombie:
            self.when_zombified = (self.time_func(), self._round_number)
            self.is_zombie = True
            return
        self._did_touch_humans_this_round = True
        self.points += 1

    def touch(self, other: Player) -> None:
        self._get_touched_by(other)
        other._get_touched_by(self)

    def drink_potion(self) -> None:
        if self._did_drink_potion:
            return
        if self.when_zombified is not None:
            when_zombified, round_zombified = self.when_zombified
            now = self.time_func()
            if (
                now - when_zombified < datetime.timedelta(minutes=10)
                and round_zombified == self._round_number
            ):
                self.is_zombie = False
                self.when_zombified = None
        self._did_drink_potion = True

    def end_round(self) -> None:
        if not self._did_touch_humans_this_round:
            self.is_zombie = True
        self._touched_this_round = set()
        self._did_touch_humans_this_round = False
        self._round_number += 1


class Model:
    def __init__(self, time_func: Callable[[], datetime.datetime]) -> None:
        self.players_by_nfc_id: dict[str, Player] = {}
        self.round_number = 0
        self.is_round_started = False
        self.time_func = time_func

    def add_player(self, name: str, nfc_id: str) -> None:
        self.players_by_nfc_id[nfc_id] = Player(name, nfc_id, self.time_func)

    def make_zombie(self, nfc_id: str) -> None:
        self.players_by_nfc_id[nfc_id].is_zombie = True
        self.players_by_nfc_id[nfc_id].is_initial_zombie = True

    def touch(self, left_nfc: str, right_nfc: str) -> None:
        if not self.is_round_started or left_nfc == right_nfc:
            return
        try:
            left = self.players_by_nfc_id[left_nfc]
            right = self.players_by_nfc_id[right_nfc]
        except KeyError:
            return
        left.touch(right)

    def drink_potion(self, nfc_id: str) -> None:
        if not self.is_round_started:
            return
        self.players_by_nfc_id[nfc_id].drink_potion()

    def start_next_round(self) -> None:
        if self.round_number >= 3 or self.is_round_started:
            return
        self.round_number += 1
        self.is_round_started = True

    def end_round(self) -> None:
        if not self.is_round_started:
            return
        self.is_round_started = False
        for player in self.players_by_nfc_id.values():
            player.end_round()

    def scores(self) -> list[Player]:
        scores = [
            (p.name, 0 if p.is_zombie else p.points, p.is_initial_zombie, p.is_zombie)
            for p in self.players_by_nfc_id.values()
        ]
        return sorted(
            scores,
            key=lambda p: (int(p[2]) or p[1], p[0]),
            reverse=True,
        )


class StateMachine(RuleBasedStateMachineWithClient):
    def __init__(self) -> None:
        super().__init__()

        self.game_id = self.client.put("/api/game").json["id_"]
        self.client.put("/api/active-game", json={"game_id": self.game_id})

        self.model = Model(time_func=lambda: self.fake_time.current_time)

        self.player_id_by_nfc: dict[str, int] = {}

    nfc_ids = Bundle("nfc_ids")

    @initialize(target=nfc_ids)
    def register_players_and_start_game(self):
        for name, nfc_id in _PLAYERS:
            self.register_player(name, nfc_id)

        for _, nfc_id in _PLAYERS[:2]:
            self.make_zombie(nfc_id)

        self.start_game()

        return multiple(*[nfc_id for _, nfc_id in _PLAYERS])

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
            self.player_id_by_nfc[nfc_id] = player_id

    def make_zombie(self, nfc_id: str):
        player_id = self.player_id_by_nfc[nfc_id]
        self.model.make_zombie(nfc_id)
        self.client.post("/api/toggle-zombie", json={"player_id": player_id})

    def start_game(self):
        self.client.post(f"/api/games/{self.game_id}/start")

    @rule()
    def wait_10_minutes(self):
        self.fake_time.tick_time(datetime.timedelta(minutes=10))

    @rule(nfc_id=nfc_ids)
    def drink_potion(self, nfc_id: str) -> None:
        self.model.drink_potion(nfc_id)
        self.client.put("/api/potion_chug", json={"nfc_id": nfc_id})

    @rule()
    def start_next_round(self):
        self.model.start_next_round()
        self.client.post(f"/api/games/{self.game_id}/start-round")

    @rule()
    def end_round(self):
        self.model.end_round()
        self.client.post(f"/api/games/{self.game_id}/end-round")

    @rule(left=nfc_ids, right=nfc_ids)
    def touch(self, left: str, right: str) -> None:
        self.model.touch(left, right)
        self.client.put("/api/touch", json={"left_uid": left, "right_uid": right})

    @rule()
    def score_board_matches(self):
        model_scores = self.model.scores()
        real_scores = self.client.get("/api/active-game/leader-board").json
        assert model_scores == [
            (p["name"], p["points"], p["is_initial_zombie"], p["is_zombie"])
            for p in real_scores
        ]


TestGame = StateMachine.make_test_case()
TestGame.settings = settings(
    max_examples=300,
    deadline=datetime.timedelta(seconds=1),
    stateful_step_count=40,
    print_blob=True,
)
