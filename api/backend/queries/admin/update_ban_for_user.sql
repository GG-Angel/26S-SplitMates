UPDATE bans
SET reasons = COALESCE(%(reasons)s, reasons),
    expires_at = COALESCE(%(expires_at)s, expires_at)
WHERE user_id = %(user_id)s
  AND ban_id = %(ban_id)s;