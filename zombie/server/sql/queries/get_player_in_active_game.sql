SELECT 
    games.game_id AS game_id,
    players.name AS name
FROM players
RIGHT OUTER JOIN games ON players.game_id = games.game_id
WHERE players.nfc_id = %(nfc_id)s OR players.nfc_id IS NULL
AND games.is_active