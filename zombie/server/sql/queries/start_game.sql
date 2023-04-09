/*
Columns:
    game_id: bigint
*/
UPDATE games
SET is_started = true
WHERE game_id = %(game_id)s
RETURNING game_id
