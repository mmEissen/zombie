CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE IF NOT EXISTS games (
    game_id BIGSERIAL PRIMARY KEY,
    when_created TIMESTAMP DEFAULT now(),

    is_active BOOLEAN NOT NULL DEFAULT false,
    is_started BOOLEAN NOT NULL DEFAULT false
);

CREATE UNIQUE INDEX IF NOT EXISTS only_one_active_game ON games(is_active) WHERE is_active = true;

CREATE TABLE IF NOT EXISTS players (
    player_id BIGSERIAL PRIMARY KEY,
    when_created TIMESTAMP DEFAULT now(),

    game_id BIGINT NOT NULL references games(game_id),
    name TEXT NOT NULL,
    nfc_id TEXT NOT NULL,

    is_initial_zombie BOOLEAN NOT NULL DEFAULT false,

    UNIQUE (game_id, name),
    UNIQUE (game_id, nfc_id),
    CHECK (char_length(name) >= 3),
    CHECK (char_length(name) >= 1)
);

CREATE TABLE IF NOT EXISTS rounds (
    round_id BIGSERIAL PRIMARY KEY,
    when_created TIMESTAMP DEFAULT now(),

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

CREATE UNIQUE INDEX IF NOT EXISTS only_one_active_round ON rounds(when_ended) WHERE when_ended IS NULL;

CREATE TABLE IF NOT EXISTS touches (
    touch_id BIGSERIAL PRIMARY KEY,
    when_created TIMESTAMP DEFAULT now(),
    
    round_id BIGINT NOT NULL references rounds(round_id),
    when_touched TIMESTAMP NOT NULL DEFAULT now(),
    left_player BIGINT NOT NULL references players(player_id),
    right_player BIGINT NOT NULL references players(player_id),

    UNIQUE (round_id, left_player, right_player),
    CHECK (left_player != right_player)
);

CREATE OR REPLACE FUNCTION game_not_started() RETURNS TRIGGER AS $$
DECLARE
    is_game_started BOOLEAN;
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        SELECT INTO is_game_started is_started FROM games WHERE game_id = NEW.game_id;
        IF is_game_started THEN
            RAISE EXCEPTION 'During % of players: Game must not be started',tg_op;
        END IF;
    END IF;

    IF TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN
        SELECT INTO is_game_started is_started FROM games WHERE game_id = OLD.game_id;
        IF is_game_started THEN
            RAISE EXCEPTION 'During % of players: Game must not be started',tg_op;
        END IF;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE 'plpgsql';

CREATE CONSTRAINT TRIGGER game_not_started_trigger
AFTER INSERT OR UPDATE OR DELETE ON players
FOR EACH ROW EXECUTE PROCEDURE game_not_started();
