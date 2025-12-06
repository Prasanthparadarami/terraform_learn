# ✅ Google OAuth + PostgreSQL Application - Setup Checklist

## Pre-Setup (Complete Before Starting)

- [ ] Python 3.7+ installed
- [ ] PostgreSQL 10+ installed and running
- [ ] Git installed
- [ ] Google account (for OAuth)
- [ ] Internet connection

## Step 1: Install Dependencies (5 minutes)

```bash
cd d:\terraform_learn
pip install -r requirements.txt
```

- [ ] Flask 2.3.3
- [ ] google-auth-oauthlib 1.1.0
- [ ] sqlalchemy 2.0.21
- [ ] psycopg2-binary 2.9.9
- [ ] python-dotenv 1.0.0
- [ ] bcrypt 4.1.1

**Verify:**
```bash
python -c "import flask; print('Flask OK')"
python -c "import sqlalchemy; print('SQLAlchemy OK')"
```

## Step 2: Setup PostgreSQL Database (10 minutes)

```bash
# Create database
createdb user_db

# Create tables
psql -U postgres -d user_db -f sql_ddl_user_schema.sql

# Verify tables created
psql -U postgres -d user_db -c "\dt"
```

- [ ] Database `user_db` created
- [ ] All 11 tables created:
  - [ ] users
  - [ ] user_profiles
  - [ ] user_authentications
  - [ ] user_sessions
  - [ ] user_login_history
  - [ ] user_activity_log
  - [ ] user_notifications
  - [ ] user_preferences
  - [ ] user_roles
  - [ ] user_permissions

**Verify:**
```bash
psql -U postgres -d user_db -c "SELECT COUNT(*) FROM users;"
# Should return: 0 (empty table)
```

## Step 3: Get Google OAuth Credentials (15 minutes)

1. [ ] Go to: https://console.cloud.google.com/
2. [ ] Click "Create Project"
3. [ ] Name: "OAuth Test" (or your choice)
4. [ ] Wait for project creation
5. [ ] Go to "APIs & Services"
6. [ ] Click "Enable APIs and Services"
7. [ ] Search for "Google+ API"
8. [ ] Click "Enable"
9. [ ] Go to "Credentials"
10. [ ] Click "Create Credentials" → "OAuth client ID"
11. [ ] Select "Web application"
12. [ ] Add "Authorized redirect URIs":
    - `http://localhost:5000/auth/callback`
13. [ ] Click "Create"
14. [ ] Download JSON file
15. [ ] Save as `credentials.json` in project root

**Verify:**
```bash
ls credentials.json
# Should list the file
```

## Step 4: Configure Environment Variables (5 minutes)

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# Get these from Google Console
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_SECRET_HERE

# PostgreSQL (change password if needed)
DATABASE_URL=postgresql://postgres:password@localhost:5432/user_db

# Flask (change to random string)
SECRET_KEY=your-random-secret-key-here
```

- [ ] GOOGLE_CLIENT_ID filled
- [ ] GOOGLE_CLIENT_SECRET filled
- [ ] DATABASE_URL correct
- [ ] SECRET_KEY set to random string

**Verify:**
```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('OK' if os.getenv('GOOGLE_CLIENT_ID') else 'MISSING')"
# Should print: OK
```

## Step 5: Test Database Connection (5 minutes)

```bash
python
```

```python
from sqlalchemy_user_models import Base, User
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
Base.metadata.bind = engine

