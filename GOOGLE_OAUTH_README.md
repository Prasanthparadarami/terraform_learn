# 🎯 Google OAuth + PostgreSQL Python Application - Complete Package

## 📦 What's Included

Complete, production-ready Python application to authenticate users with Google OAuth and store data in PostgreSQL.

### Two Applications Available:

1. **Flask Web Application** - Full-featured web interface
2. **Standalone CLI Tool** - Simple command-line collector

---

## 🚀 Quick Start (30 seconds)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup PostgreSQL
createdb user_db
psql -U postgres -d user_db -f sql_ddl_user_schema.sql

# 3. Configure Google OAuth
# Get credentials from: https://console.cloud.google.com/
# Save as credentials.json in project root

# 4. Create .env file
cp .env.example .env
# Edit with your DATABASE_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

# 5. Run one of:
python google_oauth_app.py          # Web app at http://localhost:5000
python google_oauth_collector.py    # CLI tool
```

---

## 📂 File Structure

### Python Applications
- **`google_oauth_app.py`** - Flask web application with full UI
- **`google_oauth_collector.py`** - Standalone CLI collector tool

### ORM Models
- **`sqlalchemy_user_models.py`** - SQLAlchemy ORM (Python/Flask/FastAPI)
- **`django_user_models.py`** - Django ORM alternative

### Database
- **`sql_ddl_user_schema.sql`** - Complete PostgreSQL schema (11 tables)
- **`sql_sample_queries.sql`** - Example queries and analytics

### Configuration
- **`requirements.txt`** - Python dependencies
- **`.env.example`** - Environment template

### Web Interface (Flask App)
```
templates/
├── index.html       # Home page
├── login.html       # Login/signup with OAuth
├── dashboard.html   # User dashboard
├── register.html    # Registration form
└── error.html       # Error pages
```

### Documentation
- **`SETUP_GUIDE.md`** ⭐ START HERE - Complete setup instructions
- **`README_OAUTH.md`** - Flask app documentation
- **`USER_SCHEMA_README.md`** - Database schema guide
- **`CICD_SETUP.md`** - CI/CD pipeline setup

---

## ✨ Features

### Authentication
✅ Google OAuth 2.0 login  
✅ Email/password registration  
✅ Bcrypt password hashing  
✅ Session management  
✅ Remember me functionality  

### Data Management
✅ 11 normalized database tables  
✅ User profiles  
✅ OAuth provider tracking  
✅ Session history  
✅ Login audit trail  
✅ Activity logging  
✅ User preferences  

### Security
✅ Bcrypt password hashing  
✅ Secure session tokens  
✅ CSRF protection ready  
✅ Soft delete support  
✅ Input validation  
✅ SQL injection prevention (ORM)  

### Performance
✅ 20+ database indexes  
✅ Optimized queries  
✅ Connection pooling  
✅ Cached relationships  

---

## 🔑 Key Files Explained

| File | Purpose |
|------|---------|
| `google_oauth_app.py` | Full Flask web application |
| `google_oauth_collector.py` | Simple CLI tool |
| `sqlalchemy_user_models.py` | SQLAlchemy ORM models |
| `django_user_models.py` | Django ORM models |
| `sql_ddl_user_schema.sql` | Database creation script |
| `requirements.txt` | All Python dependencies |
| `.env.example` | Configuration template |

---

## 📊 Database Schema

**11 Tables:**
- `users` - Core user information
- `user_profiles` - Extended profile details
- `user_authentications` - OAuth connections
- `user_sessions` - Active sessions
- `user_login_history` - Login audit trail
- `user_activity_log` - User actions
- `user_notifications` - Notification queue
- `user_preferences` - User settings
- `user_roles` - Role assignments
- `user_permissions` - Permission grants

---

## 🎓 Usage Examples

### Example 1: Web Application

```bash
python google_oauth_app.py
# Open: http://localhost:5000
# Click: Continue with Google
# Authorize in popup
# Done! View your dashboard
```

### Example 2: CLI Collector

```bash
python google_oauth_collector.py
# Select: 1 - Authenticate
# Follow Google OAuth flow
# Data automatically saved to PostgreSQL
```

### Example 3: Python Script

```python
from sqlalchemy_user_models import User, UserProfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://user:pass@localhost/user_db")
Session = sessionmaker(bind=engine)
session = Session()

# Query users
users = session.query(User).filter_by(status='active').all()
for user in users:
    print(f"{user.username}: {user.email}")
```

---

## 🔗 API Endpoints (Web App)

```
Authentication
GET  /login              Login page
POST /login-email        Email login
POST /register           Create account
GET  /auth/google        Start Google OAuth
GET  /auth/callback      OAuth callback
GET  /logout             Logout

