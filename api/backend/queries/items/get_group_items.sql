SELECT i.item_id,
       i.group_id,
       i.name,
       i.picture_url,
       i.created_by,
       u.first_name,
       u.last_name
FROM items i
         JOIN users u ON i.created_by = u.user_id
WHERE i.group_id = %(group_id)s
ORDER BY i.item_id;
