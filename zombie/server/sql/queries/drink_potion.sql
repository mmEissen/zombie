/*
 Columns:
 potion_chug_id: bigint
 */
INSERT INTO potion_chugs (player_id)
VALUES (
        (
            SELECT (
                    SELECT player_id
                    FROM players
                        JOIN games ON games.game_id = players.game_id
                    WHERE players.nfc_id = %(nfc_id)s
                        AND games.is_active
                )
            FROM rounds
                INNER JOIN games ON games.game_id = rounds.game_id
                AND rounds.when_ended IS NULL
                AND games.is_active
                AND games.is_started
        )
    )
RETURNING potion_chug_id