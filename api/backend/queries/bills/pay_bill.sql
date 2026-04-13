UPDATE bill_assignments
SET paid_at = CURRENT_TIMESTAMP
WHERE bill_id = %(bill_id)s AND user_id = %(user_id)s;