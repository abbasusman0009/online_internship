import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import db, EmployerProfile, Internship, Application, Feedback

employer = Blueprint('employer', __name__)

@employer.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'employer':
        return redirect(url_for('index'))
    profile = EmployerProfile.query.filter_by(user_id=current_user.id).first()
    
    app_status_count = {'Submitted': 0, 'Under Review': 0, 'Accepted': 0, 'Rejected': 0}
    for internship in profile.internships:
        for app in internship.applications:
            app_status_count[app.status] = app_status_count.get(app.status, 0) + 1
            
    return render_template('employer/dashboard.html', profile=profile, app_status_count=app_status_count)

@employer.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'employer':
        return redirect(url_for('index'))
    
    profile = EmployerProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        profile.company_name = request.form.get('company_name')
        profile.description = request.form.get('description')
        profile.website = request.form.get('website')
        
        db.session.commit()
        flash('Company profile updated successfully!', 'success')
        return redirect(url_for('employer.dashboard'))

    return render_template('employer/profile.html', profile=profile)

@employer.route('/post_internship', methods=['GET', 'POST'])
@login_required
def post_internship():
    if current_user.role != 'employer':
        return redirect(url_for('index'))
    
    profile = EmployerProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        duration = request.form.get('duration')
        skills_required = request.form.get('skills_required')
        
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                # To avoid collisions, you could append a timestamp or UUID
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        internship = Internship(employer_id=profile.id, title=title, description=description, 
                                location=location, duration=duration, skills_required=skills_required,
                                image_filename=image_filename)
        db.session.add(internship)
        db.session.commit()
        flash('Internship posted successfully!', 'success')
        return redirect(url_for('employer.dashboard'))

    return render_template('employer/post_internship.html')

@employer.route('/manage_internships')
@login_required
def manage_internships():
    if current_user.role != 'employer':
        return redirect(url_for('index'))
    profile = EmployerProfile.query.filter_by(user_id=current_user.id).first()
    internships = Internship.query.filter_by(employer_id=profile.id).all()
    return render_template('employer/manage_internships.html', internships=internships)

@employer.route('/applicants/<int:internship_id>')
@login_required
def applicants(internship_id):
    if current_user.role != 'employer':
        return redirect(url_for('index'))
    
    internship = Internship.query.get_or_404(internship_id)
    profile = EmployerProfile.query.filter_by(user_id=current_user.id).first()
    if internship.employer_id != profile.id:
        return redirect(url_for('employer.dashboard'))
        
    applications = Application.query.filter_by(internship_id=internship.id).all()
    return render_template('employer/applicants.html', internship=internship, applications=applications)

@employer.route('/update_status/<int:application_id>', methods=['POST'])
@login_required
def update_status(application_id):
    if current_user.role != 'employer':
        return redirect(url_for('index'))
        
    application = Application.query.get_or_404(application_id)
    status = request.form.get('status')
    application.status = status
    db.session.commit()
    flash(f'Application status updated to {status}', 'success')
    return redirect(url_for('employer.applicants', internship_id=application.internship_id))

@employer.route('/feedback/<int:application_id>', methods=['GET', 'POST'])
@login_required
def feedback(application_id):
    if current_user.role != 'employer':
        return redirect(url_for('index'))
        
    application = Application.query.get_or_404(application_id)
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comments = request.form.get('comments')
        
        fb = Feedback(application_id=application.id, rating=rating, comments=comments)
        db.session.add(fb)
        db.session.commit()
        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('employer.applicants', internship_id=application.internship_id))

    return render_template('employer/feedback.html', application=application)
