SELECT g.group_id, g.name, g.address, g.city, g.state, g.zip_code, g.group_leader
FROM group_members gm
JOIN `groups` g ON gm.group_id = g.group_id
WHERE gm.user_id = %(user_id)s
ORDER BY g.group_id;