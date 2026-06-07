from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    admin_email = 'admin@oims.com'
    admin_user = User.query.filter_by(email=admin_email).first()
    
    if not admin_user:
        hashed_password = generate_password_hash('admin123')
        new_admin = User(email=admin_email, password_hash=hashed_password, role='admin')
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin user created: {admin_email} / admin123")
    else:
        print(f"Admin user already exists: {admin_email}")
