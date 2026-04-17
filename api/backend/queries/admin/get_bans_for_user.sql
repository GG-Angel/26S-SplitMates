SELECT ban_id, user_id, issued_by, issued_at, reasons, expires_at
FROM bans
WHERE user_id = %(user_id)s
ORDER BY issued_at DESC;