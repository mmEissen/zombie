SELECT 
    games.game_id AS game_id,
    games.when_created AS when_created
FROM games
WHERE when_created <= %(before)s
ORDER BY games.when_created DESC
LIMIT %(count)s
