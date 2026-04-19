SELECT COUNT(*) AS inactive_users
FROM users
WHERE account_status <> 'active';