Dashboard
GET  /dashboard          User dashboard
GET  /api/user/profile   Get profile (JSON)
POST /api/user/update    Update profile
GET  /api/user/activities Activity log (JSON)
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/user_db

# Google OAuth (from Google Cloud Console)
GOOGLE_CLIENT_ID=your_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback

# Flask
SECRET_KEY=your-secret-key
FLASK_ENV=development
```

---

## 🔧 Setup Google OAuth

1. Go to: https://console.cloud.google.com/
2. Create new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Type: Web application
   - Authorized redirect URIs: `http://localhost:5000/auth/callback`
5. Download JSON → Save as `credentials.json`
6. Copy CLIENT_ID and SECRET to `.env`

---

## 📋 Database Setup

```bash
# Create database
createdb user_db

# Create all tables
psql -U postgres -d user_db -f sql_ddl_user_schema.sql

# Verify
psql -U postgres -d user_db -c "SELECT * FROM users;"
```

---

## 📚 Documentation

| Document | Content |
|----------|---------|
| **SETUP_GUIDE.md** | 🌟 **START HERE** - Complete setup |
| **README_OAUTH.md** | Flask app detailed docs |
| **USER_SCHEMA_README.md** | Database schema & ORM |
| **CICD_SETUP.md** | GitHub Actions CI/CD |

---

## 🧪 Testing

### Test Google OAuth Login
```bash
python google_oauth_app.py
# Visit: http://localhost:5000
# Click "Continue with Google"
# Follow popup
# Check: Dashboard shows data
```

### Test Email Registration
```bash
# Visit: http://localhost:5000/login
# Click "Sign Up"
# Fill form and submit
# Login with new credentials
```

### Verify in PostgreSQL
```bash
psql -U postgres -d user_db
SELECT * FROM users;
SELECT * FROM user_authentications;
SELECT * FROM user_login_history;
```

---

## 🚨 Troubleshooting

### PostgreSQL Connection Failed
```bash
# Create database
createdb user_db

# Run schema
psql -U postgres -d user_db -f sql_ddl_user_schema.sql

# Check .env DATABASE_URL
```

### Google OAuth Error
- ✓ Verify CLIENT_ID and SECRET in .env
- ✓ Check credentials.json exists
- ✓ Verify redirect URI in Google Console

### Port 5000 In Use
```bash
# Edit google_oauth_app.py
app.run(port=5001)  # Use different port
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

## 📈 Production Deployment

### Checklist
- [ ] Set FLASK_ENV=production
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Update Google redirect URI
- [ ] Use managed PostgreSQL (AWS RDS, etc.)
- [ ] Setup automated backups
- [ ] Use Gunicorn/uWSGI
- [ ] Setup reverse proxy (Nginx)
- [ ] Enable rate limiting
- [ ] Monitor logs and errors

### Example Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 google_oauth_app:app
```

---

## 📞 Support & Resources

- 📖 [Flask Documentation](https://flask.palletsprojects.com/)
- 🔐 [Google OAuth Docs](https://developers.google.com/identity/protocols/oauth2)
- 🗄️ [PostgreSQL Docs](https://www.postgresql.org/docs/)
- 🐍 [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

---

## 💡 Tips & Tricks

### Export Users to JSON
```python
from google_oauth_collector import GoogleOAuthCollector

collector = GoogleOAuthCollector(DATABASE_URL)
collector.export_users_to_json('users.json')
```

### Query Users Programmatically
```python
from sqlalchemy_user_models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Get all admin users
admins = session.query(User).filter_by(role='admin').all()

# Get active users
active = session.query(User).filter_by(status='active').all()

# Get users by email domain
gmail_users = session.query(User).filter(
    User.email.like('%@gmail.com')
).all()
```

### Add Custom User Fields
```python
# Edit sqlalchemy_user_models.py
class User(Base):
    # ... existing fields ...
    custom_field = Column(String(255))  # Add this
```

---

## 🎯 Next Steps

1. ✅ Read **SETUP_GUIDE.md**
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Setup PostgreSQL and schema
4. ✅ Get Google OAuth credentials
5. ✅ Configure `.env` file
6. ✅ Run application
7. ✅ Test authentication
8. ✅ Deploy to production

---

## 📄 License

MIT License - Free to use for learning and development

---

## 👨‍💻 Version Info

- **Version:** 1.0
- **Created:** December 6, 2025
- **Python:** 3.7+
- **PostgreSQL:** 10+
- **Status:** ✅ Production Ready

---

**🎉 Ready to get started? See SETUP_GUIDE.md**
