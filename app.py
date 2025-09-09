# Change Password Route (Student Only)
from flask import Flask, render_template, request, redirect, url_for, flash, session,send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from config import config
import pandas as pd
import io
from datetime import datetime

app = Flask(__name__)
# Student dashboard features: Saved Jobs, Job Alerts, Career Insights

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}
# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
if config_name not in config:
    config_name = 'development'  # Fallback to development
app.config.from_object(config[config_name])

db = SQLAlchemy(app)
migrate=Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Model for saved jobs
class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'job_id', name='unique_user_job'),)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='jobseeker')
    profile_complete = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(200))
    bio = db.Column(db.Text)
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)
    education = db.Column(db.Text)
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    remote = db.Column(db.Boolean, default=False)
    salary = db.Column(db.String(100))
    tags = db.Column(db.Text)
    urgent = db.Column(db.Boolean, default=False)
    logo = db.Column(db.String(200))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    benefits = db.Column(db.Text)
    category = db.Column(db.String(100))
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    employer_email = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='active')
    applications_count = db.Column(db.Integer, default=0)
    application_deadline = db.Column(db.DateTime)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Job relationship
    job_id = db.Column(db.Integer, db.ForeignKey('job.id', name='fk_application_job'), nullable=False)
    job = db.relationship('Job', backref='applications')

    job_title = db.Column(db.String(200), nullable=False)

    # Applicant (job seeker)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), name='fk_application_applicant', nullable=False)
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref='applications_as_applicant')
    applicant_name = db.Column(db.String(200), nullable=False)
    applicant_email = db.Column(db.String(200), nullable=False)

    # Employer (job poster)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), name='fk_application_employer', nullable=False)
    employer = db.relationship('User', foreign_keys=[employer_id], backref='applications_as_employer')

    # Optional generic user_id (you probably don’t need this if applicant_id/employer_id are clear)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=[user_id], backref='applications_as_user')

    resume = db.Column(db.String(200))
    drive_link = db.Column(db.String(500))  # Google Drive link ✅
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(20), default='new')  # new, reviewing, shortlisted, rejected, hired
    notes = db.Column(db.Text)  # Employer notes about the application
    rating = db.Column(db.Integer)  # 1-5 rating
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, default=60)  # Duration in minutes
    interview_type = db.Column(db.String(50), default='video')  # video, phone, onsite
    location = db.Column(db.String(200))  # For onsite interviews
    meeting_link = db.Column(db.String(500))  # For video interviews
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled, rescheduled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships for template access
    job = db.relationship('Job', backref='interviews', lazy=True)
    applicant = db.relationship('User', foreign_keys=[applicant_id], backref='interviews_as_applicant', lazy=True)


class ApplicationAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    total_applications = db.Column(db.Integer, default=0)
    applications_today = db.Column(db.Integer, default=0)
    applications_this_week = db.Column(db.Integer, default=0)
    applications_this_month = db.Column(db.Integer, default=0)
    shortlisted_count = db.Column(db.Integer, default=0)
    interview_count = db.Column(db.Integer, default=0)
    hired_count = db.Column(db.Integer, default=0)
    rejected_count = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Model for job alerts
class JobAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    keywords = db.Column(db.String(200))
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    # Link to the User model
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Field for admin approval
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='posts')

@login_manager.user_loader
def load_user(user_id):
    if str(user_id) == "0":
        class AdminUser:
            is_authenticated = True
            is_active = True
            is_anonymous = False
            id = 0
            email = 'manju@branchlogic.com'
            role = 'admin'
            first_name = 'Admin'
            last_name = 'User'
            display_name = 'Admin User'

            def get_id(self):
                return str(self.id)
        return AdminUser()
    return User.query.get(int(user_id))

def format_count(n):
    if n >= 1000:
        return f"{n//1000}K+"
    return str(n)
# Routes
@app.route('/')
def home():
    job_count = Job.query.count()  
    featured_jobs = Job.query.filter_by(status='active').order_by(Job.created_at.desc()).limit(6).all()
    
    # Get job categories for the homepage
    categories = db.session.query(Job.category).filter(Job.category.isnot(None)).distinct().limit(8).all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    # Get some stats
    total_jobs = Job.query.filter_by(status='active').count()
    total_companies = db.session.query(Job.company).distinct().count()
    
    return render_template('index.html', 
                        job_count=job_count,
                         featured_jobs=featured_jobs, 
                         categories=categories,
                         total_jobs=total_jobs,
                         total_companies=total_companies)

