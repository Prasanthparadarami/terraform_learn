"""
Google OAuth Integration with PostgreSQL
Simple Python application to authenticate users via Google and store data in PostgreSQL

Install dependencies:
pip install flask google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install sqlalchemy psycopg2-binary python-dotenv bcrypt
"""

import os
import json
import secrets
from datetime import datetime
from functools import wraps

import bcrypt
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import ORM models
from sqlalchemy_user_models import (
    Base, User, UserProfile, UserAuthentication, UserSession,
    UserLoginHistory, UserPreferences, UserActivityLog
)

# Load environment variables
load_dotenv()

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/user_db')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/callback')
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Database setup
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Google OAuth configuration
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email'
]


def get_db_session():
    """Get a database session"""
    return Session()


def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_session_token():
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)


def get_google_flow():
    """Create and return Google OAuth flow"""
    return Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        db = get_db_session()
        user = db.query(User).filter_by(id=session['user_id']).first()
        db.close()
        return render_template('index.html', user=user)
    return render_template('index.html', user=None)


@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')


@app.route('/auth/google')
def auth_google():
    """Initiate Google OAuth flow"""
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    session['state'] = state
    return redirect(authorization_url)


@app.route('/auth/callback')
def auth_callback():
    """Handle Google OAuth callback"""
    try:
        # Get authorization code
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code or state != session.get('state'):
            return redirect(url_for('login'))
        
        # Exchange code for token
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URI
        )
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        # Get user info from Google
        import google.auth.transport.requests as google_requests
        from google.oauth2 import service_account
        import requests
        
        headers = {'Authorization': f'Bearer {credentials.token}'}
        google_user_info = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            headers=headers
        ).json()
        
        # Database session
        db = get_db_session()
        
        # Check if user exists
        user = db.query(User).filter_by(email=google_user_info.get('email')).first()
        
        if not user:
            # Create new user
            user = User(
                username=google_user_info.get('email', '').split('@')[0],
                email=google_user_info.get('email'),
                password_hash=hash_password(secrets.token_urlsafe(16)),
                first_name=google_user_info.get('given_name', ''),
                last_name=google_user_info.get('family_name', ''),
                full_name=google_user_info.get('name', ''),
                profile_picture_url=google_user_info.get('picture', ''),
                is_email_verified=google_user_info.get('verified_email', False),
                status='active'
            )
            db.add(user)
            db.flush()
            
            # Create user profile
            profile = UserProfile(user_id=user.id)
            db.add(profile)
            
            # Create user preferences
            preferences = UserPreferences(user_id=user.id)
            db.add(preferences)
            
            db.commit()
        
        # Add or update authentication method
        auth = db.query(UserAuthentication).filter_by(
            user_id=user.id,
            auth_provider='google'
        ).first()
        
        if not auth:
            auth = UserAuthentication(
                user_id=user.id,
                auth_provider='google',
                provider_user_id=google_user_info.get('id'),
                provider_username=google_user_info.get('email'),
                provider_email=google_user_info.get('email'),
                is_primary=True
            )
            db.add(auth)
        
        # Update token
        auth.access_token = credentials.token
        if credentials.refresh_token:
            auth.refresh_token = credentials.refresh_token
        if credentials.expiry:
            auth.token_expiry = credentials.expiry
        auth.additional_data = {
            'locale': google_user_info.get('locale', ''),
            'picture': google_user_info.get('picture', '')
        }
        
        db.commit()
        
        # Create session
        session_token = generate_session_token()
        user_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            device_type='web',
            is_active=True
        )
        db.add(user_session)
        
        # Log login
        login_log = UserLoginHistory(
            user_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            device_type='web',
            login_successful=True,
            login_method='oauth'
        )
        db.add(login_log)
        
        # Update user last login
        user.last_login = datetime.utcnow()
        user.login_count += 1
        
        # Log activity
        activity = UserActivityLog(
            user_id=user.id,
            action='user_login_oauth',
            resource_type='user',
            resource_id=str(user.id),
            status='success',
            ip_address=request.remote_addr
        )
        db.add(activity)
        
        db.commit()
        db.close()
        
        # Set session
        session['user_id'] = user.id
        session['session_token'] = session_token
        
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        print(f"Error during Google OAuth: {str(e)}")
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user with email/password"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            
            # Validation
            if not all([username, email, password, first_name, last_name]):
                return jsonify({'error': 'All fields are required'}), 400
            
            db = get_db_session()
            
            # Check if user exists
            if db.query(User).filter_by(email=email).first():
                db.close()
                return jsonify({'error': 'Email already registered'}), 409
            
            if db.query(User).filter_by(username=username).first():
                db.close()
                return jsonify({'error': 'Username already taken'}), 409
            
            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                first_name=first_name,
                last_name=last_name,
                full_name=f"{first_name} {last_name}",
                status='active'
            )
            db.add(user)
            db.flush()
            
            # Create profile and preferences
            profile = UserProfile(user_id=user.id)
            preferences = UserPreferences(user_id=user.id)
            db.add(profile)
            db.add(preferences)
            
            db.commit()
            db.close()
            
            return jsonify({'message': 'Registration successful', 'user_id': user.id}), 201
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('register.html')


