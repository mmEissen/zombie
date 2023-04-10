SELECT 
    touches.left_player AS left_player_id,
    touches.right_player AS right_player_id,
    touches.when_created AS when_touched,
    rounds.round_number AS round_number
FROM touches
JOIN rounds ON touches.round_id = rounds.round_id
WHERE rounds.game_id = %(game_id)s
