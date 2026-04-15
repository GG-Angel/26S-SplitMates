SELECT u.user_id,
       u.first_name,
       u.last_name,
       u.picture_url
FROM item_owners io
         JOIN users u ON io.user_id = u.user_id
WHERE io.item_id = %(item_id)s;
