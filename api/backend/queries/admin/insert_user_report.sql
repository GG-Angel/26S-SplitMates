INSERT INTO user_reports (reported_user, reported_by, reason, status)
VALUES (%(reported_user)s, %(reported_by)s, %(reason)s, 'pending')
