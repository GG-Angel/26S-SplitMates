SELECT version_id, version_number, deployed_by, status, release_notes, deployed_at
FROM app_versions
ORDER BY version_number DESC;