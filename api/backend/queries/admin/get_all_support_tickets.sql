SELECT ticket_id, submitted_by, status, priority, description,
       assigned_to, title, created_at, resolved_at
FROM support_tickets
ORDER BY created_at DESC;