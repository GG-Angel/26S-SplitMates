SELECT c.chore_id,
       c.title,
       c.effort,
       c.due_at,
       c.completed_at,
       CASE WHEN ca_mine.user_id IS NOT NULL THEN 'assigned' ELSE 'communal' END AS assignment_type
FROM chores c
LEFT JOIN chore_assignments ca_mine
    ON ca_mine.chore_id = c.chore_id AND ca_mine.user_id = %(user_id)s
WHERE c.completed_at IS NULL
  AND (%(group_id)s IS NULL OR c.group_id = %(group_id)s)
  AND (
    ca_mine.user_id IS NOT NULL
    OR NOT EXISTS (
        SELECT 1 FROM chore_assignments ca2 WHERE ca2.chore_id = c.chore_id
    )
  )
ORDER BY c.due_at ASC;
