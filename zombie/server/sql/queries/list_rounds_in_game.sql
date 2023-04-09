SELECT 
    round_id AS round_id,
    round_number AS round_number,
    when_started AS when_started,
    when_ended AS when_ended
FROM rounds
WHERE game_id = %(game_id)s
ORDER BY round_number
