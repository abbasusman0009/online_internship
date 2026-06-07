from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, StudentProfile, EmployerProfile

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role == 'employer':
                return redirect(url_for('employer.dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password_hash=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        if role == 'student':
            first_name = request.form.get('first_name', '')
            last_name = request.form.get('last_name', '')
            student_profile = StudentProfile(user_id=new_user.id, first_name=first_name, last_name=last_name)
            db.session.add(student_profile)
        elif role == 'employer':
            company_name = request.form.get('company_name', '')
            employer_profile = EmployerProfile(user_id=new_user.id, company_name=company_name)
            db.session.add(employer_profile)

        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