@app.route('/jobs')
def jobs():
    search_query = request.args.get('q', '')
    location = request.args.get('location', '')
    remote = request.args.get('remote', '')
    category = request.args.get('category', '')
    job_type = request.args.get('job_type', '')
    
    jobs_query = Job.query.filter_by(status='active')
    
    if search_query:
        jobs_query = jobs_query.filter(Job.title.contains(search_query) | Job.company.contains(search_query))
    if location:
        jobs_query = jobs_query.filter(Job.location.contains(location))
    if remote:
        jobs_query = jobs_query.filter_by(remote=True)
    if category:
        jobs_query = jobs_query.filter_by(category=category)
    if job_type:
        jobs_query = jobs_query.filter_by(job_type=job_type)
    
    jobs = jobs_query.order_by(Job.created_at.desc()).all()
    
    # Get categories for filter dropdown
    categories = db.session.query(Job.category).filter(Job.category.isnot(None)).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('jobs.html', 
                         jobs=jobs, 
                         search_query=search_query, 
                         location=location, 
                         remote=remote, 
                         category=category,
                         job_type=job_type,
                         categories=categories)

@app.route('/search')
def search():
    # Redirect homepage search to jobs page with parameters
    return redirect(url_for('jobs', **request.args))

@app.route('/jobs/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    related_jobs = Job.query.filter_by(category=job.category).filter(Job.id != job_id).limit(3).all()
    already_applied = False
    if current_user.is_authenticated:
        already_applied = Application.query.filter_by(job_id=job_id, applicant_id=current_user.id).first() is not None
    return render_template('job_detail.html', job=job, related_jobs=related_jobs, already_applied=already_applied)

@app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)

    # Prevent duplicate applications
    already_applied = Application.query.filter_by(job_id=job_id, applicant_id=current_user.id).first()
    if already_applied:
        flash('You have already applied for this job.', 'info')
        return redirect(url_for('job_detail', job_id=job_id))

    if request.method == 'POST':
        try:
            resume = request.files.get('resume')
            drive_link = request.form.get('drive_link')
            cover_letter = request.form.get('cover_letter')
            print(f"[DEBUG] Received POST: resume={resume}, drive link={drive_link}, cover_letter={cover_letter}")

            # Handle resume upload
            resume_filename = None
            if resume and resume.filename:
                resume_filename = f"resume_{current_user.id}_{job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(resume.filename)[1]}"
                resume.save(os.path.join('uploads', resume_filename))
                print(f"[DEBUG] Resume saved as {resume_filename}")
            else:
                print("[DEBUG] No resume uploaded or filename is empty.")

            # ✅ Create Application AFTER resume is processed
            application = Application(
                job_id=job_id,
                job_title=job.title,
                applicant_id=current_user.id,
                applicant_name=f"{current_user.first_name} {current_user.last_name}",
                applicant_email=current_user.email,
                employer_id=job.employer_id,
                resume=resume_filename,   # <- Use saved filename or None
                drive_link=drive_link,
                cover_letter=cover_letter,
                status='new'
            )

            db.session.add(application)
            job.applications_count += 1
            db.session.commit()

            flash('Application submitted successfully!', 'success')
            print("[DEBUG] Application committed to DB.")
            return redirect(url_for('job_detail', job_id=job_id))

        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Application submission failed: {e}")
            flash(f'Application submission failed: {e}', 'error')

    return render_template('apply_job.html', job=job)

