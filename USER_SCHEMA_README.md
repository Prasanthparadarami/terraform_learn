# PostgreSQL User Information Schema & ORM Models

Complete SQL DDL schema and ORM models for storing user information in PostgreSQL database with full support for modern web applications.

## 📋 What's Included

### 1. **SQL DDL Schema** (`sql_ddl_user_schema.sql`)
- 11 normalized database tables
- Enum types for roles, status, gender
- Advanced features: JSONB fields, soft deletes, audit trails
- 20+ indexes for performance
- Triggers for automatic timestamp updates
- Views for common queries

### 2. **SQLAlchemy Models** (`sqlalchemy_user_models.py`)
- Complete ORM models for Python
- Relationships and cascading deletes
- Input validation
- Compatible with Flask, FastAPI, etc.

### 3. **Django Models** (`django_user_models.py`)
- Full Django ORM implementation
- Model managers and methods
- Admin integration ready
- Migration compatible

## 🗄️ Database Tables

| Table | Purpose |
|-------|---------|
| `users` | Core user information |
| `user_profiles` | Extended profile details |
| `user_authentications` | OAuth/SSO provider connections |
| `user_roles` | Role assignments with expiry |
| `user_permissions` | Granular permission management |
| `user_sessions` | Active session tracking |
| `user_login_history` | Login audit trail |
| `user_activity_log` | User action logging |
| `user_notifications` | User notification queue |
| `user_preferences` | User settings/preferences |

## 🚀 Quick Start

### Setup PostgreSQL

```bash
# Create database
createdb user_db

# Connect to database
psql -U postgres -d user_db

# Run SQL schema
psql -U postgres -d user_db -f sql_ddl_user_schema.sql
```

### Python with SQLAlchemy

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_user_models import Base, User, UserProfile

# Create database connection
DATABASE_URL = "postgresql://user:password@localhost:5432/user_db"
engine = create_engine(DATABASE_URL)

# Create all tables
Base.metadata.create_all(engine)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

# Create a new user
new_user = User(
    username="john_doe",
    email="john@example.com",
    password_hash="hashed_password_here",
    first_name="John",
    last_name="Doe"
)
session.add(new_user)
session.commit()

# Add user profile
profile = UserProfile(
    user_id=new_user.id,
    company="Tech Corp",
    job_title="Software Engineer",
    country="USA"
)
session.add(profile)
session.commit()

# Query users
users = session.query(User).filter_by(status='active').all()
for user in users:
    print(f"{user.username}: {user.email}")
```

### Django Setup

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'your_app',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'user_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Create tables
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

```python
# Usage in Django views
from django_user_models import User, UserProfile

# Create user
user = User.objects.create(
    username='john_doe',
    email='john@example.com',
    password_hash='hashed_password',
    first_name='John'
)

# Add profile
profile = UserProfile.objects.create(
    user=user,
    company='Tech Corp',
    job_title='Engineer'
)

