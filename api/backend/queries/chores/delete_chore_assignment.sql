DELETE FROM chore_assignments
WHERE chore_id = %(chore_id)s AND user_id = %(user_id)s;
