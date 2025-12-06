# 🧪 Local Testing Guide

## Current Status

✅ **PASSED:**
- Python 3.12.5 installed
- All required packages installed
- Environment variables configured (.env)
- Google OAuth credentials ready

❌ **NEEDS SETUP:**
- PostgreSQL database connection

---

## Step 1: Setup PostgreSQL

### On Windows:

```bash
# Start PostgreSQL service
# Option A: Using Services
#   Open Services → Find "PostgreSQL" → Right-click → Start

# Option B: Using PowerShell
Start-Service postgresql

# Option C: Using command line
pg_ctl -D "C:\Program Files\PostgreSQL\15\data" start
```

### Verify PostgreSQL is Running:
```bash
psql --version
psql -U postgres -c "SELECT 1"
```

### Create Database:
```bash
# If you get password prompt, use your PostgreSQL password
createdb -U postgres user_db
```

---

## Step 2: Update .env File

Edit `d:\terraform_learn\.env`:

```bash
# Update with your PostgreSQL password if needed
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/user_db

# Keep these (should already be set)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
SECRET_KEY=...
```

---

## Step 3: Create Database Tables

```bash
# Run the SQL schema
psql -U postgres -d user_db -f sql_ddl_user_schema.sql

# Verify tables were created
psql -U postgres -d user_db -c "\dt"
```

---

## Step 4: Run Setup Test Again

```bash
cd d:\terraform_learn
python test_setup.py
```

Should show: ✅ ALL TESTS PASSED

---

## Step 5: Run Application

### Option A: Web Application
```bash
python google_oauth_app.py
# Then open: http://localhost:5000
```

### Option B: CLI Tool
```bash
python google_oauth_collector.py
# Follow the menu
```

### Option C: Python Interactive
```bash
python
>>> from sqlalchemy_user_models import User
>>> from sqlalchemy import create_engine
>>> from sqlalchemy.orm import sessionmaker
>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()
>>> engine = create_engine(os.getenv('DATABASE_URL'))
>>> Session = sessionmaker(bind=engine)
>>> session = Session()
>>> users = session.query(User).all()
>>> print(f"Total users: {len(users)}")
```

---

## Common Issues

### Issue 1: "FATAL: password authentication failed"
**Solution:**
```bash
# Edit .env with correct PostgreSQL password
# Or use postgres user without password if configured
DATABASE_URL=postgresql://postgres@localhost:5432/user_db
```

### Issue 2: "database 'user_db' does not exist"
**Solution:**
```bash
createdb -U postgres user_db
```

### Issue 3: "relation 'users' does not exist"
**Solution:**
```bash
psql -U postgres -d user_db -f sql_ddl_user_schema.sql
```

### Issue 4: "Port 5000 already in use"
**Solution:**
```bash
# Edit google_oauth_app.py
# Change: app.run(port=5000)
# To:     app.run(port=5001)
```

### Issue 5: "Google OAuth not working"
**Solution:**
1. Verify credentials.json exists
2. Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env
3. Check redirect URI in Google Cloud Console matches http://localhost:5000/auth/callback

---

## Testing Checklist

- [ ] PostgreSQL running
- [ ] .env file configured with correct password
- [ ] Database user_db created
- [ ] Tables created from sql_ddl_user_schema.sql
- [ ] test_setup.py passes all checks
- [ ] Choose and run: web app, CLI tool, or Python script

---

## Next: Quick Tests

### Test 1: Simple Database Query
```bash
cd d:\terraform_learn
python
>>> import os
>>> from dotenv import load_dotenv
>>> load_dotenv()
>>> from sqlalchemy import create_engine, text
>>> engine = create_engine(os.getenv('DATABASE_URL'))
>>> with engine.connect() as conn:
...     result = conn.execute(text("SELECT COUNT(*) FROM users"))
...     print(f"Users in DB: {result.scalar()}")
>>> exit()
```

### Test 2: Run Flask App
```bash
python google_oauth_app.py
# Open: http://localhost:5000
# Click: Continue with Google
# Authorize
# Check dashboard shows your profile
```

### Test 3: CLI Tool
```bash
python google_oauth_collector.py
# Select: 1 - Authenticate
# Follow OAuth flow
# Verify: Data saved to database
```

---

## Helpful Commands

```bash
# Check PostgreSQL is running
psql --version

# Connect to database
psql -U postgres -d user_db

# List tables
\dt

# Query users
SELECT * FROM users;

# Exit psql
\q

# Reset test environment
dropdb -U postgres user_db
createdb -U postgres user_db
psql -U postgres -d user_db -f sql_ddl_user_schema.sql

# View .env file
type .env

# Show local IP (for testing from other machines)
ipconfig
```

---

## You're Ready When:

✅ PostgreSQL is running  
✅ Database user_db exists  
✅ Tables are created  
✅ test_setup.py passes all checks  
✅ You can run one of the applications  

**Then choose:**
1. **Web App**: `python google_oauth_app.py` → http://localhost:5000
2. **CLI Tool**: `python google_oauth_collector.py`
3. **Python**: Interactive testing

---

## Troubleshooting Help

If you get stuck:

1. **Check PostgreSQL Status:**
   ```bash
   psql -U postgres -c "SELECT 1"
   ```

2. **View Current Config:**
   ```bash
   type .env
   ```

3. **Verify Database:**
   ```bash
   psql -U postgres -d user_db -c "\dt"
   ```

4. **Test Connection:**
   ```bash
   python test_setup.py
   ```

5. **Check Logs:** Look at application output for specific errors

---

**Ready to test? Start with Step 1: Setup PostgreSQL** 🚀
