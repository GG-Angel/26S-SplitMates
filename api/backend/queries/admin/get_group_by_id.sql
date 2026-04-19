SELECT
    g.group_id,
    g.name,
    g.address,
    g.city,
    g.state,
    g.zip_code,
    g.group_leader,
    COUNT(gm.user_id) AS member_count
FROM `groups` g
LEFT JOIN group_members gm ON g.group_id = gm.group_id
WHERE g.group_id = %(group_id)s
GROUP BY g.group_id, g.name, g.address, g.city, g.state, g.zip_code, g.group_leader;