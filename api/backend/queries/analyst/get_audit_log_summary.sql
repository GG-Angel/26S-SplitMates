SELECT action_type, target_table, COUNT(*) AS total_uses
FROM audit_logs
GROUP BY action_type, target_table
ORDER BY total_uses DESC;
