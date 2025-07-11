from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    ValidationError,
    Regexp,
)


class LoginForm(FlaskForm):
    """Form for user login."""

    email = EmailField(
        "Email", validators=[DataRequired(), Email(message="Invalid email address")]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    """Form for user registration."""

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(
                min=3, max=64, message="Username must be between 3 and 64 characters"
            ),
            Regexp(
                "^[A-Za-z0-9_.]+$",
                message="Username can only contain letters, numbers, dots, and underscores",
            ),
        ],
    )

    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Invalid email address"),
            Length(max=120),
        ],
    )

    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(message="First name is required"),
            Length(max=64, message="First name must be less than 64 characters."),
            Regexp(
                r"^[A-Za-z\s]+$",
                message="First name must contain only letters and spaces.",
            ),
        ],
    )

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(message="Last name is required"),
            Length(max=64, message="Last name must be less than 64 characters."),
            Regexp(
                r"^[A-Za-z\s]+$",
                message="Last name must contain only letters and spaces.",
            ),
        ],
    )

    phone_number = StringField(
        "Phone Number",
        validators=[
            DataRequired(message="Phone number is required"),
            Length(min=10, max=10, message="Phone number must be 10 digits."),
            Regexp(r"^[0-9]+$", message="Phone number must contain only digits."),
        ],
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long"),
            Regexp(
                r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$",
                message="Password must contain at least one letter and one number",
            ),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        """Validate the username is not already in use."""
        from app.models.user import User

        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Username already in use. Please choose a different username."
            )

    def validate_email(self, email):
        """Validate the email is not already in use."""
        from app.models.user import User

        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                "Email already registered. Please use a different email or log in."
            )