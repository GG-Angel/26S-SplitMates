SELECT g.group_id, g.name
FROM `groups` g
JOIN group_members gm 
    ON gm.group_id = g.group_id 
    AND gm.user_id = %(user_id)s;