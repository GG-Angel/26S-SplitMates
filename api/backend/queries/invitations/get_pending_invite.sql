SELECT invitation_id
FROM invitations
WHERE group_id = %(group_id)s
  AND sent_to = %(user_id)s
  AND was_accepted = FALSE
LIMIT 1;
