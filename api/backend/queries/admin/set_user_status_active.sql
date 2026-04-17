UPDATE users
SET account_status = 'active'
WHERE user_id = %(user_id)s;