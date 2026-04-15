SELECT report_id, reported_user, reported_by, reason, status,
       reviewed_by, reviewed_at, created_at
FROM user_reports
WHERE report_id = %(report_id)s;