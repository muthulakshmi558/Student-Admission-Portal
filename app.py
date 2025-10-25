# app.py
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from config import Config
from models.models import db, Student, Admin
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from utils.notifications import notify_student
from datetime import datetime
from functools import wraps
import os, webbrowser

# ------------------------------------------------------------
# App Initialization
# ------------------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)

# Database + Mail
db.init_app(app)
mail = Mail(app)

# Twilio Config
twilio_cfg = {
    "TWILIO_ACCOUNT_SID": app.config.get('TWILIO_ACCOUNT_SID'),
    "TWILIO_AUTH_TOKEN": app.config.get('TWILIO_AUTH_TOKEN'),
    "TWILIO_PHONE_NUMBER": app.config.get('TWILIO_PHONE_NUMBER')
}

# ------------------------------------------------------------
# Database setup & default admin creation
# ------------------------------------------------------------
with app.app_context():
    db.create_all()
    if not Admin.query.first():
        admin = Admin(username='admin', password=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()
        app.logger.info("✅ Default admin created (username: admin, password: admin123)")

# ------------------------------------------------------------
# Utility: Admin Login Required Decorator
# ------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash("Please login to access dashboard.", "warning")
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------

# Home Page
@app.route('/')
def index():
    return render_template('index.html', title="Student Admission Portal")

# Student Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            full_name = request.form['full_name']
            email = request.form['email']
            phone = request.form.get('phone')
            dob = request.form['dob']
            address = request.form.get('address', '')
            course = request.form['course']

            student = Student(
                full_name=full_name,
                email=email,
                phone=phone,
                dob=dob,
                address=address,
                course=course
            )
            db.session.add(student)
            db.session.commit()

            # Notify student via Email & SMS
            subject = "🎓 Application Received - Thank you!"
            html_body = render_template('email_templates/application_received.html', student=student)
            sms_body = f"Hello {student.full_name}, we received your application for {student.course}. Status: Pending."

            notify_student(app, mail, twilio_cfg, student, subject, html_body, sms_body)

            flash("✅ Application submitted successfully!", "success")
            return redirect(url_for('index'))

        except Exception as e:
            app.logger.error(f"Error during registration: {e}")
            flash("❌ Something went wrong! Please try again later.", "danger")

    return render_template('register.html', title="Register")

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_logged_in'] = True
            session['admin_username'] = admin.username
            flash("🎉 Welcome back, Admin!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("❌ Invalid username or password", "danger")

    return render_template('login.html', title="Admin Login")

# Admin Logout
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash("🔒 Logged out successfully.", "info")
    return redirect(url_for('admin_login'))

# Admin Dashboard
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    students = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('admin_dashboard.html', students=students, title="Dashboard")

# Change Student Status (Approve / Reject)
@app.route('/admin/api/student/<int:student_id>/status', methods=['POST'])
@login_required
def change_student_status(student_id):
    data = request.get_json() or {}
    new_status = data.get('status')

    if new_status not in ('Approved', 'Rejected'):
        return jsonify({"success": False, "message": "Invalid status"}), 400

    student = Student.query.get_or_404(student_id)
    student.status = new_status
    student.updated_at = datetime.utcnow()
    db.session.commit()

    # Notify Student
    subject = f"Application {new_status}"
    if new_status == 'Approved':
        html_body = render_template('email_templates/application_approved.html', student=student)
        sms_body = f"🎉 Congratulations {student.full_name}! Your application for {student.course} is APPROVED."
    else:
        html_body = render_template('email_templates/application_rejected.html', student=student)
        sms_body = f"⚠️ Hello {student.full_name}, we regret to inform you that your application for {student.course} was not approved."

    try:
        notify_student(app, mail, twilio_cfg, student, subject, html_body, sms_body)
    except Exception as e:
        app.logger.error(f"Notification failed: {e}")

    return jsonify({"success": True, "new_status": new_status})

# Dashboard Stats API (for charts)
@app.route('/admin/api/stats')
@login_required
def admin_stats():
    students = Student.query.all()
    counts = {
        "Pending": sum(1 for s in students if s.status == 'Pending'),
        "Approved": sum(1 for s in students if s.status == 'Approved'),
        "Rejected": sum(1 for s in students if s.status == 'Rejected'),
    }
    course_counts = {}
    for s in students:
        course_counts[s.course] = course_counts.get(s.course, 0) + 1

    return jsonify({"counts": counts, "course_counts": course_counts})

# ------------------------------------------------------------
# Run App
# ------------------------------------------------------------
if __name__ == '__main__':
    url = "http://127.0.0.1:5000"
    print(f"🚀 Server running at {url}")
    webbrowser.open(url)
    app.run(debug=True)