@app.route('/dashboard')
@login_required
def dashboard():
    # 1. Redirect admin users to the new admin dashboard
    if current_user.role == 'admin':
        jobs = Job.query.all() 
        return redirect(url_for('admin_dashboard',jobs=jobs))

    # 3. Handle jobseeker users (as before)
    else:
        applications = Application.query.filter_by(applicant_id=current_user.id).all()
        return render_template('dashboard.html', applications=applications)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Ensure only admins can access this page
    if current_user.role != 'admin':
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('home'))

    # Fetch site-wide statistics
    stats = {
        'total_users': User.query.count(),
        'total_jobs': Job.query.count(),
        'total_applications': Application.query.count(),
        'total_interviews': Interview.query.count(),
        'jobs_posted_today': Job.query.filter(db.func.date(Job.created_at) == datetime.utcnow().date()).count(),
        'applications_today': Application.query.filter(db.func.date(Application.applied_at) == datetime.utcnow().date()).count(),
        'interviews_scheduled_today': Interview.query.filter(db.func.date(Interview.scheduled_at) == datetime.utcnow().date()).count(),
        'active_jobs': Job.query.filter_by(status='active').count(),
        'inactive_jobs': Job.query.filter_by(status='inactive').count(),
        'pending_applications': Application.query.filter_by(status='new').count(),
        'shortlisted_applications': Application.query.filter_by(status='shortlisted').count(),
        'hired_applications': Application.query.filter_by(status='hired').count(),
        'rejected_applications': Application.query.filter_by(status='rejected').count(),
        'completed_interviews': Interview.query.filter_by(status='completed').count(),
        'upcoming_interviews': Interview.query.filter(Interview.status=='scheduled', Interview.scheduled_at >= datetime.utcnow()).count(),
        'cancelled_interviews': Interview.query.filter_by(status='cancelled').count(),
        'rescheduled_interviews': Interview.query.filter_by(status='rescheduled').count()
    }

    # Fetch recent activity
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()


    return render_template('admin_dashboard.html', 
                           stats=stats,
                           recent_jobs=recent_jobs,
                           recent_users=recent_users)

@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role not in ['admin']:
        flash('Only employers and admins can post jobs', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        job = Job(
            title=request.form['title'],
            company=request.form['company'],
            location=request.form['location'],
            job_type=request.form['job_type'],
            remote=bool(request.form.get('remote')),
            salary=request.form['salary'],
            tags=request.form['tags'],
            urgent=bool(request.form.get('urgent')),
            description=request.form['description'],
            requirements=request.form['requirements'],
            benefits=request.form['benefits'],
            category=request.form['category'],
            employer_id=current_user.id,
            employer_email=current_user.email
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('post_job.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Hardcoded admin credentials
        ADMIN_EMAIL = 'manju@branchlogic.com'
        ADMIN_PASSWORD = 'manju123'
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            # Create a fake admin user object for session
            class AdminUser:
                is_authenticated = True
                is_active = True
                is_anonymous = False
                id = 0
                email = ADMIN_EMAIL
                role = 'admin'
                first_name = 'Admin'
                last_name = 'User'
                display_name = 'Admin User'

                def get_id(self):
                    return str(self.id)
            admin_user = AdminUser()
            login_user(admin_user)
            return redirect(url_for('admin_dashboard'))
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')

# In app.py, replace your existing signup function

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = 'jobseeker' # Only allow jobseeker role for signup
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            display_name=f"{first_name} {last_name}",
            role=role,
            profile_complete=False # Profile starts as incomplete
        )
        db.session.add(user)
        db.session.commit()

        # --- KEY CHANGES ARE HERE ---
        # 1. Log the new user in automatically
        login_user(user) 
        
        # 2. Flash a new message and redirect to the profile page
        flash('Registration successful! Please complete your profile to get started.', 'success')
        return redirect(url_for('profile')) 

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# In app.py, replace your existing profile function

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Check if the profile was incomplete before this update
        was_profile_incomplete = not current_user.profile_complete

        # Update user details from the form
        current_user.first_name = request.form['first_name']
        current_user.last_name = request.form['last_name']
        current_user.bio = request.form['bio']
        current_user.skills = request.form['skills']
        current_user.experience = request.form['experience']
        current_user.education = request.form['education']
        current_user.location = request.form['location']
        current_user.website = request.form['website']
        current_user.linkedin = request.form['linkedin']
        current_user.github = request.form['github']
        
        # Mark the profile as complete
        current_user.profile_complete = True
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')

        # --- KEY CHANGE IS HERE ---
        # If this was their first time, redirect to the homepage
        if was_profile_incomplete:
            return redirect(url_for('home'))
        # Otherwise, redirect back to the profile page
        else:
            return redirect(url_for('profile'))
    
    return render_template('profile.html')

# Application Management Routes
@app.route('/applications')
@login_required
def applications():
    if current_user.role in ['employer', 'admin']:
        # Employer/Admin view: see all applications for their jobs
        applications = Application.query.join(Job).filter(Job.employer_id == current_user.id).order_by(Application.applied_at.desc()).all()
        return render_template('employer_applications.html', applications=applications)
    else:
        # Job seeker view: see their own applications
        applications = Application.query.filter_by(applicant_id=current_user.id).order_by(Application.applied_at.desc()).all()
        return render_template('applications.html', applications=applications)

@app.route('/admin/job/<int:job_id>')
@login_required
def admin_view_job(job_id):
    if current_user.role != 'admin':   # assuming you store roles
        return redirect(url_for('dashboard'))  # prevent normal users

    job = Job.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_id=job_id).all()

    return render_template('admin_view_job.html', job=job, applications=applications)

@app.route('/admin/job/<int:job_id>/applications')
@login_required
def admin_view_applications(job_id):
    # Ensure only admins can access
    if current_user.role != 'admin':
        flash("Access denied: Admins only", "danger")
        return redirect(url_for('home'))

    job = Job.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_id=job.id).all()

    return render_template(
        'admin_view_applications.html',
        job=job,
        applications=applications
    )

