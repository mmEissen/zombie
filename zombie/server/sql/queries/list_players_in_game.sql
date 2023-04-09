SELECT 
    players.player_id AS player_id,
    players.is_initial_zombie AS is_initial_zombie,
    players.nfc_id AS nfc_id,
    players.name AS name
FROM players
WHERE players.game_id = %(game_id)s
ORDER BY players.name