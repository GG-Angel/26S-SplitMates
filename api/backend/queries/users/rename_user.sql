UPDATE users
SET first_name = %(first_name)s,
	  last_name = %(last_name)s
WHERE user_id = %(user_id)s;