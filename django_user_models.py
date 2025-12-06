"""
Django ORM Models for User Information Schema
Compatible with PostgreSQL

Install: pip install django psycopg2-binary
"""

from django.db import models
from django.core.validators import EmailValidator, URLValidator
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.search import SearchVectorField
import uuid


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"
    MODERATOR = "moderator", "Moderator"
    GUEST = "guest", "Guest"


class AccountStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    SUSPENDED = "suspended", "Suspended"
    DELETED = "deleted", "Deleted"


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say", "Prefer not to say"


class User(models.Model):
    """User information model"""
    
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True, validators=[EmailValidator()])
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        default=Gender.PREFER_NOT_TO_SAY
    )
    profile_picture_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE,
        db_index=True
    )
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    last_login = models.DateTimeField(blank=True, null=True)
    login_count = models.IntegerField(default=0)
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['status']),
            models.Index(fields=['role']),
            models.Index(fields=['created_at']),
            models.Index(fields=['deleted_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def is_active(self):
        return self.status == AccountStatus.ACTIVE and self.deleted_at is None

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.status = AccountStatus.DELETED
        self.save()


class UserProfile(models.Model):
    """Extended user profile information"""
    
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company = models.CharField(max_length=255, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    language_preference = models.CharField(max_length=10, default='en')
    notification_preferences = models.JSONField(
        default=dict,
        blank=True
    )
    privacy_settings = models.JSONField(
        default=dict,
        blank=True
    )
    bio_extended = models.TextField(blank=True, null=True)
    social_links = models.JSONField(default=dict, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"

    def __str__(self):
        return f"Profile for {self.user.username}"


class UserAuthentication(models.Model):
    """Third-party authentication methods"""
    
    AUTH_PROVIDERS = (
        ('google', 'Google'),
        ('github', 'GitHub'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('microsoft', 'Microsoft'),
        ('apple', 'Apple'),
    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authentications')
    auth_provider = models.CharField(max_length=50, choices=AUTH_PROVIDERS)
    provider_user_id = models.CharField(max_length=255)
    provider_username = models.CharField(max_length=255, blank=True, null=True)
    provider_email = models.EmailField(blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)
    additional_data = models.JSONField(default=dict, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_authentications"
        unique_together = ('user', 'auth_provider')
        indexes = [
            models.Index(fields=['user', 'auth_provider']),
            models.Index(fields=['auth_provider']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.auth_provider}"


class UserSession(models.Model):
    """Active user sessions"""
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_token = models.CharField(max_length=500, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    browser_name = models.CharField(max_length=100, blank=True, null=True)
    os_name = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "user_sessions"
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_token']),
        ]

    def __str__(self):
        return f"Session for {self.user.username}"

    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class UserLoginHistory(models.Model):
    """User login history tracking"""
    
    LOGIN_METHODS = (
        ('password', 'Password'),
        ('oauth', 'OAuth'),
        ('mfa', 'Multi-Factor Auth'),
        ('sso', 'Single Sign On'),
    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    browser_name = models.CharField(max_length=100, blank=True, null=True)
    os_name = models.CharField(max_length=100, blank=True, null=True)
    login_successful = models.BooleanField()
    failure_reason = models.CharField(max_length=255, blank=True, null=True)
    login_method = models.CharField(
        max_length=50,
        choices=LOGIN_METHODS,
        default='password'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "user_login_history"
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        status = "Success" if self.login_successful else "Failed"
        return f"{self.user.username} - {status}"


class UserActivityLog(models.Model):
    """User activity logging"""
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100, blank=True, null=True)
    resource_id = models.CharField(max_length=255, blank=True, null=True)
    changes = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "user_activity_log"
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.action}"


class UserNotification(models.Model):
    """User notifications"""
    
    NOTIFICATION_TYPES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
        ('in_app', 'In App'),
    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(
        max_length=100,
        choices=NOTIFICATION_TYPES
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "user_notifications"
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} to {self.user.username}"

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class UserPreferences(models.Model):
    """User preferences and settings"""
    
    THEMES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    )

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(max_length=50, choices=THEMES, default='light')
    language = models.CharField(max_length=10, default='en')
    notifications_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    data_collection = models.BooleanField(default=True)
    additional_preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_preferences"

    def __str__(self):
        return f"Preferences for {self.user.username}"
