SELECT 1
FROM group_members
WHERE group_id = %(group_id)s
  AND user_id = %(user_id)s
LIMIT 1;
