from __future__ import annotations

import dataclasses
import datetime
from hypothesis.stateful import (
    Bundle,
    rule,
    invariant,
    precondition,
)
from hypothesis import settings
import hypothesis.strategies as st


import urllib.parse

from .state_machine import RuleBasedStateMachineWithClient


@dataclasses.dataclass
class Player:
    name: str
    nfc_id: str
    is_zombie: bool = False


class Model:
    def __init__(self) -> None:
        self.players_by_nfc_id: dict[str, Player] = {}
        self.is_game_started = False

    def _name_exists(self, name: str) -> bool:
        return name in [p.name for p in self.players_by_nfc_id.values()]

    def add_player(self, name: str, nfc_id: str) -> None:
        if (
            len(name) < 3
            or self.is_game_started
            or len(nfc_id) < 1
            or "\0" in name
            or "\0" in nfc_id
            or self._name_exists(name)
        ):
            return
        if nfc_id in self.players_by_nfc_id:
            self.players_by_nfc_id[nfc_id].name = name
            return
        self.players_by_nfc_id[nfc_id] = Player(name, nfc_id)

    def toggle_zombie(self, nfc_id: str) -> None:
        if self.is_game_started:
            return
        try:
            player = self.players_by_nfc_id[nfc_id]
        except KeyError:
            return

        player.is_zombie = not player.is_zombie

    def start_game(self) -> None:
        self.is_game_started = True

    def list_players(self) -> list[tuple[str, str, bool]]:
        return sorted((p.name, p.nfc_id, p.is_zombie) for p in self.players_by_nfc_id.values())


class StateMachine(RuleBasedStateMachineWithClient):
    def __init__(self) -> None:
        super().__init__()

        self.game_id = self.client.put("/api/game").json["id_"]
        self.client.put("/api/active-game", json={"game_id": self.game_id})

        self.player_id_by_nfc: dict[str, int] = {}

        self.model = Model()

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
        self.client.post(f"/api/games/{self.game_id}/start")
        self.model.start_game()

    @rule(name=names, nfc_id=nfc_ids)
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

    @rule(nfc_id=nfc_ids)
    def toggle_zombie(self, nfc_id: str):
        player_id = self.player_id_by_nfc.get(nfc_id, 999_999_999)
        self.model.toggle_zombie(nfc_id)
        self.client.post("/api/toggle-zombie", json={"player_id": player_id})

    @invariant()
    def player_list_matches(self):
        real_players = [
            (p["name"], p["uid"], p["is_initial_zombie"]) for p in
            self.client.get(f"/api/game/{self.game_id}").json["players"]
        ]
        real_players.sort()
        assert real_players == self.model.list_players()


TestPlayerSetup = StateMachine.make_test_case()
TestPlayerSetup.settings = settings(
    max_examples=100,
    deadline=datetime.timedelta(seconds=1),
    stateful_step_count=20,
)
