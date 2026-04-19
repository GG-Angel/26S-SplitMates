UPDATE invitations
SET was_accepted = TRUE
WHERE invitation_id = %(invitation_id)s;

INSERT INTO group_members (user_id, group_id)
SELECT %(user_id)s, group_id
FROM invitations
WHERE invitation_id = %(invitation_id)s;
