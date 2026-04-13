SELECT e.*, u.first_name, u.last_name
FROM events e
JOIN users u ON e.created_by = u.user_id
WHERE e.group_id = %(group_id)s
  AND e.starts_at >= CURDATE()
ORDER BY e.starts_at ASC;
