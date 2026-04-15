SELECT
    al.log_id,
    al.details,
    al.action_type,
    al.target_table,
    al.target_id,
    al.performed_at,
    u.first_name,
    u.last_name
FROM audit_logs al
JOIN users u ON al.user_id = u.user_id
ORDER BY al.performed_at DESC
LIMIT 5;