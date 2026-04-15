SELECT
    gs.household_size,
    COUNT(DISTINCT gs.group_id) AS total_groups,
    ROUND(AVG(gs.chore_count), 1) AS avg_chores,
    ROUND(AVG(gs.completed_chore_count), 1) AS avg_completed_chores,
    ROUND(AVG(gs.bill_count), 1) AS avg_bills,
    ROUND(AVG(gs.event_count), 1) AS avg_events
FROM (
    SELECT
        g.group_id,
        COUNT(DISTINCT gm.user_id) AS household_size,
        COUNT(DISTINCT c.chore_id) AS chore_count,
        COUNT(DISTINCT CASE WHEN c.completed_at IS NOT NULL THEN c.chore_id END) AS completed_chore_count,
        COUNT(DISTINCT b.bill_id) AS bill_count,
        COUNT(DISTINCT e.event_id) AS event_count
    FROM `groups` g
    LEFT JOIN group_members gm ON g.group_id = gm.group_id
    LEFT JOIN chores c ON g.group_id = c.group_id
    LEFT JOIN bills b ON g.group_id = b.group_id
    LEFT JOIN events e ON g.group_id = e.group_id
    GROUP BY g.group_id
) AS gs
GROUP BY gs.household_size
ORDER BY gs.household_size;
