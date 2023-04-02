/*
Columns:
    round_id: bigint
*/
INSERT INTO rounds (game_id, round_number)
VALUES (%(game_id)s, (SELECT coalesce(max(rounds.round_number), 0) + 1 FROM rounds WHERE game_id = %(game_id)s))
RETURNING round_id
