SELECT
    i.invitation_id,
    i.group_id,
    g.name AS group_name,
    i.sent_to,
    i.was_accepted,
    i.created_at
FROM invitations i
JOIN `groups` g ON i.group_id = g.group_id
WHERE i.sent_to = %(user_id)s
  AND (%(pending_only)s = FALSE OR i.was_accepted = FALSE)
ORDER BY i.created_at DESC;
