SELECT
    ba.*,
    u.first_name
FROM bill_assignments ba
JOIN users u ON u.user_id = ba.user_id
JOIN bills b ON b.bill_id = ba.bill_id
WHERE b.group_id = %(group_id)s;
