CREATE TABLE games (
    game_id BIGINT PRIMARY KEY,
    is_active BOOLEAN NOT NULL DEFAULT false
);

CREATE UNIQUE INDEX only_one_active_game ON games(is_active) WHERE is_active = true;

CREATE TABLE players (
    player_id BIGINT PRIMARY KEY,
    game_id BIGINT NOT NULL references games(game_id),
    name TEXT NOT NULL,
    nfc_id TEXT NOT NULL,

    UNIQUE (game_id, name),
    UNIQUE (game_id, nfc_id)
);

CREATE TABLE rounds (
    round_id BIGINT PRIMARY KEY,
    game_id BIGINT NOT NULL references games(game_id),
    round_number INTEGER NOT NULL,

    when_started DATETIME NOT NULL DEFAULT now(),
    when_ended DATETIME,

    UNIQUE (game_id, round_number),
    CHECK (round_number <= 3 AND round_number >= 1),

    CHECK (when_started < when_ended),
    CONSTRAINT no_overlapping_times EXCLUDE USING GIST (
        game_id WITH =,
        period(when_started, CASE WHEN when_ended IS NULL THEN 'infinity' ELSE when_ended END) WITH &&
    )
);

CREATE TABLE touches (
    touch_id BIGINT PRIMARY KEY,
    round_id BIGINT NOT NULL references rounds(round_id),
    when_touched DATETIME NOT NULL DEFAULT now(),
    left_player BIGINT NOT NULL references players(player_id),
    right_player BIGINT NOT NULL references players(player_id)
);
