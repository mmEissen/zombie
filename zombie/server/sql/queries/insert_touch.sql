/*
 Columns:
 game_id: bigint
 */
INSERT INTO touches (round_id, left_player, right_player)
VALUES (
        (
            SELECT round_id
            FROM rounds
                INNER JOIN games ON games.game_id = rounds.game_id
                AND rounds.when_ended IS NULL
                AND games.is_active
                AND games.is_started
        ),
        (
            SELECT min(player_id)
            FROM players
            JOIN games ON games.game_id = players.game_id
            WHERE nfc_id in (%(left_player_nfc)s, %(right_player_nfc)s)
            AND games.is_active
        ),
        (
            SELECT max(player_id)
            FROM players
            JOIN games ON games.game_id = players.game_id
            WHERE nfc_id in (%(left_player_nfc)s, %(right_player_nfc)s)
            AND games.is_active
        )
    )
RETURNING touch_id