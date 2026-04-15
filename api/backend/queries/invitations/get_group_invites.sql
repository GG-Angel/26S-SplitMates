SELECT
    i.invitation_id,
    i.group_id,
    i.sent_to,
    u.first_name,
    u.last_name,
    u.email,
    i.was_accepted,
    i.created_at
FROM invitations i
JOIN users u ON i.sent_to = u.user_id
WHERE i.group_id = %(group_id)s
  AND (%(pending_only)s = FALSE OR i.was_accepted = FALSE)
ORDER BY i.created_at DESC;
