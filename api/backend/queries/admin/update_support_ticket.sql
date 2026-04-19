UPDATE support_tickets
SET status = COALESCE(%(status)s, status),
    priority = COALESCE(%(priority)s, priority),
    description = COALESCE(%(description)s, description),
    assigned_to = COALESCE(%(assigned_to)s, assigned_to),
    title = COALESCE(%(title)s, title),
    resolved_at = COALESCE(%(resolved_at)s, resolved_at)
WHERE ticket_id = %(ticket_id)s;