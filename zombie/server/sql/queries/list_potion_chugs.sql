SELECT 
    potion_chugs.player_id AS player_id,
    potion_chugs.when_created AS when_created
FROM potion_chugs
JOIN players ON potion_chugs.player_id = players.player_id
WHERE players.game_id = %(game_id)s
ORDER BY when_created ASC
