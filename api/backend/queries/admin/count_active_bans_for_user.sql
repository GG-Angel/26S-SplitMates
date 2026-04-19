SELECT COUNT(*) AS active_bans
FROM bans
WHERE user_id = %(user_id)s
  AND (expires_at IS NULL OR expires_at > NOW());