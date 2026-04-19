SELECT COUNT(*) AS open_tickets
FROM support_tickets
WHERE status = 'open';