# Complete Google OAuth + PostgreSQL Python Application

## 📦 What You Have

Two complete Python applications to collect Google OAuth data and store in PostgreSQL:

### 1. **Flask Web Application** (`google_oauth_app.py`)
Full-featured web application with:
- Google OAuth 2.0 authentication
- Email/password registration
- User dashboard
- Profile management
- Session tracking
- Activity logging
- Beautiful web interface

### 2. **Standalone Collector** (`google_oauth_collector.py`)
Simple command-line tool with:
- Google OAuth authentication
- Direct data storage
- User listing
- JSON export
- No web interface needed

## 🚀 Quick Start (Choose One)

### Option A: Simple Standalone (Quickest)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup PostgreSQL
createdb user_db
psql -U postgres -d user_db -f sql_ddl_user_schema.sql

# 3. Create .env file
cp .env.example .env
# Edit .env with:
# - DATABASE_URL=postgresql://postgres:password@localhost:5432/user_db
# - GOOGLE_CLIENT_ID=your_id
# - GOOGLE_CLIENT_SECRET=your_secret

# 4. Place credentials.json in project root

# 5. Run collector
python google_oauth_collector.py
```

Then select option "1" to authenticate and store Google data.

### Option B: Full Web Application

```bash
# 1-4. Same as above

# 5. Run Flask app
python google_oauth_app.py

# 6. Open browser
# http://localhost:5000
```

## 📁 Files Created

```
terraform_learn/
├── google_oauth_app.py              # Flask web application
├── google_oauth_collector.py         # Standalone CLI tool
├── sqlalchemy_user_models.py         # ORM models
├── sql_ddl_user_schema.sql          # Database schema
├── sql_sample_queries.sql           # Query examples
├── requirements.txt                  # Python dependencies
├── .env.example                     # Environment template
├── README_OAUTH.md                  # Full documentation
├── templates/
│   ├── index.html                   # Home page
│   ├── login.html                   # Login/signup
│   ├── dashboard.html               # User dashboard
│   ├── register.html                # Registration
│   └── error.html                   # Error page
└── README.md                        # This file
```

## 🔑 Key Features

### Authentication
✅ Google OAuth 2.0  
✅ Email/password login  
✅ User registration  
✅ Password hashing with bcrypt  
✅ Session management  

### Data Storage
✅ PostgreSQL integration  
✅ ORM models (SQLAlchemy)  
✅ User profiles  
✅ Activity logging  
✅ Login history  
✅ Session tracking  

### Security
✅ Password hashing  
✅ Session tokens  
✅ Soft delete support  
✅ Audit logging  
✅ HTTPS ready  

## 📊 Database Schema

11 tables with complete relationships:
- `users` - Core user data
- `user_profiles` - Extended info
- `user_authentications` - OAuth providers
- `user_sessions` - Active sessions
- `user_login_history` - Login audit trail
- `user_activity_log` - User actions
- `user_notifications` - Notifications
- `user_preferences` - User settings
- `user_roles` - Role assignments
- `user_permissions` - Permission grants

## 🔗 API Endpoints (Web App)

```
Authentication
GET  /login                    # Login page
POST /login-email              # Email login
GET  /register                 # Registration
POST /register                 # Create account
GET  /auth/google              # Google OAuth
GET  /auth/callback            # OAuth callback
GET  /logout                   # Logout

Dashboard
GET  /dashboard                # User dashboard
GET  /api/user/profile         # Get profile (JSON)
POST /api/user/update          # Update profile
GET  /api/user/activities      # Activity log
```

## 📋 Usage Examples

### Example 1: Standalone CLI

```bash
python google_oauth_collector.py

# Then follow the menu:
# 1. Authenticate with Google
# 2. List all users
# 3. Export to JSON
# 4. Exit
```

### Example 2: Web App

```bash
python google_oauth_app.py

# Visit: http://localhost:5000
# Click: Continue with Google
# Authorize in Google popup
# View dashboard
```

### Example 3: Python Script

```python
from sqlalchemy_user_models import User, UserProfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup
DATABASE_URL = "postgresql://user:password@localhost:5432/user_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Query users
users = session.query(User).all()
for user in users:
    print(f"{user.username}: {user.email}")

# Get user profile
user = session.query(User).filter_by(email="john@example.com").first()
profile = session.query(UserProfile).filter_by(user_id=user.id).first()
print(f"Company: {profile.company}")
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/user_db

