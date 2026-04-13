SELECT 
    b.bill_id,
    b.group_id,
    b.total_cost,
    b.due_at,
    b.title,
    b.created_by,
    u.first_name AS creator_name,
    b.created_at,
    ROUND(COALESCE((
        SELECT SUM(ba.split_percentage * b.total_cost)
        FROM bill_assignments ba
        WHERE ba.bill_id = b.bill_id AND ba.paid_at IS NULL
    ), 0), 2) AS amount_due
FROM bills b
JOIN users u ON b.created_by = u.user_id
WHERE b.group_id = %(group_id)s
ORDER BY b.due_at ASC;;