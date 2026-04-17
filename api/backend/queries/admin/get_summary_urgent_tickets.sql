SELECT COUNT(*) AS urgent_tickets
FROM support_tickets
WHERE priority = 'high' AND status <> 'closed';