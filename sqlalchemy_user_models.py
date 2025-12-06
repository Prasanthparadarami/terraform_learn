"""
SQLAlchemy ORM Models for User Information Schema
Compatible with PostgreSQL

Install: pip install sqlalchemy psycopg2-binary
"""

from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime, 
    Text, Date, ForeignKey, Enum, UniqueConstraint, 
    CheckConstraint, event, func, TypeDecorator
)
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
import enum

# Database connection (update with your credentials)
# DATABASE_URL = "postgresql://user:password@localhost:5432/user_db"
# engine = create_engine(DATABASE_URL)

Base = declarative_base()


class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    GUEST = "guest"


class AccountStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(200))
    phone_number = Column(String(20))
    date_of_birth = Column(Date)
    gender = Column(String(20), default="prefer_not_to_say")
    profile_picture_url = Column(Text)
    bio = Column(Text)
    role = Column(String(20), default="user", index=True)
    status = Column(String(20), default="active", index=True)
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, index=True)
    user_metadata = Column(JSONB, default={})

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    authentications = relationship("UserAuthentication", back_populates="user", cascade="all, delete-orphan")
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan", foreign_keys="UserRole.user_id")
    permissions = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan", foreign_keys="UserPermission.user_id")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    login_history = relationship("UserLoginHistory", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("UserActivityLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("UserNotification", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'"),
    )

    @validates('email')
    def validate_email(self, key, value):
        if '@' not in value:
            raise ValueError("Invalid email address")
        return value.lower()

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company = Column(String(255))
    job_title = Column(String(255))
    country = Column(String(100))
    city = Column(String(100))
    state_province = Column(String(100))
    postal_code = Column(String(20))
    address_line_1 = Column(String(255))
    address_line_2 = Column(String(255))
    timezone = Column(String(50))
    language_preference = Column(String(10), default="en")
    notification_preferences = Column(JSONB, default={"email": True, "sms": False, "push": True})
    privacy_settings = Column(JSONB, default={"profile_public": False, "show_email": False})
    bio_extended = Column(Text)
    social_links = Column(JSONB, default={})
    preferences = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, company='{self.company}')>"


class UserAuthentication(Base):
    __tablename__ = "user_authentications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    auth_provider = Column(String(50), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    provider_username = Column(String(255))
    provider_email = Column(String(120))
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expiry = Column(DateTime)
    additional_data = Column(JSONB, default={})
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="authentications")

    __table_args__ = (
        UniqueConstraint("user_id", "auth_provider", name="uq_user_auth_provider"),
    )

    def __repr__(self):
        return f"<UserAuthentication(user_id={self.user_id}, provider='{self.auth_provider}')>"


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_name = Column(String(100), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    expires_at = Column(DateTime)
    reason = Column(String(500))

    user = relationship("User", back_populates="roles", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("user_id", "role_name", name="uq_user_role"),
    )

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role='{self.role_name}')>"


class UserPermission(Base):
    __tablename__ = "user_permissions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission_name = Column(String(100), nullable=False)
    resource = Column(String(255))
    action = Column(String(50))
    granted_at = Column(DateTime, default=datetime.utcnow)
    granted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="permissions", foreign_keys=[user_id])

    __table_args__ = (
        UniqueConstraint("user_id", "permission_name", "resource", name="uq_user_permission_resource"),
    )

    def __repr__(self):
        return f"<UserPermission(user_id={self.user_id}, permission='{self.permission_name}')>"


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(500), unique=True, nullable=False)
    ip_address = Column(INET)
    user_agent = Column(Text)
    device_type = Column(String(50))
    device_name = Column(String(255))
    browser_name = Column(String(100))
    os_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True, index=True)

    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, device='{self.device_name}')>"


class UserLoginHistory(Base):
    __tablename__ = "user_login_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(INET)
    user_agent = Column(Text)
    device_type = Column(String(50))
    browser_name = Column(String(100))
    os_name = Column(String(100))
    login_successful = Column(Boolean, nullable=False)
    failure_reason = Column(String(255))
    login_method = Column(String(50), default="password")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="login_history")

    def __repr__(self):
        return f"<UserLoginHistory(user_id={self.user_id}, successful={self.login_successful})>"


class UserActivityLog(Base):
    __tablename__ = "user_activity_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    changes = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="activity_logs")

    def __repr__(self):
        return f"<UserActivityLog(user_id={self.user_id}, action='{self.action}')>"


class UserNotification(Base):
    __tablename__ = "user_notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notification_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSONB, default={})
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<UserNotification(user_id={self.user_id}, type='{self.notification_type}')>"


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    theme = Column(String(50), default="light")
    language = Column(String(10), default="en")
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    marketing_emails = Column(Boolean, default=False)
    data_collection = Column(Boolean, default=True)
    additional_preferences = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id}, theme='{self.theme}')>"


# Create all tables
# Base.metadata.create_all(engine)

# Example usage:
# from sqlalchemy.orm import sessionmaker
# Session = sessionmaker(bind=engine)
# session = Session()
# 
# new_user = User(
#     username="john_doe",
#     email="john@example.com",
#     password_hash="hashed_password",
#     first_name="John",
#     last_name="Doe"
# )
# session.add(new_user)
# session.commit()
