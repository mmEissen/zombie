CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE IF NOT EXISTS games (
    game_id BIGSERIAL PRIMARY KEY,
    is_active BOOLEAN NOT NULL DEFAULT false
);

CREATE UNIQUE INDEX IF NOT EXISTS only_one_active_game ON games(is_active) WHERE is_active = true;

CREATE TABLE IF NOT EXISTS players (
    player_id BIGSERIAL PRIMARY KEY,
    game_id BIGINT NOT NULL references games(game_id),
    name TEXT NOT NULL,
    nfc_id TEXT NOT NULL,

    UNIQUE (game_id, name),
    UNIQUE (game_id, nfc_id)
);

CREATE TABLE IF NOT EXISTS rounds (
    round_id BIGSERIAL PRIMARY KEY,
    game_id BIGINT NOT NULL references games(game_id),
    round_number INTEGER NOT NULL,

    when_started TIMESTAMP NOT NULL DEFAULT now(),
    when_ended TIMESTAMP,

    UNIQUE (game_id, round_number),
    CHECK (round_number <= 3 AND round_number >= 1),

    CHECK (when_started < when_ended),
    CONSTRAINT no_overlapping_times EXCLUDE USING GIST (
        game_id WITH =,
        tsrange(when_started, coalesce(when_ended, '3000-01-01 00:00')) WITH &&
    )
);

CREATE TABLE IF NOT EXISTS touches (
    touch_id BIGSERIAL PRIMARY KEY,
    round_id BIGINT NOT NULL references rounds(round_id),
    when_touched TIMESTAMP NOT NULL DEFAULT now(),
    left_player BIGINT NOT NULL references players(player_id),
    right_player BIGINT NOT NULL references players(player_id)
);
