UPDATE invitations
SET was_accepted = TRUE
WHERE invitation_id = %(invitation_id)s;
