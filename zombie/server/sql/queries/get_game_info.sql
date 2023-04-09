SELECT 
    games.game_id as game_id,
    games.when_created as when_created,
    games.is_active as is_active,
    games.is_started as is_started,
    count(players.player_id) as player_count,
    coalesce(max(rounds.round_number), 0) as round_number,
    CASE
        WHEN coalesce(max(rounds.round_number), 0) = 0 THEN true
        ELSE bool_and(rounds.when_ended IS NOT NULL)
    END AS round_ended
FROM games
LEFT OUTER JOIN players ON players.game_id = games.game_id
LEFT OUTER JOIN rounds ON rounds.game_id = games.game_id
WHERE games.game_id = ANY(%(game_ids)s)
GROUP BY games.game_id
