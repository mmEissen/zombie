SELECT 
    players.game_id AS game_id,
    players.name AS name
FROM players
RIGHT JOIN games ON players.game_id = games.game_id AND games.is_active
WHERE players.nfc_id = %(nfc_id)s OR players.nfc_id IS NULL
