SELECT user_id, first_name, last_name, email, created_at, is_admin, is_analyst, account_status
FROM users
ORDER BY created_at DESC;