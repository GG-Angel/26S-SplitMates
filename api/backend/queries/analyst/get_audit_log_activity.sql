SELECT
    DATE(performed_at) AS date,
    COUNT(*) AS actions
FROM audit_logs
GROUP BY DATE(performed_at)
ORDER BY date ASC;
