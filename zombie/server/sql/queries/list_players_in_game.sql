SELECT 
    players.name AS name, 
    players.nfc_id AS nfc_id
FROM players
WHERE players.game_id = %(game_id)s
ORDER BY players.name