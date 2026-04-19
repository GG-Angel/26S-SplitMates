DELETE FROM bans
WHERE user_id = %(user_id)s
  AND ban_id = %(ban_id)s;