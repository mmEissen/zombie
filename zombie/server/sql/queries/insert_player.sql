/*
Columns:
    player_id: bigint
*/
INSERT INTO players (game_id, name, nfc_id) 
VALUES ((SELECT game_id FROM games WHERE is_active), %(name)s, %(nfc_id)s)
ON CONFLICT (game_id, nfc_id) DO UPDATE SET name = %(name)s
RETURNING player_id
