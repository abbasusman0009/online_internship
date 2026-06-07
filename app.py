from flask import Flask, redirect, url_for, render_template
from models import db, User
from flask_login import LoginManager
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here_for_development'
    # Ensure the database is created in the instance folder or relative path
    import os

    # Use Render's PostgreSQL database if available, otherwise use local SQLite
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///oims.db')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from routes.student import student as student_blueprint
    app.register_blueprint(student_blueprint, url_prefix='/student')

    from routes.employer import employer as employer_blueprint
    app.register_blueprint(employer_blueprint, url_prefix='/employer')

    from routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    @app.route('/')
    def index():
        return render_template('index.html')

    with app.app_context():
        db.create_all()
        
        # Ensure admin user exists (useful for Render deployment)
        admin_email = 'admin@oims.com'
        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash('admin123')
            new_admin = User(email=admin_email, password_hash=hashed_password, role='admin')
            db.session.add(new_admin)
            db.session.commit()
            print(f"Admin user automatically created: {admin_email} / admin123")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