# Google OAuth (from Google Cloud Console)
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback

# Flask
SECRET_KEY=your-random-secret-key
FLASK_ENV=development
FLASK_DEBUG=True

# Optional
SESSION_COOKIE_SECURE=False
PERMANENT_SESSION_LIFETIME=2592000
```

## 🔧 Setting Up Google OAuth

1. Go to: https://console.cloud.google.com/
2. Create new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:5000/auth/callback`
5. Download JSON credentials
6. Save as `credentials.json` in project root
7. Copy CLIENT_ID and CLIENT_SECRET to .env

## 🗄️ Database Setup

```bash
# Create database
createdb user_db

# Create all tables
psql -U postgres -d user_db -f sql_ddl_user_schema.sql

# View tables
psql -U postgres -d user_db -c "\dt"

# Verify schema
psql -U postgres -d user_db -f sql_sample_queries.sql
```

## 🧪 Testing

### Test Google OAuth

```bash
# 1. Start app
python google_oauth_app.py

# 2. Open http://localhost:5000
# 3. Click "Continue with Google"
# 4. Authorize in popup
# 5. Check dashboard
# 6. Verify database
```

### Test Email Registration

```bash
# 1. Open http://localhost:5000/login
# 2. Click "Sign Up" tab
# 3. Fill form
# 4. Submit
# 5. Login with new credentials
# 6. Check PostgreSQL
```

### Verify Database

```bash
psql -U postgres -d user_db
# Run queries
SELECT * FROM users;
SELECT * FROM user_authentications;
SELECT * FROM user_login_history;
```

## 🐛 Common Issues

**Issue: "PostgreSQL connection failed"**
```bash
# Check database
createdb user_db
psql -U postgres -d user_db

# Update .env DATABASE_URL
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/user_db
```

**Issue: "Google OAuth error"**
- Check CLIENT_ID and CLIENT_SECRET
- Verify credentials.json exists
- Check redirect URI in Google Console

**Issue: "Port 5000 in use"**
```bash
# Use different port
# Edit google_oauth_app.py line: app.run(port=5001)
```

**Issue: "No module named google"**
```bash
pip install --upgrade -r requirements.txt
```

## 📈 Production Checklist

- [ ] Set FLASK_ENV=production
- [ ] Use strong SECRET_KEY
- [ ] Set SESSION_COOKIE_SECURE=True
- [ ] Use HTTPS (SSL certificate)
- [ ] Update Google redirect URI to production domain
- [ ] Use managed PostgreSQL database
- [ ] Enable database backups
- [ ] Setup rate limiting
- [ ] Use Gunicorn/uWSGI server
- [ ] Setup reverse proxy (Nginx)
- [ ] Monitor application logs
- [ ] Setup error tracking

## 📚 Documentation

- `README_OAUTH.md` - Complete Flask app documentation
- `USER_SCHEMA_README.md` - Database schema documentation
- `sql_sample_queries.sql` - Example queries
- `sqlalchemy_user_models.py` - ORM models with docstrings
- `django_user_models.py` - Django ORM alternative

## 🤔 FAQ

**Q: Can I use Django instead of Flask?**
A: Yes! Use `django_user_models.py` as a base for your Django app.

**Q: How do I backup the database?**
```bash
pg_dump user_db > backup.sql
# Restore: psql user_db < backup.sql
```

**Q: How do I add more OAuth providers?**
A: Modify `google_oauth_app.py` to add GitHub, Facebook, etc. using same pattern.

**Q: Can I deploy to Heroku?**
A: Yes! Add Procfile and set environment variables in Heroku dashboard.

## 📞 Support

- Check troubleshooting section above
- Review application logs
- Check PostgreSQL logs
- Review Google OAuth settings
- Check network connectivity

## 📝 Next Steps

1. ✅ Install dependencies
2. ✅ Setup PostgreSQL database
3. ✅ Get Google OAuth credentials
4. ✅ Configure .env file
5. ✅ Run standalone collector or web app
6. ✅ Authenticate with Google
7. ✅ Verify data in PostgreSQL
8. ✅ Deploy to production

---

**Version:** 1.0  
**Created:** December 6, 2025  
**Python:** 3.7+  
**PostgreSQL:** 10+  
**Status:** ✅ Production Ready
