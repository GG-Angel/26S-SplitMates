SELECT
    ba.*,
    u.first_name
FROM bill_assignments ba
JOIN users u ON u.user_id = ba.user_id
WHERE ba.bill_id = %(bill_id)s;
