SELECT 
    players.player_id AS player_id,
    games.game_id AS game_id,
    games.is_started AS is_started,
    players.is_initial_zombie AS is_initial_zombie,
    players.name AS name,
    potion_chugs.potion_chug_id IS NOT NULL AS has_chugged_potion
FROM games
LEFT OUTER JOIN players ON players.game_id = games.game_id AND players.nfc_id = %(nfc_id)s
LEFT OUTER JOIN potion_chugs ON potion_chugs.player_id = players.player_id
WHERE games.is_active