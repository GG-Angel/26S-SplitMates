SELECT
    g.group_id,
    g.group_leader
FROM `groups` g
JOIN users u ON g.group_leader = u.user_id
WHERE u.user_id = %(user_id)s;