# Query
active_users = User.objects.filter(status='active')
```

## 📊 Schema Diagram

```
users (core)
├── user_profiles (1:1) - Extended info
├── user_authentications (1:N) - OAuth providers
├── user_roles (1:N) - Role assignments
├── user_permissions (1:N) - Permission grants
├── user_sessions (1:N) - Active sessions
├── user_login_history (1:N) - Login audit
├── user_activity_log (1:N) - Action log
├── user_notifications (1:N) - Notifications
└── user_preferences (1:1) - Settings
```

## 🔑 Key Features

### 1. **Multi-Auth Support**
- Native login with password hash
- OAuth/SSO integration (Google, GitHub, etc.)
- Session-based tracking
- Multi-factor authentication ready

### 2. **Audit & Compliance**
- Soft delete support (deleted_at field)
- Complete login history
- Activity logging
- Timestamp tracking (created_at, updated_at)

### 3. **Performance**
- Strategic indexing on frequently queried fields
- JSONB support for flexible metadata
- Optimized views for common queries

### 4. **Security**
- Email format validation
- IP address tracking
- Failed login attempts tracking
- Session token management

### 5. **Flexibility**
- User metadata (JSONB)
- Custom preferences (JSONB)
- Activity tracking
- Notification queue

## 💾 Data Types

### Enums
```sql
user_role: admin, user, moderator, guest
account_status: active, inactive, suspended, deleted
gender: male, female, other, prefer_not_to_say
```

### JSONB Fields
- `metadata` - Custom user data
- `notification_preferences` - Notification settings
- `privacy_settings` - Privacy controls
- `social_links` - Social media profiles
- `changes` - Audit trail of changes
- `additional_data` - Provider-specific data

## 📝 Common Queries

### Get Active Users
```sql
SELECT * FROM active_users LIMIT 10;
```

### User Summary with Stats
```sql
SELECT * FROM user_summaries WHERE id = 1;
```

### Recent Login History
```sql
SELECT user_id, ip_address, login_successful, created_at
FROM user_login_history
WHERE user_id = 1
ORDER BY created_at DESC
LIMIT 20;
```

### User Activity Log
```sql
SELECT action, resource_type, created_at
FROM user_activity_log
WHERE user_id = 1
ORDER BY created_at DESC;
```

### Active Sessions
```sql
SELECT * FROM user_sessions
WHERE user_id = 1 AND is_active = TRUE;
```

## 🔧 Maintenance

### Backup Database
```bash
pg_dump user_db > user_db_backup.sql
```

### Restore Database
```bash
psql user_db < user_db_backup.sql
```

### Update Timestamps
Triggers automatically update `updated_at` on any row modification.

### Soft Delete a User
```python
# SQLAlchemy
user.soft_delete()  # Sets deleted_at and status='deleted'

# Django
user.soft_delete()
```

## 🛡️ Security Best Practices

1. **Never store plain passwords** - Always hash with bcrypt/argon2
2. **Use HTTPS** - For all API endpoints
3. **Secure session tokens** - Use cryptographic random generation
4. **IP whitelisting** - Consider for sensitive operations
5. **Rate limiting** - Prevent brute force on login
6. **Audit logging** - Monitor all user_activity_log entries
7. **GDPR compliance** - Implement data export with deleted_at soft deletes

## 🎯 Migration Guide

### From Existing Database

1. **Backup current data**
2. **Run DDL schema**
3. **Map existing data to new schema**
4. **Test thoroughly**
5. **Cutover during maintenance window**

### Example Migration Script
```python
# Migrate from old user table to new schema
def migrate_users():
    old_users = OldUser.objects.all()
    for old_user in old_users:
        new_user = User.objects.create(
            username=old_user.username,
            email=old_user.email,
            password_hash=old_user.password,
            first_name=old_user.first_name,
            last_name=old_user.last_name,
        )
        UserProfile.objects.create(user=new_user)
```

## 📈 Scaling Considerations

### For Large Datasets
- Archive old `user_login_history` and `user_activity_log` records
- Partition tables by date if >1B rows
- Use read replicas for reporting queries

### Performance Tuning
- Analyze table statistics: `ANALYZE users;`
- Vacuum regularly: `VACUUM ANALYZE;`
- Monitor slow queries with `pg_stat_statements`

## 🐛 Troubleshooting

### Foreign Key Errors
Ensure cascade deletes are properly configured when removing parent records.

### JSONB Query Issues
Use proper JSONB operators:
```sql
WHERE metadata->>'key' = 'value'
```

### Session Conflicts
Check unique constraint on `session_token` and `user_id/auth_provider`.

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Django ORM Documentation](https://docs.djangoproject.com/en/stable/topics/db/)
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

**Version:** 1.0  
**Last Updated:** December 6, 2025  
**PostgreSQL Version:** 10+  
**Python Support:** 3.7+
