import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db, StudentProfile, Internship, Application, Feedback

student = Blueprint('student', __name__)

@student.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        return redirect(url_for('index'))
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('student/dashboard.html', profile=profile)

@student.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'student':
        return redirect(url_for('index'))
    
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        profile.first_name = request.form.get('first_name')
        profile.last_name = request.form.get('last_name')
        profile.university = request.form.get('university')
        profile.major = request.form.get('major')
        profile.bio = request.form.get('bio')
        profile.skills = request.form.get('skills')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('student/profile.html', profile=profile)

@student.route('/internships')
@login_required
def internships():
    if current_user.role != 'student':
        return redirect(url_for('index'))
        
    query = Internship.query.filter_by(status='Open')
    
    search_q = request.args.get('q', '')
    location = request.args.get('location', '')
    
    if search_q:
        query = query.filter(Internship.title.ilike(f'%{search_q}%') | Internship.description.ilike(f'%{search_q}%'))
    if location:
        query = query.filter(Internship.location.ilike(f'%{location}%'))
        
    page = request.args.get('page', 1, type=int)
    internships_pagination = query.paginate(page=page, per_page=6, error_out=False)
    
    return render_template('student/internships.html', internships=internships_pagination.items, pagination=internships_pagination, q=search_q, location=location)

@student.route('/save_internship/<int:internship_id>', methods=['POST'])
@login_required
def save_internship(internship_id):
    if current_user.role != 'student':
        return redirect(url_for('index'))
    
    internship = Internship.query.get_or_404(internship_id)
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    if internship in profile.saved_internships:
        profile.saved_internships.remove(internship)
        flash('Internship removed from saved list.', 'info')
    else:
        profile.saved_internships.append(internship)
        flash('Internship saved successfully!', 'success')
        
    db.session.commit()
    return redirect(request.referrer or url_for('student.internships'))

@student.route('/apply/<int:internship_id>', methods=['GET', 'POST'])
@login_required
def apply(internship_id):
    if current_user.role != 'student':
        return redirect(url_for('index'))
    
    internship = Internship.query.get_or_404(internship_id)
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()

    # Check if already applied
    existing_application = Application.query.filter_by(student_id=profile.id, internship_id=internship_id).first()
    if existing_application:
        flash('You have already applied for this internship.', 'warning')
        return redirect(url_for('student.applications'))

    if request.method == 'POST':
        cover_letter = request.form.get('cover_letter')
        
        resume_filename = None
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                resume_filename = filename
                
        application = Application(student_id=profile.id, internship_id=internship.id, cover_letter=cover_letter, resume_filename=resume_filename)
        db.session.add(application)
        db.session.commit()
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('student.applications'))
    
    return render_template('student/apply.html', internship=internship)

@student.route('/applications')
@login_required
def applications():
    if current_user.role != 'student':
        return redirect(url_for('index'))
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    apps = Application.query.filter_by(student_id=profile.id).all()
    return render_template('student/applications.html', applications=apps)
