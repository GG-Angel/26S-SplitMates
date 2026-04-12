SELECT b.bill_id,
       b.title,
       b.total_cost,
       b.due_at,
       b.created_by,
       ba.split_percentage,
       ba.paid_at
FROM bill_assignments ba
JOIN bills b ON ba.bill_id = b.bill_id
WHERE ba.user_id = %(user_id)s;
