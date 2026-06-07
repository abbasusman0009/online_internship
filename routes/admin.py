from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, User, EmployerProfile, StudentProfile, Internship, Application

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    users = User.query.all()
    internships = Internship.query.all()
    applications = Application.query.all()
    
    # Calculate stats for chart
    roles_count = {'student': 0, 'employer': 0, 'admin': 0}
    for u in users:
        roles_count[u.role] = roles_count.get(u.role, 0) + 1
        
    app_status_count = {'Submitted': 0, 'Under Review': 0, 'Accepted': 0, 'Rejected': 0}
    for a in applications:
        app_status_count[a.status] = app_status_count.get(a.status, 0) + 1
    
    return render_template('admin/dashboard.html', users=users, internships=internships, applications=applications, roles_count=roles_count, app_status_count=app_status_count)

import csv
import io
from flask import send_file

@admin.route('/export_applications')
@login_required
def export_applications():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
        
    applications = Application.query.all()
    
    # Create CSV in memory
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Application ID', 'Student Name', 'Internship Title', 'Company', 'Status', 'Submission Date'])
    
    for app in applications:
        cw.writerow([
            app.id,
            f"{app.student.first_name} {app.student.last_name}",
            app.internship.title,
            app.internship.employer.company_name,
            app.status,
            app.submission_date.strftime('%Y-%m-%d %H:%M')
        ])
        
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='applications_report.csv')

@admin.route('/employers')
@login_required
def employers():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    employers = EmployerProfile.query.all()
    return render_template('admin/employers.html', employers=employers)

@admin.route('/employer/delete/<int:employer_id>', methods=['POST'])
@login_required
def delete_employer(employer_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    employer = EmployerProfile.query.get_or_404(employer_id)
    user = User.query.get(employer.user_id)
    
    # SQLAlchemy ORM will handle cascading deletes for internships if configured correctly
    db.session.delete(employer)
    db.session.delete(user)
    db.session.commit()
    
    flash('Employer and their postings have been deleted.', 'success')
    return redirect(url_for('admin.employers'))

@admin.route('/students')
@login_required
def students():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    students_pagination = StudentProfile.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/students.html', students=students_pagination.items, pagination=students_pagination)

@admin.route('/student/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    student = StudentProfile.query.get_or_404(student_id)
    user = User.query.get(student.user_id)
    
    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()
    
    flash('Student and their applications have been deleted.', 'success')
    return redirect(url_for('admin.students'))

@admin.route('/internships')
@login_required
def internships():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    all_internships = Internship.query.all()
    return render_template('admin/internships.html', internships=all_internships)

@admin.route('/internship/delete/<int:internship_id>', methods=['POST'])
@login_required
def delete_internship(internship_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    internship = Internship.query.get_or_404(internship_id)
    db.session.delete(internship)
    db.session.commit()
    
    flash('Internship deleted successfully.', 'success')
    return redirect(url_for('admin.internships'))

