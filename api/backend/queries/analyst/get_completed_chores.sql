SELECT title, effort, COUNT(*) AS times_completed
FROM chores
WHERE completed_at IS NOT NULL
GROUP BY title, effort
ORDER BY times_completed DESC;
