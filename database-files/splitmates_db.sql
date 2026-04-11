DROP DATABASE IF EXISTS splitmates_db;
CREATE DATABASE IF NOT EXISTS splitmates_db;

USE splitmates_db;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    picture_url VARCHAR(255),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(75) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_analyst BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_users_email (email)
);

CREATE TABLE `groups` (
    group_id INT AUTO_INCREMENT PRIMARY KEY,
    group_leader INT NOT NULL,
    `name` VARCHAR(50) NOT NULL DEFAULT 'My Group',
    `address` VARCHAR (200) NOT NULL,
    city VARCHAR(50) NOT NULL,
    `state` CHAR(2) NOT NULL,
    zip_code INT NOT NULL,
    FOREIGN KEY (group_leader) REFERENCES users(user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE group_members (
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES `groups` (group_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    total_cost DECIMAL(11, 2) NOT NULL, -- example: 1273.76 for $1273.76
    due_at DATETIME NOT NULL,
    title VARCHAR(128) NOT NULL,
    created_by INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES `groups` (group_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    INDEX idx_created_by (created_by)
);

CREATE TABLE bill_assignments (
    bill_id INT NOT NULL,
    user_id INT NOT NULL,
    split_percentage DECIMAL(4, 3) NOT NULL, -- example: 0.125 for 12.5%
    paid_at DATETIME,
    PRIMARY KEY (bill_id, user_id),
    FOREIGN KEY (bill_id) REFERENCES bills (bill_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE chores (
    chore_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    created_by INT NOT NULL,
    title VARCHAR(128) NOT NULL,
    effort ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    due_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES `groups` (group_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE chore_assignments (
    chore_id INT NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (chore_id, user_id),
    FOREIGN KEY (chore_id) REFERENCES chores (chore_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- TODO: add sysadmin and data-analyst related tables
-- TODO: add invitations
-- TODO: add events