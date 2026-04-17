UPDATE users
SET account_status = 'suspended'
WHERE user_id = %(user_id)s;