/*
Columns:
    player_id: bigint
*/
UPDATE players
SET is_initial_zombie = NOT is_initial_zombie
WHERE players.player_id = %(player_id)s
RETURNING player_id