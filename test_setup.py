"""
Local Testing Script for Google OAuth Application
Run this to verify everything is working before running the full app
"""

import os
import sys
from dotenv import load_dotenv

print("\n" + "="*60)
print("🧪 LOCAL TESTING - Google OAuth + PostgreSQL App")
print("="*60 + "\n")

# Load environment
load_dotenv()

# Test 1: Check Python Version
print("1️⃣  Checking Python Version...")
python_version = sys.version_info
if python_version.major >= 3 and python_version.minor >= 7:
    print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} - OK\n")
else:
    print(f"   ❌ Python {python_version.major}.{python_version.minor} - NEED 3.7+\n")
    sys.exit(1)

# Test 2: Check Required Packages
print("2️⃣  Checking Required Packages...")
required_packages = [
    'flask',
    'sqlalchemy',
    'psycopg2',
    'google_auth_oauthlib',
    'dotenv',
    'bcrypt',
    'requests'
]

all_packages_ok = True
for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"   ✅ {package}")
    except ImportError as e:
        print(f"   ❌ {package} - MISSING")
        all_packages_ok = False

if not all_packages_ok:
    print("\n   Run: pip install -r requirements.txt\n")
    sys.exit(1)

print()

# Test 3: Check Environment Variables
print("3️⃣  Checking Environment Variables (.env)...")
env_vars = {
    'DATABASE_URL': 'PostgreSQL connection string',
    'GOOGLE_CLIENT_ID': 'Google OAuth Client ID',
    'GOOGLE_CLIENT_SECRET': 'Google OAuth Secret',
    'SECRET_KEY': 'Flask secret key'
}

all_env_ok = True
for var, description in env_vars.items():
    value = os.getenv(var)
    if value and value != f'your_{var.lower()}_here':
        status = "✅" if var not in ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'] else "✅"
        print(f"   {status} {var}: Set")
    else:
        print(f"   ❌ {var}: Missing or not configured")
        all_env_ok = False

print()

if not all_env_ok:
    print("   ⚠️  Configuration incomplete!")
    print("   Run: cp .env.example .env")
    print("   Then edit .env with your values\n")
    sys.exit(1)

# Test 4: Check PostgreSQL Connection
print("4️⃣  Checking PostgreSQL Connection...")
try:
    from sqlalchemy import create_engine, text
    
    db_url = os.getenv('DATABASE_URL')
    engine = create_engine(db_url, echo=False)
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("   ✅ Connected to PostgreSQL")
        
        # Check tables
        result = connection.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        table_count = result.scalar()
        print(f"   ✅ Database has {table_count} tables")
        
        # Check users table
        result = connection.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"   ✅ Users table: {user_count} users")
    
    print()
except Exception as e:
    print(f"   ❌ Database connection failed: {str(e)}")
    print("   Make sure:")
    print("   • PostgreSQL is running")
    print("   • DATABASE_URL is correct in .env")
    print("   • Database 'user_db' exists")
    print("   • Run: createdb user_db")
    print("   • Run: psql -U postgres -d user_db -f sql_ddl_user_schema.sql\n")
    sys.exit(1)

# Test 5: Check ORM Models
print("5️⃣  Checking ORM Models...")
try:
    from sqlalchemy_user_models import Base, User, UserProfile, UserAuthentication
    print("   ✅ SQLAlchemy models loaded")
    print(f"   ✅ Base has {len(Base.registry.mappers)} mapped classes")
    print()
except Exception as e:
    print(f"   ❌ Error loading models: {str(e)}\n")
    sys.exit(1)

# Test 6: Check Flask App
print("6️⃣  Checking Flask App...")
try:
    from google_oauth_app import app
    print("   ✅ Flask app created")
    print(f"   ✅ App name: {app.name}")
    print(f"   ✅ Debug mode: {app.debug}")
    print()
except Exception as e:
    print(f"   ❌ Error loading Flask app: {str(e)}\n")
    sys.exit(1)

# Test 7: Check Google OAuth Config
print("7️⃣  Checking Google OAuth Configuration...")
google_client_id = os.getenv('GOOGLE_CLIENT_ID')
if google_client_id and 'your_' not in google_client_id:
    print(f"   ✅ Google Client ID configured")
    print(f"      ({google_client_id[:20]}...)")
else:
    print("   ⚠️  Google Client ID not configured")
    print("      Get from: https://console.cloud.google.com/")

print()

# Test 8: Check Credentials File
print("8️⃣  Checking credentials.json...")
if os.path.exists('credentials.json'):
    print("   ✅ credentials.json exists")
    try:
        import json
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
            if 'installed' in creds or 'web' in creds:
                print("   ✅ credentials.json is valid")
            else:
                print("   ⚠️  credentials.json format unexpected")
    except Exception as e:
        print(f"   ⚠️  Error reading credentials.json: {str(e)}")
else:
    print("   ⚠️  credentials.json not found")
    print("   Get from: https://console.cloud.google.com/")

print()

# Test 9: Test Database Queries
print("9️⃣  Testing Database Queries...")
try:
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy_user_models import User, UserAuthentication, UserLoginHistory
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Test different queries
    user_count = session.query(User).count()
    print(f"   ✅ Query users: {user_count} total")
    
    auth_count = session.query(UserAuthentication).count()
    print(f"   ✅ Query authentications: {auth_count} total")
    
    login_count = session.query(UserLoginHistory).count()
    print(f"   ✅ Query login history: {login_count} total")
    
    session.close()
    print()
except Exception as e:
    print(f"   ❌ Database query failed: {str(e)}\n")
    sys.exit(1)

# Summary
print("="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\nYour setup is ready. Next steps:\n")
print("Option 1: Run Flask Web App")
print("  python google_oauth_app.py")
print("  Then visit: http://localhost:5000\n")

print("Option 2: Run CLI Collector")
print("  python google_oauth_collector.py\n")

print("Option 3: Test in Python")
print("  python")
print("  from sqlalchemy_user_models import User")
print("  # ... run queries\n")

print("="*60 + "\n")
