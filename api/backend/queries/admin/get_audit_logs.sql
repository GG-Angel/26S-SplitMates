SELECT log_id, user_id, details, target_table, target_id, action_type, performed_at
FROM audit_logs
WHERE (%(user_id)s IS NULL OR user_id = %(user_id)s)
  AND (%(action_type)s IS NULL OR action_type = %(action_type)s)
ORDER BY performed_at DESC
LIMIT 500;