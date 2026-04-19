SELECT
    u.user_id,
    u.first_name,
    u.last_name,
    COUNT(s.session_id) AS total_sessions,
    ROUND(AVG(s.duration), 1) AS avg_duration_mins,
    HOUR(s.start_time) AS hour_of_day
FROM `sessions` s
JOIN users u ON s.user_id = u.user_id
GROUP BY u.user_id, u.first_name, u.last_name, HOUR(s.start_time)
ORDER BY hour_of_day ASC;