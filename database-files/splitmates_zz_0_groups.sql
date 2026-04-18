USE `splitmates_db`;
INSERT INTO `groups` (group_leader, `name`, `address`, city, `state`, zip_code) VALUES
(1, 'The Hill Boys', '123 Tremont St', 'Boston', 'MA', 02120),
(2, 'Symphonies', '456 Symphony St', 'Boston', 'MA', 02120),
(3, 'Casa Chaos', '789 Huntington Ave', 'Boston', 'MA', 02115);

INSERT INTO group_members (user_id, group_id) VALUES
(1, 1), (5, 1), (10, 1),
(2, 2), (6, 2), (11, 2),
(3, 3), (7, 3), (12, 3);
