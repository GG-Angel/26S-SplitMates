INSERT INTO bans (user_id, issued_by, reasons, expires_at)
VALUES (%(user_id)s, %(issued_by)s, %(reasons)s, %(expires_at)s);