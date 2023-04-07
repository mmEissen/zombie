/*
Columns:
    null: null
*/
UPDATE games 
SET is_active = false
WHERE game_id = (SELECT game_id FROM games WHERE is_active)
RETURNING null AS null
