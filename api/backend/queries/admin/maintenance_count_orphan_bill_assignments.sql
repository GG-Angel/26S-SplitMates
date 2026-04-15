SELECT COUNT(*) AS c
FROM bill_assignments ba
LEFT JOIN bills b ON ba.bill_id = b.bill_id
WHERE b.bill_id IS NULL;