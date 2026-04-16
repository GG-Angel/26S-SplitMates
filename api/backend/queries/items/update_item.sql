UPDATE items
SET name        = %(name)s,
    picture_url = %(picture_url)s
WHERE item_id = %(item_id)s;
