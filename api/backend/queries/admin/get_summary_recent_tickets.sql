SELECT
    st.ticket_id,
    st.title,
    st.status,
    st.priority,
    st.created_at,
    u.first_name,
    u.last_name
FROM support_tickets st
JOIN users u ON st.submitted_by = u.user_id
ORDER BY st.created_at DESC
LIMIT 5;