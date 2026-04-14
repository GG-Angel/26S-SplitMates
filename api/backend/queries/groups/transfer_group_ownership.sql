UPDATE `groups`
SET group_leader = %(user_id)s
WHERE group_id = %(group_id)s;