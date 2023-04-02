/*
Columns:
    player_id: bigint
*/
INSERT INTO players (game_id, name, nfc_id) 
VALUES (%(game_id)s, %(name)s, %(nfc_id)s) 
RETURNING player_id
