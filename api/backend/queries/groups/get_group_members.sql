SELECT u.user_id, u.first_name, u.last_name, gm.joined_at
FROM group_members gm
JOIN users u ON gm.user_id = u.user_id
WHERE gm.group_id = %(group_id)s
ORDER BY u.first_name, u.last_name;