# In app.py, replace the old admin_view_application function

# In app.py, replace the old admin_view_application function

@app.route('/admin/application/<int:application_id>', methods=['GET', 'POST'])
@login_required
def admin_view_application(application_id):
    if current_user.role != 'admin':
        flash("Access denied: Admins only", "danger")
        return redirect(url_for('home'))

    application = Application.query.get_or_404(application_id)
    existing_interviews = Interview.query.filter_by(application_id=application.id).order_by(Interview.scheduled_at.desc()).all()

    if request.method == 'POST':
        # Check which form was submitted
        form_type = request.form.get('form_type')

        # --- Logic for the "Update Status" form ---
        if form_type == 'update_status':
            try:
                application.status = request.form.get('status')
                application.notes = request.form.get('notes')
                application.rating = request.form.get('rating')
                db.session.commit()
                flash("Application status updated successfully!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error updating status: {e}", "danger")

        # --- Logic for the "Schedule Interview" form ---
        elif form_type == 'schedule_interview':
            try:
                scheduled_at = datetime.strptime(request.form['scheduled_at'], '%Y-%m-%dT%H:%M')
                interview = Interview(
                    application_id=application.id,
                    job_id=application.job_id,
                    applicant_id=application.applicant_id,
                    employer_id=application.employer_id,
                    scheduled_at=scheduled_at,
                    duration=int(request.form['duration']),
                    interview_type=request.form['interview_type'],
                    meeting_link=request.form.get('meeting_link', ''),
                    location=request.form.get('location', ''),
                    notes=request.form.get('notes_for_applicant', '')
                )
                application.status = 'shortlisted'
                db.session.add(interview)
                db.session.commit()
                flash("Interview scheduled successfully!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error scheduling interview: {e}", "danger")
        
        return redirect(url_for('admin_view_application', application_id=application.id))

    # Calculate min datetime for the scheduling form
    from datetime import timedelta
    min_dt = datetime.utcnow() + timedelta(hours=1)
    min_dt_str = min_dt.strftime('%Y-%m-%dT%H:%M')

    return render_template('admin_view_application.html', 
                           application=application, 
                           interviews=existing_interviews,
                           min_dt_str=min_dt_str)


@app.route('/application/<int:application_id>/update', methods=['POST'])
@login_required
def update_application_status(application_id):
    if current_user.role not in ['employer', 'admin']:
        flash('Access denied', 'error')
        return redirect(url_for('applications'))
    
    application = Application.query.get_or_404(application_id)
    if application.employer_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('applications'))
    
    status = request.form['status']
    notes = request.form.get('notes', '')
    rating = request.form.get('rating')
    
    application.status = status
    application.notes = notes
    if rating:
        application.rating = int(rating)
    
    db.session.commit()
    flash('Application status updated successfully!', 'success')
    return redirect(url_for('view_application', application_id=application_id))

# Interview Management Routes
# In app.py, replace the old schedule_interview function with this one

