DROP DATABASE IF EXISTS `splitmates_db`;

CREATE DATABASE `splitmates_db`;

USE `splitmates_db`;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    is_analyst BOOLEAN NOT NULL DEFAULT FALSE,
    account_status ENUM('active', 'inactive', 'suspended', 'pending') NOT NULL DEFAULT 'active',
    password_hash VARCHAR(128) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    picture_url VARCHAR(255),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(75) NOT NULL UNIQUE,
    INDEX idx_users_email (email)
);

CREATE TABLE `groups` (
    group_id INT AUTO_INCREMENT PRIMARY KEY,
    group_leader INT NOT NULL,
    `name` VARCHAR(50) NOT NULL DEFAULT 'My Group',
    `address` VARCHAR (200),
    city VARCHAR(50),
    `state` VARCHAR(50),
    zip_code INT,
    CONSTRAINT groups_fk01
        FOREIGN KEY (group_leader) REFERENCES users(user_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
);

CREATE TABLE group_members (
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, group_id),
    CONSTRAINT group_members_fk01
        FOREIGN KEY (user_id) REFERENCES users(user_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    CONSTRAINT group_members_fk02
        FOREIGN KEY (group_id) REFERENCES `groups`(group_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
);

CREATE TABLE invitations (
    invitation_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    sent_to INT NOT NULL,
    was_accepted BOOLEAN NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT invitations_fk01
        FOREIGN KEY (group_id) REFERENCES `groups`(group_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    CONSTRAINT invitations_fk02
        FOREIGN KEY (sent_to) REFERENCES users(user_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
);

CREATE TABLE bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    total_cost DECIMAL(11, 2) NOT NULL,
    due_at DATETIME NOT NULL,
    title VARCHAR(128) NOT NULL,
    created_by INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT bills_fk01
        FOREIGN KEY (created_by) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    CONSTRAINT bills_fk02
        FOREIGN KEY (group_id) REFERENCES `groups` (group_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    INDEX idx_created_by (created_by)
);

CREATE TABLE bill_assignments (
    bill_id INT NOT NULL,
    user_id INT NOT NULL,
    split_percentage DECIMAL(4, 3) NOT NULL,
    paid_at DATETIME,
    PRIMARY KEY (bill_id, user_id),
    CONSTRAINT bill_assignments_fk01
        FOREIGN KEY (bill_id) REFERENCES bills (bill_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    CONSTRAINT bill_assignments_fk02
        FOREIGN KEY (user_id) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
);

CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    title VARCHAR(128) NOT NULL,
    starts_at DATETIME NOT NULL,
    ends_at DATETIME NOT NULL,
    is_private BOOLEAN NOT NULL,
    created_by INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT events_fk01
        FOREIGN KEY (group_id) REFERENCES `groups` (group_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    CONSTRAINT events_fk02
        FOREIGN KEY (created_by) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    INDEX idx_events_created_by (created_by)
);

CREATE TABLE items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    name VARCHAR(128) NOT NULL,
    picture_url VARCHAR(255),
    created_by INT NOT NULL,
    CONSTRAINT item_fk01
       FOREIGN KEY (created_by) REFERENCES users (user_id)
           ON UPDATE CASCADE
           ON DELETE CASCADE,
    CONSTRAINT item_fk02
        FOREIGN KEY (group_id) REFERENCES `groups` (group_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    INDEX idx_items_created_by (created_by)
);

CREATE TABLE item_owners (
    item_id INT NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (item_id, user_id),
    CONSTRAINT item_owners_fk01
        FOREIGN KEY (item_id) REFERENCES items (item_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    CONSTRAINT item_owners_fk02
        FOREIGN KEY (user_id) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chores (
    chore_id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    created_by INT NOT NULL,
    title VARCHAR(128) NOT NULL,
    effort ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    due_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chores_fk01
        FOREIGN KEY (created_by) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    CONSTRAINT chores_fk02
        FOREIGN KEY (group_id) REFERENCES `groups` (group_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    INDEX idx_chores_created_by (created_by)
);

CREATE TABLE IF NOT EXISTS chore_assignments (
    chore_id INT NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (chore_id, user_id),
    CONSTRAINT choreAssignments_fk01
        FOREIGN KEY (chore_id) REFERENCES chores (chore_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    CONSTRAINT choreAssignments_fk02
        FOREIGN KEY (user_id) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
);

CREATE TABLE bans (
    ban_id INT AUTO_INCREMENT NOT NULL,
    user_id INT NOT NULL,
    issued_by INT NOT NULL,
    issued_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reasons VARCHAR(255),
    expires_at DATETIME,
    PRIMARY KEY (ban_id),
    CONSTRAINT fk_ban_user_id
        FOREIGN KEY (user_id) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    CONSTRAINT fk_ban_user_admin
        FOREIGN KEY (issued_by) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
);

CREATE TABLE support_tickets (
    ticket_id INT AUTO_INCREMENT,
    submitted_by INT NOT NULL,
    status ENUM('open', 'in_progress', 'closed') NOT NULL DEFAULT 'open',
    priority ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'low',
    description VARCHAR(255),
    assigned_to INT NOT NULL,
    title VARCHAR(100),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    PRIMARY KEY(ticket_id),
    CONSTRAINT fk_support_ticket_submit_by
        FOREIGN KEY (submitted_by) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,
    CONSTRAINT fk_support_ticket_assigned_to
        FOREIGN KEY (assigned_to) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
);

CREATE TABLE app_versions (
    version_id INT AUTO_INCREMENT,
    version_number INT NOT NULL UNIQUE,
    deployed_by INT NOT NULL,
    status ENUM('staged', 'deployed', 'rolled_back', 'deprecated') NOT NULL DEFAULT 'deployed',
    release_notes VARCHAR(1024),
    deployed_at DATETIME,
    PRIMARY KEY (version_id),
    CONSTRAINT fk_appversion_admin
        FOREIGN KEY (deployed_by) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,
    INDEX idx_ver_num (version_number)
);

CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT NOT NULL,
    user_id INT NOT NULL,
    details VARCHAR(255) NOT NULL,
    target_table VARCHAR(50) NOT NULL,
    target_id INT NOT NULL,
    action_type ENUM('create', 'update', 'delete') NOT NULL DEFAULT 'create',
    performed_at DATETIME NOT NULL,
    PRIMARY KEY (log_id),
    CONSTRAINT auditLog_fk01
        FOREIGN KEY (user_id) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,
    INDEX idx_audit_user_id (user_id)
);

CREATE TABLE `sessions` (
    session_id INT NOT NULL,
    user_id INT NOT NULL,
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NOT NULL,
    duration INT NOT NULL CHECK (duration > 0),
    PRIMARY KEY (session_id),
    CONSTRAINT session_fk01
        FOREIGN KEY (user_id) REFERENCES users (user_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,
    INDEX idx_session_user_id (user_id)
);

CREATE TABLE user_reports (
    report_id INT AUTO_INCREMENT NOT NULL,
    reported_user INT NOT NULL,
    reported_by INT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    status ENUM('pending', 'resolved',  'under_review', 'dismissed'),
    reviewed_by INT NOT NULL,
    reviewed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (report_id),
    CONSTRAINT fk_reported_user_users
        FOREIGN KEY (reported_user) REFERENCES users(user_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,
    CONSTRAINT fk_reported_by_users
        FOREIGN KEY (reported_by) REFERENCES users(user_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT,
    CONSTRAINT fk_reviewed_by_admin
        FOREIGN KEY (reviewed_by) REFERENCES users(user_id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
);

