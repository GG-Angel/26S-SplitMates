SELECT report_id, reported_user, reported_by, reason, status,
       reviewed_by, reviewed_at, created_at
FROM user_reports
WHERE reported_user = %(reported_user)s
ORDER BY created_at DESC;