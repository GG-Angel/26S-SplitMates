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
    account_status ENUM('active', 'inactive', 'suspended', 'pending') NOT NULL DEFAULT 'pending',
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
