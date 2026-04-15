DELETE FROM bills
WHERE created_by = %(user_id)s AND group_id = %(group_id)s;

DELETE FROM chores
WHERE created_by = %(user_id)s AND group_id = %(group_id)s;

DELETE FROM events
WHERE created_by = %(user_id)s AND group_id = %(group_id)s;

DELETE FROM group_members
WHERE user_id = %(user_id)s AND group_id = %(group_id)s;
