UPDATE chores
SET completed_at = CURRENT_TIMESTAMP
WHERE chore_id = %(chore_id)s;
