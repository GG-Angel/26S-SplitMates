SELECT COUNT(*) AS c
FROM bills b
LEFT JOIN `groups` g ON b.group_id = g.group_id
WHERE g.group_id IS NULL;