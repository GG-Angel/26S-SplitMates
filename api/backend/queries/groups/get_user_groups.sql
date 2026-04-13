SELECT 
    g.group_id,
    g.group_leader,
    g.name,
    g.city,
    g.state,
    (SELECT COUNT(*) FROM group_members WHERE group_id = g.group_id) AS member_count
FROM `groups` g
JOIN group_members gm ON g.group_id = gm.group_id
WHERE gm.user_id = %(user_id)s;