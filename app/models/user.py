from datetime import datetime
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone_number = db.Column(db.String(20))
    profile_image = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100))
    reset_password_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    loyalty_points = db.Column(db.Integer, default=0)
    
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set password hash for the user."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password is correct."""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def generate_verification_token(self):
        """Generate a token for email verification."""
        self.verification_token = str(uuid.uuid4())
        db.session.commit()
        return self.verification_token
    
    def verify_email(self, token):
        """Verify the user's email with the provided token."""
        if self.verification_token == token:
            self.email_verified = True
            self.verification_token = None
            db.session.commit()
            return True
        return False
    
    def generate_reset_token(self, expiry_hours=24):
        """Generate a token for password reset."""
        from datetime import timedelta
        self.reset_password_token = str(uuid.uuid4())
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=expiry_hours)
        db.session.commit()
        return self.reset_password_token
    
    def verify_reset_token(self, token):
        """Verify the password reset token."""
        if self.reset_password_token != token:
            return False
        if self.reset_token_expiry and self.reset_token_expiry < datetime.utcnow():
            # Token expired
            return False
        return True
    
    def complete_password_reset(self, token, new_password):
        """Complete the password reset process."""
        if not self.verify_reset_token(token):
            return False
        self.set_password(new_password)
        self.reset_password_token = None
        self.reset_token_expiry = None
        self.login_attempts = 0
        self.locked_until = None
        db.session.commit()
        return True
    
    def track_login_attempt(self, successful):
        """Track login attempts and handle account locking."""
        if successful:
            self.login_attempts = 0
            self.locked_until = None
            self.last_login = datetime.utcnow()
        else:
            self.login_attempts += 1
            if self.login_attempts >= 5:
                from datetime import timedelta
                self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
    
    def is_account_locked(self):
        """Check if the account is currently locked."""
        if not self.locked_until:
            return False
        if self.locked_until > datetime.utcnow():
            return True
        # Reset if lock has expired
        self.locked_until = None
        self.login_attempts = 0
        db.session.commit()
        return False
    
    @classmethod
    def get_by_email(cls, email):
        """Get a user by email."""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_username(cls, username):
        """Get a user by username."""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def email_exists(cls, email):
        """Check if a user with the given email exists."""
        return cls.query.filter_by(email=email).first() is not None
    
    @classmethod
    def username_exists(cls, username):
        """Check if a user with the given username exists."""
        return cls.query.filter_by(username=username).first() is not None
    
    @classmethod
    def verify_token(cls, token):
        """Verify a user by token and return the user object."""
        user = cls.query.filter_by(verification_token=token).first()
        return user

@login_manager.user_loader
def load_user(id):
    """Load a user by ID for Flask-Login."""
    return User.query.get(int(id))
