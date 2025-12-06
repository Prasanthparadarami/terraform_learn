-- User Schema - Sample Data & Test Queries
-- This file contains examples of inserting and querying data

-- ============================================
-- SAMPLE INSERT STATEMENTS
-- ============================================

-- Insert sample users
INSERT INTO users (username, email, password_hash, first_name, last_name, role, status)
VALUES 
    ('admin_user', 'admin@example.com', '$2b$12$abcdefghijklmnopqrstuvwxyz', 'Admin', 'User', 'admin', 'active'),
    ('john_doe', 'john@example.com', '$2b$12$abcdefghijklmnopqrstuvwxyz', 'John', 'Doe', 'user', 'active'),
    ('jane_smith', 'jane@example.com', '$2b$12$abcdefghijklmnopqrstuvwxyz', 'Jane', 'Smith', 'user', 'active'),
    ('bob_moderator', 'bob@example.com', '$2b$12$abcdefghijklmnopqrstuvwxyz', 'Bob', 'Moderator', 'moderator', 'active')
ON CONFLICT (email) DO NOTHING;

-- Insert user profiles
INSERT INTO user_profiles (user_id, company, job_title, country, city, timezone, language_preference)
SELECT u.id, 'Tech Corp', 'Software Engineer', 'USA', 'San Francisco', 'America/Los_Angeles', 'en'
FROM users u WHERE u.username = 'john_doe'
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_profiles (user_id, company, job_title, country, city, timezone, language_preference)
SELECT u.id, 'Design Inc', 'UX Designer', 'USA', 'New York', 'America/New_York', 'en'
FROM users u WHERE u.username = 'jane_smith'
ON CONFLICT (user_id) DO NOTHING;

-- Insert authentication providers
INSERT INTO user_authentications (user_id, auth_provider, provider_user_id, provider_username, is_primary)
SELECT u.id, 'google', 'google_12345', 'john.doe', false
FROM users u WHERE u.username = 'john_doe'
ON CONFLICT (user_id, auth_provider) DO NOTHING;

-- Insert user roles
INSERT INTO user_roles (user_id, role_name, reason)
SELECT u.id, 'content_creator', 'Approved for content creation'
FROM users u WHERE u.username = 'jane_smith'
ON CONFLICT (user_id, role_name) DO NOTHING;

-- Insert user permissions
INSERT INTO user_permissions (user_id, permission_name, resource, action)
SELECT u.id, 'manage_users', 'users', 'write'
FROM users u WHERE u.username = 'admin_user'
ON CONFLICT (user_id, permission_name, resource) DO NOTHING;

-- Insert user preferences
INSERT INTO user_preferences (user_id, theme, language, email_notifications, push_notifications)
SELECT u.id, 'dark', 'en', true, true
FROM users u WHERE u.username = 'john_doe'
ON CONFLICT (user_id) DO NOTHING;

-- ============================================
-- SAMPLE QUERY EXAMPLES
-- ============================================

-- 1. Get all active users with their profiles
SELECT 
    u.id,
    u.username,
    u.email,
    u.first_name,
    u.last_name,
    up.company,
    up.job_title,
    u.created_at
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
WHERE u.status = 'active' AND u.deleted_at IS NULL
ORDER BY u.created_at DESC;

-- 2. Count users by role
SELECT role, COUNT(*) as user_count
FROM users
WHERE deleted_at IS NULL
GROUP BY role
ORDER BY user_count DESC;

-- 3. Get user by username with all details
SELECT 
    u.*,
    up.company,
    up.job_title,
    COUNT(DISTINCT ua.id) as oauth_count,
    MAX(ulh.created_at) as last_login
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
LEFT JOIN user_authentications ua ON u.id = ua.user_id
LEFT JOIN user_login_history ulh ON u.id = ulh.user_id
WHERE u.username = 'john_doe'
GROUP BY u.id, up.id;

-- 4. Get user's recent login history
SELECT 
    user_id,
    login_method,
    ip_address,
    browser_name,
    os_name,
    login_successful,
    failure_reason,
    created_at
FROM user_login_history
WHERE user_id = (SELECT id FROM users WHERE username = 'john_doe')
ORDER BY created_at DESC
LIMIT 10;

-- 5. Get user's active sessions
SELECT 
    id,
    session_token,
    ip_address,
    device_name,
    browser_name,
    created_at,
    last_activity,
    expires_at
FROM user_sessions
WHERE user_id = (SELECT id FROM users WHERE username = 'john_doe')
  AND is_active = TRUE
  AND (expires_at IS NULL OR expires_at > NOW());

-- 6. Get unread notifications for user
SELECT 
    id,
    notification_type,
    title,
    message,
    created_at
FROM user_notifications
WHERE user_id = (SELECT id FROM users WHERE username = 'john_doe')
  AND is_read = FALSE
ORDER BY created_at DESC;

-- 7. Get user activity log
SELECT 
    action,
    resource_type,
    resource_id,
    changes,
    created_at
FROM user_activity_log
WHERE user_id = (SELECT id FROM users WHERE username = 'john_doe')
ORDER BY created_at DESC
LIMIT 20;

-- 8. Get users who haven't logged in for 30 days
SELECT 
    id,
    username,
    email,
    last_login,
    NOW() - last_login as days_inactive
FROM users
WHERE status = 'active'
  AND deleted_at IS NULL
  AND last_login < NOW() - INTERVAL '30 days'
ORDER BY last_login ASC;

