SELECT
    u.user_id,
    u.first_name,
    SUM(c.effort + 0) AS chore_points
FROM chores c
JOIN chore_assignments ca ON ca.chore_id = c.chore_id
JOIN users u ON u.user_id = ca.user_id
WHERE c.completed_at IS NOT NULL
  AND c.group_id = %(group_id)s
GROUP BY u.user_id, u.first_name
ORDER BY chore_points DESC;
