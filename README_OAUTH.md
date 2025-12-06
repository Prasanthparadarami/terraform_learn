# Google OAuth Integration with PostgreSQL

Complete Python Flask application to authenticate users via Google OAuth and store data in PostgreSQL using SQLAlchemy ORM.

## 📋 Overview

This application provides:
- ✅ Google OAuth 2.0 authentication
- ✅ Email/password registration and login
- ✅ PostgreSQL database integration
- ✅ User profile management
- ✅ Session tracking
- ✅ Login history and activity logging
- ✅ Role-based access control
- ✅ Modern web interface

## 🚀 Quick Start

### Step 1: Prerequisites

Ensure you have installed:
- Python 3.7+
- PostgreSQL 10+
- Git

### Step 2: Clone/Setup Project

```bash
cd d:\terraform_learn
git clone <repo-url>  # or use existing repo
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup PostgreSQL Database

```bash
# Create database
createdb user_db

# Create tables
psql -U postgres -d user_db -f sql_ddl_user_schema.sql
```

### Step 5: Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google+ API**
4. Create OAuth 2.0 credentials (Web application)
   - Authorized redirect URIs: `http://localhost:5000/auth/callback`
5. Download credentials as JSON

**Note:** If downloading JSON directly:
```bash
# Save to credentials.json in project root
# Or rename and keep as credentials.json
```

### Step 6: Configure Environment

```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your values
# - DATABASE_URL: postgresql://user:password@localhost:5432/user_db
# - GOOGLE_CLIENT_ID: your_client_id
# - GOOGLE_CLIENT_SECRET: your_client_secret
# - SECRET_KEY: your_secret_key
```

### Step 7: Run Application

```bash
python google_oauth_app.py
```

Open browser: `http://localhost:5000`

## 📁 Project Structure

```
terraform_learn/
├── google_oauth_app.py           # Main Flask application
├── sqlalchemy_user_models.py     # ORM models
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── credentials.json              # Google OAuth credentials
├── sql_ddl_user_schema.sql      # Database schema
├── templates/
│   ├── index.html               # Home page
│   ├── login.html               # Login/signup page
│   ├── dashboard.html           # User dashboard
│   ├── register.html            # Registration page
│   └── error.html               # Error page
└── README_OAUTH.md              # This file
```

## 🔐 Features

### Authentication Methods

1. **Google OAuth 2.0**
   - One-click login
   - Auto-creates user account
   - Syncs profile picture

2. **Email/Password**
   - Traditional registration
   - Bcrypt password hashing
   - Session management

### User Management

- Complete user profiles
- Extended profile information (company, location, etc.)
- User preferences
- Activity logging
- Role-based access

### Security

- Password hashing with bcrypt
- Session tokens
- CSRF protection ready
- Login history tracking
- Failed login attempts tracking
- Soft delete support

## 🔗 API Endpoints

### Authentication

```
GET  /                          # Home page
GET  /login                     # Login page
GET  /register                  # Registration page
POST /register                  # Create account
POST /login-email               # Email login
GET  /auth/google               # Start Google OAuth
GET  /auth/callback             # Google OAuth callback
GET  /logout                    # Logout
```

### Dashboard

```
GET  /dashboard                 # User dashboard
GET  /api/user/profile          # Get user profile (JSON)
POST /api/user/update           # Update profile (JSON)
GET  /api/user/activities       # Get activity log (JSON)
```

## 💾 Database Tables

The application uses these ORM models:

- **User** - Core user information
- **UserProfile** - Extended profile details
- **UserAuthentication** - OAuth provider connections
- **UserSession** - Active sessions
- **UserLoginHistory** - Login audit trail
- **UserActivityLog** - User actions
- **UserNotification** - Notifications queue
- **UserPreferences** - User settings

See `USER_SCHEMA_README.md` for complete documentation.

## 🔧 Configuration Options

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/user_db

# Google OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback

# Flask
SECRET_KEY=your-secret-key
FLASK_ENV=development
FLASK_DEBUG=True

# Session
SESSION_COOKIE_SECURE=False          # Set True in production
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=2592000   # 30 days
```

## 📊 Data Flow

### Google OAuth Login

```
1. User clicks "Continue with Google"
   ↓
2. Redirect to Google login
   ↓
3. User authorizes app
   ↓
4. Google redirects to /auth/callback with code
   ↓
5. App exchanges code for token
   ↓
6. Fetch user info from Google
   ↓
7. Check if user exists in DB
   ├─ If YES: Update auth token
   └─ If NO: Create new user
   ↓
8. Create session
   ↓
9. Log login activity
   ↓
10. Redirect to dashboard
```

### Email Login

```
1. User fills login form
   ↓
2. POST to /login-email
   ↓
3. Verify email & password
   ↓
4. Create session
   ↓
5. Log login activity
   ↓
6. Redirect to dashboard
```

## 🧪 Testing

### Test Google OAuth Locally

```python
# Use OAuth 2.0 Playground: https://developers.google.com/oauthplayground/
# Or install ngrok for HTTPS tunnel:
pip install ngrok
ngrok http 5000
# Update GOOGLE_REDIRECT_URI to https URL
```

### Test Email Login

```bash
# Navigate to http://localhost:5000/login
# Switch to "Sign Up" tab
# Fill form and submit
# Login with credentials
```

## 🐛 Troubleshooting

### "PostgreSQL connection failed"
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running
- Verify database exists: `psql -l`

### "Google OAuth Error: invalid_client"
- Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
- Ensure credentials.json path is correct
- Verify redirect URI matches in Google Console

### "Port 5000 already in use"
```bash
# Use different port
python google_oauth_app.py  # Will use 5000
# Or modify: app.run(port=5001)
```

### "Session token not found"
- Clear browser cookies
- Clear session storage
- Restart application

## 📈 Production Deployment

### Before going live:

1. **Security**
   ```bash
   # Set secure environment variables
   SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   FLASK_ENV=production
   SESSION_COOKIE_SECURE=True
   ```

2. **Database**
   - Use managed PostgreSQL (AWS RDS, Azure Database, etc.)
   - Enable SSL connections
   - Setup automated backups

3. **HTTPS**
   - Get SSL certificate (Let's Encrypt)
   - Use HTTPS everywhere
   - Update Google redirect URI

4. **Server**
   - Use production WSGI server (Gunicorn, uWSGI)
   - Setup reverse proxy (Nginx, Apache)
   - Enable rate limiting

### Example Gunicorn Setup

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 google_oauth_app:app
```

### Example Nginx Config

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Support

For issues or questions:
1. Check troubleshooting section
2. Review logs: `app.logger`
3. Check PostgreSQL logs
4. Review Google OAuth configuration

## 📝 License

MIT License - Feel free to use for learning and development.

---

**Version:** 1.0  
**Last Updated:** December 6, 2025  
**Python Version:** 3.7+  
**PostgreSQL Version:** 10+
