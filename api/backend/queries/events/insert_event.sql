INSERT INTO events (group_id, created_by, title, starts_at, ends_at, is_private)
VALUES (%(group_id)s, %(created_by)s, %(title)s, %(starts_at)s, %(ends_at)s, %(is_private)s);
