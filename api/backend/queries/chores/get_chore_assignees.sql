SELECT u.user_id, u.first_name, u.last_name
FROM chore_assignments ca
JOIN users u ON ca.user_id = u.user_id
WHERE ca.chore_id = %(chore_id)s;
