SELECT *
FROM bills
WHERE bill_id = %(bill_id)s AND group_id = %(group_id)s;