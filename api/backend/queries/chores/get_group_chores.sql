SELECT c.*, u.first_name, u.last_name
FROM chores c
JOIN users u ON c.created_by = u.user_id
WHERE c.group_id = %(group_id)s
  AND (%(incomplete_only)s = FALSE OR c.completed_at IS NULL)
ORDER BY c.due_at ASC;
