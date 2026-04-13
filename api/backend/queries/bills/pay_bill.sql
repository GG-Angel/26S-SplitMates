UPDATE bills
SET paid_at = CURRENT_TIMESTAMP
WHERE bill_id = %(bill_id)s;