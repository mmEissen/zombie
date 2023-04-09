SELECT 
    left_player.player_id AS left_player_id,
    left_player.name AS left_player_name,
    right_player.player_id AS right_player_id,
    right_player.name AS right_player_name
FROM touches
JOIN players AS left_player ON touches.left_player = left_player.player_id
JOIN players AS right_player ON touches.right_player = right_player.player_id
JOIN rounds ON touches.round_id = rounds.round_id
WHERE rounds.game_id = %(game_id)s
