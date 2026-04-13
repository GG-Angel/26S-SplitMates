SELECT 
    b.bill_id,
    b.group_id,
    b.title,
    b.total_cost,
    ROUND(b.total_cost * ba.split_percentage, 2) AS user_cost,
    b.due_at,
    b.created_by,
    ba.split_percentage,
    ba.paid_at
FROM bill_assignments ba
JOIN bills b ON ba.bill_id = b.bill_id
WHERE ba.user_id = %(user_id)s
    AND (%(group_id)s IS NULL OR b.group_id = %(group_id)s);