@app.route('/login-email', methods=['POST'])
def login_email():
    """Login with email and password"""
    try:
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        db = get_db_session()
        user = db.query(User).filter_by(email=email).first()
        
        if not user or not verify_password(password, user.password_hash):
            db.close()
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if user.status != 'active':
            db.close()
            return jsonify({'error': 'Account is not active'}), 403
        
        # Create session
        session_token = generate_session_token()
        user_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            device_type='web',
            is_active=True
        )
        db.add(user_session)
        
        # Log login
        login_log = UserLoginHistory(
            user_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            login_successful=True,
            login_method='password'
        )
        db.add(login_log)
        
        user.last_login = datetime.utcnow()
        user.login_count += 1
        
        db.commit()
        db.close()
        
        session['user_id'] = user.id
        session['session_token'] = session_token
        
        return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    db = get_db_session()
    
    user = db.query(User).filter_by(id=session['user_id']).first()
    profile = db.query(UserProfile).filter_by(user_id=user.id).first()
    auths = db.query(UserAuthentication).filter_by(user_id=user.id).all()
    sessions = db.query(UserSession).filter_by(user_id=user.id, is_active=True).all()
    login_history = db.query(UserLoginHistory).filter_by(user_id=user.id).limit(10).all()
    
    db.close()
    
    return render_template('dashboard.html', 
                          user=user,
                          profile=profile,
                          auths=auths,
                          sessions=sessions,
                          login_history=login_history)


@app.route('/api/user/profile')
@login_required
def get_profile():
    """Get user profile data as JSON"""
    db = get_db_session()
    
    user = db.query(User).filter_by(id=session['user_id']).first()
    profile = db.query(UserProfile).filter_by(user_id=user.id).first()
    
    data = {
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'status': user.status,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        },
        'profile': {
            'company': profile.company,
            'job_title': profile.job_title,
            'country': profile.country,
            'city': profile.city,
            'timezone': profile.timezone
        } if profile else None
    }
    
    db.close()
    return jsonify(data)


@app.route('/api/user/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        db = get_db_session()
        
        user = db.query(User).filter_by(id=session['user_id']).first()
        profile = db.query(UserProfile).filter_by(user_id=user.id).first()
        
        # Update user
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'bio' in data:
            user.bio = data['bio']
        
        # Update profile
        if profile:
            if 'company' in data:
                profile.company = data['company']
            if 'job_title' in data:
                profile.job_title = data['job_title']
            if 'country' in data:
                profile.country = data['country']
            if 'city' in data:
                profile.city = data['city']
            if 'timezone' in data:
                profile.timezone = data['timezone']
        
        # Log activity
        activity = UserActivityLog(
            user_id=user.id,
            action='profile_updated',
            resource_type='user_profile',
            resource_id=str(user.id),
            changes=data,
            status='success'
        )
        db.add(activity)
        
        db.commit()
        db.close()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user/activities')
@login_required
def get_activities():
    """Get user activity log"""
    db = get_db_session()
    
    activities = db.query(UserActivityLog).filter_by(
        user_id=session['user_id']
    ).order_by(UserActivityLog.created_at.desc()).limit(20).all()
    
    data = [
        {
            'action': a.action,
            'resource_type': a.resource_type,
            'status': a.status,
            'created_at': a.created_at.isoformat() if a.created_at else None
        }
        for a in activities
    ]
    
    db.close()
    return jsonify(data)


@app.route('/logout')
def logout():
    """Logout user"""
    if 'user_id' in session and 'session_token' in session:
        db = get_db_session()
        
        user_session = db.query(UserSession).filter_by(
            session_token=session['session_token']
        ).first()
        
        if user_session:
            user_session.is_active = False
        
        db.commit()
        db.close()
    
    session.clear()
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(e):
    """404 error handler"""
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    """500 error handler"""
    return render_template('error.html', error='Server error'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
