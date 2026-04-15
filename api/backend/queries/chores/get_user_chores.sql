SELECT c.chore_id,
       c.title,
       c.effort,
       c.due_at,
       c.completed_at
FROM chore_assignments ca
JOIN chores c ON ca.chore_id = c.chore_id
WHERE ca.user_id = %(user_id)s
  AND c.completed_at IS NULL
ORDER BY c.due_at ASC;
