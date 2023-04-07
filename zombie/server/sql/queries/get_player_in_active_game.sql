SELECT 
    games.game_id AS game_id,
    (SELECT players.name FROM players WHERE players.nfc_id = %(nfc_id)s) AS name
FROM games
WHERE games.is_active