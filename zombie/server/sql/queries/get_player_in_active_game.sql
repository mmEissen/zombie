SELECT 
    players.player_id AS player_id,
    games.game_id AS game_id,
    games.is_started AS is_started,
    players.name AS name
FROM games
LEFT OUTER JOIN players ON players.game_id = games.game_id AND players.nfc_id = %(nfc_id)s
WHERE games.is_active