# Try to query
connection = engine.connect()
result = connection.execute("SELECT COUNT(*) FROM users;")
print(f"Users in database: {result.fetchone()[0]}")
connection.close()
```

- [ ] Connected to database
- [ ] Can query tables
- [ ] No connection errors

**Type `exit()` to quit Python shell**

## Step 6: Run Application (Choose One)

### Option A: Flask Web Application

```bash
python google_oauth_app.py
```

- [ ] Server started
- [ ] Output shows: "Running on http://127.0.0.1:5000"
- [ ] Open browser: http://localhost:5000
- [ ] Page loads successfully

### Option B: CLI Collector Tool

```bash
python google_oauth_collector.py
```

- [ ] Menu displayed
- [ ] Can see options 1-4

**Continue with Option A (Web App) below**

## Step 7: Test Google OAuth (Web App Only)

1. [ ] Open: http://localhost:5000
2. [ ] Click "Login / Sign Up"
3. [ ] Click "Continue with Google"
4. [ ] Select your Google account
5. [ ] Click "Allow" to authorize
6. [ ] Redirected to dashboard
7. [ ] See your profile information

**Check Dashboard:**
- [ ] First name shows
- [ ] Last name shows
- [ ] Email shows
- [ ] Profile picture shows (if available)

## Step 8: Verify Data in PostgreSQL

```bash
psql -U postgres -d user_db
```

```sql
SELECT id, username, email, first_name, last_name FROM users;
SELECT * FROM user_authentications WHERE auth_provider='google';
SELECT * FROM user_login_history ORDER BY created_at DESC LIMIT 1;
```

- [ ] User record exists in `users` table
- [ ] OAuth record exists in `user_authentications`
- [ ] Login record exists in `user_login_history`

**Type `\q` to exit PostgreSQL**

## Step 9: Test Email Registration (Web App)

1. [ ] Go to: http://localhost:5000/login
2. [ ] Click "Sign Up" tab
3. [ ] Fill form:
   - [ ] First Name: John
   - [ ] Last Name: Doe
   - [ ] Username: john_doe
   - [ ] Email: john@example.com
   - [ ] Password: password123
4. [ ] Click "Create Account"
5. [ ] Go back to login
6. [ ] Enter email and password
7. [ ] Click "Login"
8. [ ] See dashboard

**Verify in Database:**
```bash
psql -U postgres -d user_db -c "SELECT email, username FROM users ORDER BY created_at DESC LIMIT 1;"
```

- [ ] New user record created

## Step 10: Test CLI Collector (Optional)

```bash
python google_oauth_collector.py
```

1. [ ] Select "1 - Authenticate with Google"
2. [ ] Visit URL shown
3. [ ] Authorize account
4. [ ] Copy authorization code
5. [ ] Paste into terminal
6. [ ] See "Successfully saved" message
7. [ ] Select "2 - List all users"
8. [ ] See users displayed
9. [ ] Select "3 - Export users to JSON"
10. [ ] Check users_export.json created

- [ ] OAuth flow works
- [ ] Data saved to database
- [ ] Export functionality works

## Step 11: Production Checklist (Before Deploying)

### Security
- [ ] Change FLASK_ENV to 'production'
- [ ] Use strong SECRET_KEY (32 characters)
- [ ] Rotate GOOGLE_CLIENT_SECRET
- [ ] Setup HTTPS/SSL certificate
- [ ] Enable CSRF protection
- [ ] Add rate limiting

### Database
- [ ] Use managed PostgreSQL (not local)
- [ ] Enable SSL for DB connections
- [ ] Setup automated backups
- [ ] Test backup/restore
- [ ] Monitor database size

### Deployment
- [ ] Use Gunicorn/uWSGI
- [ ] Setup Nginx reverse proxy
- [ ] Add Upstart/Systemd service file
- [ ] Configure logging
- [ ] Setup error tracking
- [ ] Add monitoring/alerts

### Google OAuth
- [ ] Update redirect URI to production domain
- [ ] Review OAuth scopes
- [ ] Setup verified domain
- [ ] Add privacy policy
- [ ] Add terms of service

## Final Verification Checklist

### Core Functionality
- [ ] Google OAuth login works
- [ ] Email registration works
- [ ] Email login works
- [ ] Logout works
- [ ] Dashboard displays correct data

### Database
- [ ] All tables created
- [ ] Data persists after restart
- [ ] Queries return correct results
- [ ] Relationships work correctly

### Security
- [ ] Passwords hashed in database
- [ ] Session tokens generated
- [ ] CSRF tokens present
- [ ] No sensitive data in logs

### Performance
- [ ] App starts in < 2 seconds
- [ ] Pages load in < 1 second
- [ ] Queries complete in < 100ms

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| Connection refused | Start PostgreSQL service |
| Google auth fails | Check CLIENT_ID, SECRET, redirect URI |
| Module not found | Run: `pip install -r requirements.txt` |
| Port 5000 in use | Edit: `app.run(port=5001)` |
| Database not found | Run: `createdb user_db` |
| Tables not created | Run: `psql -U postgres -d user_db -f sql_ddl_user_schema.sql` |

## Success! You're Done 🎉

If all checkboxes are complete, you have:

✅ Working PostgreSQL database  
✅ Google OAuth authentication  
✅ Email/password registration  
✅ User profile management  
✅ Session tracking  
✅ Activity logging  
✅ Production-ready application  

## Next Steps

1. **Deploy to Production**
   - See README_OAUTH.md for deployment instructions

2. **Customize**
   - Add more fields to user profiles
   - Implement additional OAuth providers
   - Add email verification
   - Add password reset flow

3. **Integrate**
   - Add to your existing app
   - Extend with more features
   - Connect additional services

4. **Monitor**
   - Setup error tracking
   - Monitor performance
   - Track user activity
   - Review logs regularly

---

**Created:** December 6, 2025  
**Estimated Time:** 60-90 minutes  
**Difficulty:** Beginner to Intermediate  
**Status:** ✅ Ready to Deploy