-- 9. Get failed login attempts
SELECT 
    u.username,
    u.email,
    COUNT(*) as failed_attempts,
    MAX(ulh.created_at) as last_failed,
    array_agg(DISTINCT ulh.ip_address) as ip_addresses
FROM user_login_history ulh
JOIN users u ON ulh.user_id = u.id
WHERE ulh.login_successful = FALSE
  AND ulh.created_at > NOW() - INTERVAL '24 hours'
GROUP BY u.id, u.username, u.email
HAVING COUNT(*) >= 3
ORDER BY failed_attempts DESC;

-- 10. Get user's OAuth connections
SELECT 
    auth_provider,
    provider_username,
    provider_email,
    is_primary,
    created_at
FROM user_authentications
WHERE user_id = (SELECT id FROM users WHERE username = 'john_doe')
ORDER BY is_primary DESC, created_at DESC;

-- 11. Get users with specific permissions
SELECT DISTINCT
    u.id,
    u.username,
    u.email,
    up.permission_name,
    up.resource,
    up.action
FROM users u
JOIN user_permissions up ON u.id = up.user_id
WHERE up.permission_name LIKE '%manage%'
  AND (up.expires_at IS NULL OR up.expires_at > NOW());

-- 12. Update last login
UPDATE users 
SET last_login = NOW(), login_count = login_count + 1
WHERE username = 'john_doe';

-- 13. Mark notifications as read
UPDATE user_notifications
SET is_read = TRUE, read_at = NOW()
WHERE user_id = (SELECT id FROM users WHERE username = 'john_doe')
  AND is_read = FALSE;

-- 14. Log user activity
INSERT INTO user_activity_log (user_id, action, resource_type, resource_id, status, created_at)
VALUES (
    (SELECT id FROM users WHERE username = 'john_doe'),
    'updated_profile',
    'user_profile',
    '1',
    'success',
    NOW()
);

-- 15. Soft delete a user
UPDATE users 
SET deleted_at = NOW(), status = 'deleted'
WHERE username = 'john_doe';

-- 16. Get user metrics/stats
SELECT 
    u.username,
    u.email,
    COUNT(DISTINCT us.id) as active_sessions,
    COUNT(DISTINCT ulh.id) as total_logins,
    SUM(CASE WHEN ulh.login_successful THEN 1 ELSE 0 END) as successful_logins,
    SUM(CASE WHEN NOT ulh.login_successful THEN 1 ELSE 0 END) as failed_logins,
    MAX(ulh.created_at) as last_login_time
FROM users u
LEFT JOIN user_sessions us ON u.id = us.user_id AND us.is_active = TRUE
LEFT JOIN user_login_history ulh ON u.id = ulh.user_id
WHERE u.id = (SELECT id FROM users WHERE username = 'john_doe')
GROUP BY u.id, u.username, u.email;

-- 17. Get all admin and moderator users
SELECT 
    id,
    username,
    email,
    role,
    status,
    created_at
FROM users
WHERE role IN ('admin', 'moderator')
  AND status = 'active'
  AND deleted_at IS NULL
ORDER BY created_at DESC;

-- 18. Find duplicate emails (data quality check)
SELECT 
    email,
    COUNT(*) as count,
    array_agg(id) as user_ids
FROM users
WHERE deleted_at IS NULL
GROUP BY email
HAVING COUNT(*) > 1;

-- 19. Get user's preferences
SELECT 
    theme,
    language,
    notifications_enabled,
    email_notifications,
    sms_notifications,
    push_notifications,
    marketing_emails,
    additional_preferences
FROM user_preferences
WHERE user_id = (SELECT id FROM users WHERE username = 'john_doe');

-- 20. Get detailed user summary (views example)
SELECT *
FROM user_summaries
WHERE id = (SELECT id FROM users WHERE username = 'john_doe');

-- ============================================
-- ANALYTICS QUERIES
-- ============================================

-- Total users breakdown
SELECT 
    status,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM users WHERE deleted_at IS NULL), 2) as percentage
FROM users
WHERE deleted_at IS NULL
GROUP BY status;

-- New users this month
SELECT 
    DATE_TRUNC('day', created_at)::DATE as signup_date,
    COUNT(*) as new_users
FROM users
WHERE created_at >= DATE_TRUNC('month', NOW())
  AND deleted_at IS NULL
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY signup_date DESC;

-- Most active users (by activity count)
SELECT 
    u.username,
    u.email,
    COUNT(ual.id) as activity_count
FROM users u
LEFT JOIN user_activity_log ual ON u.id = ual.user_id
WHERE u.deleted_at IS NULL
GROUP BY u.id, u.username, u.email
ORDER BY activity_count DESC
LIMIT 10;

-- Users by country
SELECT 
    up.country,
    COUNT(DISTINCT u.id) as user_count
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
WHERE u.status = 'active' AND u.deleted_at IS NULL
GROUP BY up.country
ORDER BY user_count DESC;

-- ============================================
-- MAINTENANCE QUERIES
-- ============================================

-- Remove expired sessions
DELETE FROM user_sessions
WHERE expires_at < NOW();

-- Remove expired permissions
DELETE FROM user_permissions
WHERE expires_at < NOW();

-- Remove expired roles
DELETE FROM user_roles
WHERE expires_at < NOW();

-- Archive old login history (keep last 1 year)
DELETE FROM user_login_history
WHERE created_at < NOW() - INTERVAL '1 year';

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE tablename LIKE 'user%'
ORDER BY idx_scan DESC;
