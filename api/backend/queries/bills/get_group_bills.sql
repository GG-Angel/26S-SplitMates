SELECT 
    b.bill_id,
    b.group_id,
    b.total_cost,
    b.due_at,
    b.title,
    b.created_by,
    b.created_at,
    COALESCE((
        SELECT SUM(ba.split_percentage * b.total_cost)
        FROM bill_assignments ba
        WHERE ba.bill_id = b.bill_id AND ba.paid_at IS NULL
    ), 0) AS amount_remaining
FROM bills b
WHERE b.group_id = %(group_id)s;