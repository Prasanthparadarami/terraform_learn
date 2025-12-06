"""
Standalone Script: Collect Google OAuth Data and Store in PostgreSQL
Simple command-line tool to authenticate with Google and store user data

Usage:
    python google_oauth_collector.py

Install dependencies:
    pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
    pip install sqlalchemy psycopg2-binary python-dotenv bcrypt
"""

import os
import json
import bcrypt
from datetime import datetime
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_user_models import (
    Base, User, UserProfile, UserAuthentication, UserPreferences, UserActivityLog
)

# Load environment variables
load_dotenv()

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/user_db')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# Scopes for Google API
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email'
]


class GoogleOAuthCollector:
    """Collect Google OAuth data and store in PostgreSQL"""
    
    def __init__(self, db_url):
        """Initialize database connection"""
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def authenticate_with_google(self):
        """Authenticate user with Google OAuth and return user info"""
        try:
            # Create OAuth flow
            flow = Flow.from_client_secrets_file(
                'credentials.json',
                scopes=SCOPES
            )
            flow.redirect_uri = 'http://localhost:8080/'
            
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            print("Please visit this URL to authorize the app:")
            print(authorization_url)
            print("\nAfter authorization, copy the authorization code from the URL")
            
            auth_code = input("Paste authorization code: ").strip()
            
            # Exchange code for token
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            
            # Fetch user info
            import requests
            headers = {'Authorization': f'Bearer {credentials.token}'}
            response = requests.get(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                headers=headers
            )
            
            if response.status_code == 200:
                user_info = response.json()
                return user_info, credentials
            else:
                print(f"Error fetching user info: {response.status_code}")
                return None, None
        
        except Exception as e:
            print(f"Error during Google authentication: {str(e)}")
            return None, None
    
    def save_user_to_db(self, google_user_info, credentials):
        """Save user data to PostgreSQL"""
        try:
            session = self.Session()
            
            # Check if user already exists
            user = session.query(User).filter_by(
                email=google_user_info.get('email')
            ).first()
            
            if user:
                print(f"\n✓ User already exists: {user.email}")
                
                # Update authentication
                auth = session.query(UserAuthentication).filter_by(
                    user_id=user.id,
                    auth_provider='google'
                ).first()
                
                if auth:
                    auth.access_token = credentials.token
                    if credentials.refresh_token:
                        auth.refresh_token = credentials.refresh_token
                    if credentials.expiry:
                        auth.token_expiry = credentials.expiry
                    print("✓ Updated OAuth tokens")
            else:
                # Create new user
                username = google_user_info.get('email', '').split('@')[0]
                
                user = User(
                    username=username,
                    email=google_user_info.get('email'),
                    password_hash=self._hash_password(os.urandom(16).hex()),
                    first_name=google_user_info.get('given_name', ''),
                    last_name=google_user_info.get('family_name', ''),
                    full_name=google_user_info.get('name', ''),
                    profile_picture_url=google_user_info.get('picture', ''),
                    is_email_verified=google_user_info.get('verified_email', False),
                    status='active'
                )
                session.add(user)
                session.flush()
                
                print(f"\n✓ Created new user: {user.email}")
                
                # Create user profile
                profile = UserProfile(user_id=user.id)
                session.add(profile)
                print("✓ Created user profile")
                
                # Create user preferences
                preferences = UserPreferences(user_id=user.id)
                session.add(preferences)
                print("✓ Created user preferences")
                
                # Add OAuth authentication
                auth = UserAuthentication(
                    user_id=user.id,
                    auth_provider='google',
                    provider_user_id=google_user_info.get('id'),
                    provider_username=google_user_info.get('email'),
                    provider_email=google_user_info.get('email'),
                    access_token=credentials.token,
                    refresh_token=credentials.refresh_token,
                    token_expiry=credentials.expiry,
                    additional_data={
                        'locale': google_user_info.get('locale', ''),
                        'picture': google_user_info.get('picture', '')
                    },
                    is_primary=True
                )
                session.add(auth)
                print("✓ Added OAuth authentication")
            
            # Log activity
            activity = UserActivityLog(
                user_id=user.id,
                action='oauth_authentication',
                resource_type='user',
                resource_id=str(user.id),
                status='success'
            )
            session.add(activity)
            
            session.commit()
            
            print("\n✓ Successfully saved to PostgreSQL")
            self._display_user_info(user)
            
            session.close()
            return True
        
        except Exception as e:
            print(f"Error saving to database: {str(e)}")
            session.rollback()
            session.close()
            return False
    
    def _hash_password(self, password):
        """Hash password with bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _display_user_info(self, user):
        """Display user information"""
        print("\n" + "="*50)
        print("USER INFORMATION STORED IN DATABASE")
        print("="*50)
        print(f"ID:              {user.id}")
        print(f"Username:        {user.username}")
        print(f"Email:           {user.email}")
        print(f"Name:            {user.first_name} {user.last_name}")
        print(f"Role:            {user.role}")
        print(f"Status:          {user.status}")
        print(f"Email Verified:  {user.is_email_verified}")
        print(f"Created:         {user.created_at}")
        print("="*50 + "\n")
    
    def list_all_users(self):
        """List all users in database"""
        try:
            session = self.Session()
            
            users = session.query(User).all()
            
            if not users:
                print("\nNo users found in database")
                return
            
            print("\n" + "="*70)
            print("ALL USERS IN DATABASE")
            print("="*70)
            
            for user in users:
                print(f"\nID: {user.id}")
                print(f"  Username:      {user.username}")
                print(f"  Email:         {user.email}")
                print(f"  Name:          {user.first_name} {user.last_name}")
                print(f"  Role:          {user.role}")
                print(f"  Status:        {user.status}")
                print(f"  Created:       {user.created_at}")
                print(f"  Last Login:    {user.last_login or 'Never'}")
            
            print("\n" + "="*70 + "\n")
            
            session.close()
        
        except Exception as e:
            print(f"Error fetching users: {str(e)}")
    
    def export_users_to_json(self, filename='users_export.json'):
        """Export all users to JSON file"""
        try:
            session = self.Session()
            
            users = session.query(User).all()
            
            users_data = []
            for user in users:
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'status': user.status,
                    'is_email_verified': user.is_email_verified,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                })
            
            with open(filename, 'w') as f:
                json.dump(users_data, f, indent=2)
            
            print(f"\n✓ Exported {len(users_data)} users to {filename}")
            
            session.close()
        
        except Exception as e:
            print(f"Error exporting users: {str(e)}")


def main():
    """Main function"""
    print("\n" + "="*50)
    print("GOOGLE OAUTH DATA COLLECTOR")
    print("="*50 + "\n")
    
    # Check environment variables
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        print("Error: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET not set in .env")
        print("Please configure .env file with Google OAuth credentials")
        return
    
    collector = GoogleOAuthCollector(DATABASE_URL)
    
    while True:
        print("\nOptions:")
        print("1. Authenticate with Google and store data")
        print("2. List all users")
        print("3. Export users to JSON")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            print("\nAuthenticating with Google...")
            user_info, credentials = collector.authenticate_with_google()
            
            if user_info and credentials:
                print("\nSaving to PostgreSQL database...")
                collector.save_user_to_db(user_info, credentials)
        
        elif choice == '2':
            collector.list_all_users()
        
        elif choice == '3':
            filename = input("Enter filename (default: users_export.json): ").strip()
            if not filename:
                filename = 'users_export.json'
            collector.export_users_to_json(filename)
        
        elif choice == '4':
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid option. Please try again.")


if __name__ == '__main__':
    main()