@app.route('/schedule_interview/<int:application_id>', methods=['GET', 'POST'])
@login_required
def schedule_interview(application_id):
    application = Application.query.get_or_404(application_id)

    # --- FIX 1: Corrected Permission Check ---
    # Admins can schedule for anyone. Employers can only schedule for their own jobs.
    if current_user.role != 'admin' and application.employer_id != current_user.id:
        flash('You do not have permission to schedule this interview.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        scheduled_at = datetime.strptime(request.form['scheduled_at'], '%Y-%m-%dT%H:%M')
        duration = int(request.form['duration'])
        interview_type = request.form['interview_type']
        location = request.form.get('location', '')
        meeting_link = request.form.get('meeting_link', '')
        notes = request.form.get('notes', '')
        
        interview = Interview(
            application_id=application_id,
            job_id=application.job_id,
            applicant_id=application.applicant_id,
            # --- FIX 2: Assign the correct employer ID ---
            employer_id=application.employer_id, # Assigns the job's actual employer, not the admin
            scheduled_at=scheduled_at,
            duration=duration,
            interview_type=interview_type,
            location=location,
            meeting_link=meeting_link,
            notes=notes
        )
        
        application.status = 'shortlisted'
        db.session.add(interview)
        db.session.commit()
        
        flash('Interview scheduled successfully!', 'success')
        # Redirect admin to the application they just updated
        if current_user.role == 'admin':
            return redirect(url_for('admin_view_application', application_id=application_id))
        else:
            return redirect(url_for('view_application', application_id=application_id))
    
    from datetime import timedelta
    min_dt = datetime.utcnow() + timedelta(hours=1)
    min_dt_str = min_dt.strftime('%Y-%m-%dT%H:%M')
    return render_template('schedule_interview.html', application=application, min_dt_str=min_dt_str)
@app.route('/interviews')
@login_required
def interviews():
    if current_user.role in ['employer', 'admin']:
        interviews = Interview.query.filter_by(employer_id=current_user.id).order_by(Interview.scheduled_at.desc()).all()
    else:
        interviews = Interview.query.filter_by(applicant_id=current_user.id).order_by(Interview.scheduled_at.desc()).all()
    
    return render_template('interviews.html', interviews=interviews)

@app.route('/interview/<int:interview_id>/update', methods=['POST'])
@login_required
def update_interview_status(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Check permissions
    if current_user.role in ['employer', 'admin'] and interview.employer_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('interviews'))
    elif current_user.role == 'jobseeker' and interview.applicant_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('interviews'))
    
    status = request.form['status']
    notes = request.form.get('notes', '')
    
    interview.status = status
    interview.notes = notes
    
    db.session.commit()
    flash('Interview status updated successfully!', 'success')
    return redirect(url_for('interviews'))

