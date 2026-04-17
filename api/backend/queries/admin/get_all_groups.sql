SELECT
    g.group_id,
    g.name,
    g.group_leader,
    COUNT(gm.user_id) AS member_count
FROM `groups` g
LEFT JOIN group_members gm ON g.group_id = gm.group_id
GROUP BY g.group_id, g.name, g.group_leader
ORDER BY g.group_id;