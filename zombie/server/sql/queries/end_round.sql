/*
Columns:
    round_id: bigint
*/
UPDATE rounds SET when_ended = now()
WHERE game_id = %(game_id)s
AND when_ended IS NULL
RETURNING round_id