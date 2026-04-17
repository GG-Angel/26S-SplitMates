UPDATE user_reports
SET status = COALESCE(%(status)s, status),
    reviewed_by = COALESCE(%(reviewed_by)s, reviewed_by),
    reviewed_at = COALESCE(%(reviewed_at)s, reviewed_at)
WHERE report_id = %(report_id)s;