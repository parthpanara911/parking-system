from flask import Flask, Blueprint, redirect, url_for, render_template
from flask_login import login_required, current_user
from config.settings import Config
from app.extensions import db, migrate, login_manager, mail, csrf, cors
from datetime import datetime


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    cors.init_app(app)

    # Configure login
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    login_manager.login_message = "Please log in to access this page."

    # Register auth blueprint
    from app.auth.routes import auth

    app.register_blueprint(auth)

    # Register parking blueprint
    from app.parking.routes import parking, seed_parking_locations, seed_parking_slots

    app.register_blueprint(parking)

    # Register admin blueprint
    from app.admin.routes import admin

    app.register_blueprint(admin)

    # Create main blueprint for basic routes
    from flask import Blueprint

    main = Blueprint("main", __name__)

    @main.route("/")
    def index():
        if current_user.is_authenticated:
            return render_template("index.html")
        else:
            return redirect(url_for("auth.login"))

    @main.route("/profile")
    @login_required
    def profile():
        """User profile page."""
        return render_template("profile.html")

    app.register_blueprint(main)

    # Register error handlers
    from app.utils.error_handlers import register_error_handlers

    register_error_handlers(app)

    # Add template context processors
    @app.context_processor
    def utility_processor():
        return {"now": datetime.now}

    # Import models to ensure they're registered with SQLAlchemy
    with app.app_context():
        # Import models here to avoid circular imports
        from app.models.user import User
        from app.models.parking_location import ParkingLocation
        from app.models.parking_slot import ParkingSlot

        # Create database tables if they don't exist
        try:
            db.create_all()

            # Create admin user if needed
            if not User.query.filter_by(
                email=app.config.get("ADMIN_EMAIL", "admin@example.com")
            ).first():
                try:
                    admin = User(
                        email=app.config.get("ADMIN_EMAIL", "admin@example.com"),
                        username="admin",
                        is_admin=True,
                        first_name="Admin",
                        last_name="User",
                    )
                    admin.set_password(
                        "admin"
                    )  # Default password, should be changed immediately
                    db.session.add(admin)
                    db.session.commit()
                    app.logger.info("Created default admin user")
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Error creating admin user: {str(e)}")

            # Seed parking locations if needed
            seed_parking_locations()

            # Seed parking slots if needed
            seed_parking_slots()

        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        return {"db": db, "app": app}

    return app
