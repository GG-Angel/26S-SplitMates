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
        SELECT SUM(ba2.split_percentage * b.total_cost)
        FROM bill_assignments ba2
        WHERE ba2.bill_id = b.bill_id AND ba2.paid_at IS NULL
    ), 0), 2) AS amount_due,
    ba.split_percentage,
    ROUND(ba.split_percentage * b.total_cost, 2) AS user_cost
FROM bills b
JOIN users u ON b.created_by = u.user_id
JOIN bill_assignments ba ON b.bill_id = ba.bill_id
WHERE b.group_id = %(group_id)s
  AND ba.user_id = %(user_id)s
  AND (%(unpaid_only)s = FALSE OR ba.paid_at IS NULL)
ORDER BY b.due_at ASC;