# Analytics Routes
@app.route('/analytics')
@login_required
def analytics():
    if current_user.role not in ['employer', 'admin']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # Get analytics for all jobs posted by the employer
    jobs = Job.query.filter_by(employer_id=current_user.id).all()
    
    analytics_data = {
        'total_jobs': len(jobs),
        'total_applications': 0,
        'applications_today': 0,
        'applications_this_week': 0,
        'applications_this_month': 0,
        'shortlisted_count': 0,
        'interview_count': 0,
        'hired_count': 0,
        'rejected_count': 0,
        'average_rating': 0.0,
        'job_stats': []
    }
    
    from datetime import datetime, timedelta
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    for job in jobs:
        job_applications = Application.query.filter_by(job_id=job.id).all()
        total_apps = len(job_applications)
        
        # Count applications by time period
        today_apps = sum(1 for app in job_applications if app.applied_at.date() == today)
        week_apps = sum(1 for app in job_applications if app.applied_at.date() >= week_ago)
        month_apps = sum(1 for app in job_applications if app.applied_at.date() >= month_ago)
        
        # Count by status
        shortlisted = sum(1 for app in job_applications if app.status == 'shortlisted')
        interviews = sum(1 for app in job_applications if app.status == 'shortlisted')
        hired = sum(1 for app in job_applications if app.status == 'hired')
        rejected = sum(1 for app in job_applications if app.status == 'rejected')
        
        # Calculate average rating
        ratings = [app.rating for app in job_applications if app.rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        job_stats = {
            'job_title': job.title,
            'company': job.company,
            'total_applications': total_apps,
            'applications_today': today_apps,
            'applications_this_week': week_apps,
            'applications_this_month': month_apps,
            'shortlisted_count': shortlisted,
            'interview_count': interviews,
            'hired_count': hired,
            'rejected_count': rejected,
            'average_rating': round(avg_rating, 1)
        }
        
        analytics_data['job_stats'].append(job_stats)
        analytics_data['total_applications'] += total_apps
        analytics_data['applications_today'] += today_apps
        analytics_data['applications_this_week'] += week_apps
        analytics_data['applications_this_month'] += month_apps
        analytics_data['shortlisted_count'] += shortlisted
        analytics_data['interview_count'] += interviews
        analytics_data['hired_count'] += hired
        analytics_data['rejected_count'] += rejected
    
    # Calculate overall average rating
    all_ratings = [app.rating for app in Application.query.join(Job).filter(Job.employer_id == current_user.id) if app.rating]
    if all_ratings:
        analytics_data['average_rating'] = round(sum(all_ratings) / len(all_ratings), 1)
    
    # Precompute denominator for trend bar to avoid using 'max' in Jinja
    analytics_data['total_applications_or_1'] = max(analytics_data['total_applications'], 1)
    analytics_data['total_applications_or_1_week'] = max(analytics_data['total_applications'], 1)
    analytics_data['total_applications_or_1_month'] = max(analytics_data['total_applications'], 1)
    return render_template('analytics.html', analytics=analytics_data)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500



# Admin: Export student applications as Excel (all or for a specific job)
@app.route('/admin/export_applications')
@login_required
def export_applications():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    job_id = request.args.get('job_id', type=int)
    query = db.session.query(Application, User, Job).join(User, Application.applicant_id == User.id).join(Job, Application.job_id == Job.id)
    if job_id:
        query = query.filter(Application.job_id == job_id)
    applications = query.all()

    data = []
    for app, user, job in applications:
        data.append({
            'Application ID': app.id,
            'Student ID': user.id,
            'Student Name': f"{user.first_name} {user.last_name}",
            'Student Email': user.email,
            'Job Title': job.title,
            'Company': job.company,
            'Applied At': app.applied_at.strftime('%Y-%m-%d %H:%M'),
            'Resume Filename': app.resume or '',
            'Status': app.status,
            'Rating': app.rating or '',
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Applications')
    output.seek(0)

    if job_id:
        filename = f"applications_job_{job_id}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    else:
        filename = f"all_applications_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(output, download_name=filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# Serve uploaded resumes and files (must be after app is defined)
from flask import send_from_directory
@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    # Optionally, restrict access to only employers or admins
    if current_user.role not in ['employer', 'admin']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    return send_from_directory('uploads', filename, as_attachment=True)

# Student dashboard features: Saved Jobs, Job Alerts, Career Insights
@app.route('/saved_jobs')
@login_required
def saved_jobs():
    # Show jobs saved by the current user
    saved = SavedJob.query.filter_by(user_id=current_user.id).all()
    job_ids = [s.job_id for s in saved]
    jobs = Job.query.filter(Job.id.in_(job_ids)).all() if job_ids else []
    return render_template('saved_jobs.html', jobs=jobs)

# In app.py, replace the old job_alerts function with this one

from sqlalchemy import or_  # Make sure to add 'or_' to your imports at the top of the file!

@app.route('/job_alerts', methods=['GET', 'POST'])
@login_required
def job_alerts():
    alert = JobAlert.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        keywords = request.form.get('keywords', '').strip()
        location = request.form.get('location', '').strip()
        if alert:
            alert.keywords = keywords
            alert.location = location
        else:
            alert = JobAlert(user_id=current_user.id, keywords=keywords, location=location)
            db.session.add(alert)
        db.session.commit()
        flash('Job alert preferences updated!', 'success')
        return redirect(url_for('job_alerts'))

    # --- THE IMPROVED JOB MATCHING LOGIC IS HERE ---
    jobs = []
    if alert and (alert.keywords or alert.location):
        jobs_query = Job.query.filter_by(status='active')

        # More powerful keyword search
        if alert.keywords:
            search_term = f"%{alert.keywords}%"
            jobs_query = jobs_query.filter(or_(
                Job.title.ilike(search_term),
                Job.company.ilike(search_term),
                Job.tags.ilike(search_term),
                Job.description.ilike(search_term)
            ))
        
        # Location search (as before)
        if alert.location:
            jobs_query = jobs_query.filter(Job.location.ilike(f"%{alert.location}%"))
            
        jobs = jobs_query.order_by(Job.created_at.desc()).all()

    return render_template('job_alerts.html', alert=alert, jobs=jobs)



@app.route('/career_insights')
@login_required
def career_insights():
    from sqlalchemy import func

    # This function now correctly calculates trends from ALL jobs on the platform.
    # The incorrect filter for a non-existent 'admin' user has been removed.

    top_titles = (
        db.session.query(Job.title, func.count().label('count'))
        .group_by(Job.title)
        .order_by(func.count().desc())
        .limit(5)
        .all()
    )
    
    top_locations = (
        db.session.query(Job.location, func.count().label('count'))
        .group_by(Job.location)
        .order_by(func.count().desc())
        .limit(5)
        .all()
    )
    
    return render_template('career_insights.html', top_titles=top_titles, top_locations=top_locations)


# Route to save a job (POST)
@app.route('/save_job/<int:job_id>', methods=['POST'])
@login_required
def save_job(job_id):
    # Overwrite any existing saved job for this user/job
    existing = SavedJob.query.filter_by(user_id=current_user.id, job_id=job_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
    saved = SavedJob(user_id=current_user.id, job_id=job_id)
    db.session.add(saved)
    db.session.commit()
    flash('Job saved successfully!', 'success')
    return redirect(request.referrer or url_for('jobs'))

# Edit Job Route
@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    # Only allow employer/admin who owns the job
    if current_user.role not in ['admin'] or (current_user.role in ['admin'] and job.employer_id != current_user.id):
        flash('You do not have permission to edit this job.', 'error')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        job.title = request.form['title']
        job.company = request.form['company']
        job.location = request.form['location']
        job.job_type = request.form['job_type']
        job.salary = request.form['salary']
        job.tags = request.form['tags']
        job.description = request.form['description']
        job.requirements = request.form['requirements']
        job.benefits = request.form['benefits']
        job.category = request.form['category']
        db.session.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_job.html', job=job)

# Close Job Route
@app.route('/close_job/<int:job_id>', methods=['POST'])
@login_required
def close_job(job_id):
    job = Job.query.get_or_404(job_id)
    if current_user.role not in ['employer', 'admin'] or (current_user.role in ['employer', 'admin'] and job.employer_id != current_user.id):
        flash('You do not have permission to close this job.', 'error')
        return redirect(url_for('dashboard'))
    job.status = 'closed'
    db.session.commit()
    flash('Job closed successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if current_user.role != 'jobseeker':
        flash('Only students can change their password here.', 'error')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        current_pwd = request.form['current_password']
        new_pwd = request.form['new_password']
        confirm_pwd = request.form['confirm_password']
        if not check_password_hash(current_user.password_hash, current_pwd):
            flash('Current password is incorrect.', 'error')
            return render_template('change_password.html')
        if new_pwd != confirm_pwd:
            flash('New passwords do not match.', 'error')
            return render_template('change_password.html')
        if len(new_pwd) < 6:
            flash('New password must be at least 6 characters.', 'error')
            return render_template('change_password.html')
        current_user.password_hash = generate_password_hash(new_pwd)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('change_password.html')


     # Blog page route
@app.route('/blog')
def blog():
    got_job_at_branchlogic = False
    if current_user.is_authenticated:
        # Find if user has a 'hired' application for a BranchLogic job
        from sqlalchemy import or_
        hired_app = Application.query.join(Job, Application.job_id == Job.id) \
            .filter(Application.applicant_id == current_user.id) \
            .filter(Application.status == 'hired') \
            .filter(or_(Job.company.ilike('%branchlogic%'), Job.company.ilike('%branch logic%'))) \
            .first()
        if hired_app:
            got_job_at_branchlogic = True
    return render_template('blog.html', got_job_at_branchlogic=got_job_at_branchlogic)


# Add this new route to app.py

@app.route('/about')
def about_us():
    return render_template('about.html')
       # Add this new route to app.py

@app.route('/admin/applications')
@login_required
def admin_all_applications():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))

    # Fetch all applications from the database, ordered by the most recent
    applications = Application.query.order_by(Application.applied_at.desc()).all()
    return render_template('admin_all_applications.html', applications=applications)
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create uploads directory if it doesn't exist
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
    import os
    app.run(debug=False, host='0.0.0.0')

 







