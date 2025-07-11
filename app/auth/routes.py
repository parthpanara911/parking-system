from flask import (Blueprint, render_template,redirect,url_for,flash,request,session,current_app)
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError
from app import db
from app.models.user import User
from app.auth.forms import (
    LoginForm,
    RegistrationForm,
)
from app.utils.email import send_verification_email, send_password_reset_email

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=["GET", "POST"])
def register():
    """User registration endpoint."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            email = form.email.data.lower().strip()
            username = form.username.data.strip()

            user = User(
                username=username,
                email=email,
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                phone_number=form.phone_number.data.strip(),
            )
            user.set_password(form.password.data)

            token = user.generate_verification_token()
            if not token:
                raise ValueError("Failed to generate verification token")

            db.session.add(user)
            db.session.commit()

            try:
                send_verification_email(user, token)
                flash(
                    "Registration successful!",
                    "success",
                )
                return redirect(url_for("auth.login"))
            except Exception as e:
                current_app.logger.error(f"Email sending failed: {str(e)}")
                flash(
                    "Registration successful.",
                    "warning",
                )
                return redirect(url_for("auth.login"))

        except IntegrityError:
            db.session.rollback()
            flash("Username or email already exists. Please try again.", "danger")
        except ValueError as ve:
            db.session.rollback()
            flash(str(ve), "danger")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {str(e)}", exc_info=True)
            flash(f"An error occurred during registration. Please try again.", "danger")

    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    """User login endpoint."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user or not user.check_password(form.password.data):
            if user:
                user.track_login_attempt(successful=False)
            flash("Invalid email or password", "danger")
            return render_template("auth/login.html", form=form)

        # Check if account is locked due to too many failed attempts
        if user.is_account_locked():
            flash(
                "Your account has been temporarily locked due to too many failed login attempts. "
                "Please try again later.",
                "danger",
            )
            return render_template("auth/login.html", form=form)

        # Check if email is verified (if verification is required)
        if (
            current_app.config.get("REQUIRE_EMAIL_VERIFICATION", True)
            and not user.email_verified
        ):
            # In development mode, offer the option to bypass verification
            if current_app.config.get("DEBUG", False):
                verification_url = url_for("auth.debug_verify_email", email=user.email)
                flash(
                    f"Please verify your email address before logging in. "
                    f"Check your inbox for the verification link. "
                    f'<a href="{verification_url}" class="alert-link">Click here to bypass verification</a> (DEV MODE ONLY)',
                    "warning",
                )
            else:
                flash(
                    "Please verify your email address before logging in. "
                    "Check your inbox for the verification link.",
                    "warning",
                )
            return render_template("auth/login.html", form=form)

        user.track_login_attempt(successful=True)
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")
        if not next_page or not next_page.startswith("/"):
            if user.is_admin:
                next_page = url_for("admin.dashboard") 
            else:
                next_page = url_for("main.index")  

        return redirect(next_page)

    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    """User logout endpoint."""
    logout_user()
    session.clear()  
    flash("You have been logged out successfully", "info")
    return redirect(url_for("auth.login"))


@auth.route("/profile", methods=["GET"])
@login_required
def profile():
    """User profile page."""
    return render_template("user/profile.html")


@auth.route("/update-profile", methods=["POST"])
@login_required
def update_profile():
    """Update user profile information."""
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    phone_number = request.form.get("phone_number")

    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.phone_number = phone_number

    try:
        db.session.commit()
        flash("Profile updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", "danger")

    return redirect(url_for("auth.profile"))


@auth.route("/change-password", methods=["POST"])
@login_required
def change_password():
    """Change user password."""
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if new_password != confirm_password:
        flash("New passwords do not match", "danger")
        return redirect(url_for("auth.profile"))

    try:
        current_user.set_password(new_password)
        db.session.commit()
        flash("Password changed successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", "danger")

    return redirect(url_for("auth.profile"))


# Debugging route for development use only
@auth.route("/test")
def test_page():
    """A simple test page to confirm the application is running."""
    return render_template("auth/login.html", form=LoginForm())