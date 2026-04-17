SELECT
    u.user_id,
    u.first_name,
    u.last_name,
    u.email,
    u.account_status,
    MAX(s.end_time) AS last_session
FROM users u
LEFT JOIN `session` s ON u.user_id = s.user_id
GROUP BY u.user_id, u.first_name, u.last_name, u.email, u.account_status
HAVING u.account_status = 'inactive'
    OR MAX(s.end_time) IS NULL
    OR MAX(s.end_time) < NOW() - INTERVAL 30 DAY
ORDER BY last_session ASC;get_session_summary.sql