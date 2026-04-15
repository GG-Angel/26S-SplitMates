UPDATE chores
SET title = %(title)s,
    effort = %(effort)s,
    due_at = %(due_at)s
WHERE chore_id = %(chore_id)s;
