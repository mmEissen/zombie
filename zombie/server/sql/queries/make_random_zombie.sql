/*
Columns:
    player_id: bigint
*/
UPDATE players
SET is_initial_zombie = true
WHERE players.player_id in (
    SELECT players.player_id
    FROM players
    WHERE players.game_id = %(game_id)s
    AND NOT players.is_initial_zombie
    ORDER BY random()
    LIMIT coalesce(%(number_zombies)s, 1)
)