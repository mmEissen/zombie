/*
Columns:
    null: null
*/
UPDATE games 
SET is_active = true
WHERE game_id = %(game_id)s
RETURNING null AS null
