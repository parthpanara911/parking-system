from flask import Flask, Blueprint, redirect, url_for, render_template
from flask_login import login_required, current_user
from config.settings import Config
from app.extensions import db, migrate, login_manager, mail, csrf, cors
from datetime import datetime
import os


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD')
    app.config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

    app.config['DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
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

    from app.auth.routes import auth

    app.register_blueprint(auth)

    from app.parking.routes import parking, seed_parking_locations, seed_parking_slots

    app.register_blueprint(parking)

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

    app.register_blueprint(main)

    from app.utils.error_handlers import register_error_handlers

    register_error_handlers(app)
        
    # Add template context processors
    @app.context_processor
    def utility_processor():
        return {"now": datetime.now}

    with app.app_context():
        from app.models.user import User

        # Create database tables if they don't exist
        try:
            db.create_all()

            admin_email = app.config.get("ADMIN_EMAIL", "admin@example.com")
            admin_password = app.config.get("ADMIN_PASSWORD", "default-fallback-password")

            admin_user = User.query.filter_by(email=admin_email).first()

            if not admin_user:
                admin = User(
                    email=admin_email,
                    username="admin",
                    is_admin=True,
                    first_name="Admin",
                    last_name="User",
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                app.logger.info("Created default admin user")
            else:
                admin_user.set_password(admin_password)
                db.session.commit()
                app.logger.info("Updated admin password")

            # Seed parking locations if needed
            seed_parking_locations()

            # Seed parking slots if needed
            seed_parking_slots()

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating database tables: {str(e)}")

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        return {"db": db, "app": app}

    return app