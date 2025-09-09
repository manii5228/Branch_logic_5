#!/usr/bin/env python3
"""
Database Population Script for BranchLogic
This script creates sample users, jobs, and applications for testing purposes.
"""

from app import app, db, User, Job, Application, Interview, ApplicationAnalytics
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_sample_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("Creating sample data...")
        
        # Create sample users
        users = []
        
        # Job seekers
        job_seekers = [
            {
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'jobseeker',
                'bio': 'Experienced software developer with 5+ years in web development. Passionate about creating user-friendly applications and solving complex problems.',
                'skills': 'Python, JavaScript, React, Node.js, SQL, Git',
                'experience': 'Senior Developer at TechCorp (2020-2023), Full-stack Developer at StartupXYZ (2018-2020)',
                'education': 'BS Computer Science, University of Technology (2018)',
                'location': 'San Francisco, CA',
                'website': 'https://johndoe.dev',
                'linkedin': 'https://linkedin.com/in/johndoe',
                'github': 'https://github.com/johndoe'
            },
            {
                'email': 'jane.smith@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': 'jobseeker',
                'bio': 'Creative product designer with expertise in user experience and interface design. Love working on products that make a difference.',
                'skills': 'Figma, Sketch, Adobe Creative Suite, User Research, Prototyping, Design Systems',
                'experience': 'Product Designer at Design Studio (2021-2023), UX Designer at Creative Agency (2019-2021)',
                'education': 'BA Design, Art Institute (2019)',
                'location': 'New York, NY',
                'website': 'https://janesmith.design',
                'linkedin': 'https://linkedin.com/in/janesmith',
                'github': 'https://github.com/janesmith'
            },
            {
                'email': 'mike.wilson@example.com',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'role': 'jobseeker',
                'bio': 'DevOps engineer passionate about automation and cloud infrastructure. Experience with AWS, Docker, and CI/CD pipelines.',
                'skills': 'AWS, Docker, Kubernetes, Terraform, Jenkins, Python, Bash',
                'experience': 'DevOps Engineer at CloudTech (2021-2023), System Administrator at DataCorp (2019-2021)',
                'education': 'BS Information Technology, Tech University (2019)',
                'location': 'Austin, TX',
                'website': 'https://mikewilson.dev',
                'linkedin': 'https://linkedin.com/in/mikewilson',
                'github': 'https://github.com/mikewilson'
            }
        ]
        
        # Employers
        employers = [
            {
                'email': 'hr@techcorp.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'employer',
                'bio': 'HR Manager at TechCorp, passionate about finding and nurturing top talent.',
                'location': 'San Francisco, CA',
                'company': 'TechCorp Inc.'
            },
            {
                'email': 'jobs@designstudio.com',
                'first_name': 'David',
                'last_name': 'Chen',
                'role': 'employer',
                'bio': 'Creative Director at Design Studio, looking for talented designers to join our team.',
                'location': 'New York, NY',
                'company': 'Design Studio'
            },
            {
                'email': 'careers@cloudtech.com',
                'first_name': 'Emily',
                'last_name': 'Brown',
                'role': 'employer',
                'bio': 'Talent Acquisition Specialist at CloudTech, helping build our engineering team.',
                'location': 'Austin, TX',
                'company': 'CloudTech Solutions'
            }
        ]
        
        # Create job seekers
        for seeker_data in job_seekers:
            user = User(
                email=seeker_data['email'],
                password_hash=generate_password_hash('password123'),
                first_name=seeker_data['first_name'],
                last_name=seeker_data['last_name'],
                display_name=f"{seeker_data['first_name']} {seeker_data['last_name']}",
                role=seeker_data['role'],
                profile_complete=True,
                bio=seeker_data['bio'],
                skills=seeker_data['skills'],
                experience=seeker_data['experience'],
                education=seeker_data['education'],
                location=seeker_data['location'],
                website=seeker_data['website'],
                linkedin=seeker_data['linkedin'],
                github=seeker_data['github']
            )
            db.session.add(user)
            users.append(user)
            print(f"Created job seeker: {user.display_name}")
        
        # Create employers
        for employer_data in employers:
            user = User(
                email=employer_data['email'],
                password_hash=generate_password_hash('password123'),
                first_name=employer_data['first_name'],
                last_name=employer_data['last_name'],
                display_name=f"{employer_data['first_name']} {employer_data['last_name']}",
                role=employer_data['role'],
                profile_complete=True,
                bio=employer_data['bio'],
                location=employer_data['location']
            )
            db.session.add(user)
            users.append(user)
            print(f"Created employer: {user.display_name}")
        
        db.session.commit()
        
        # Create sample jobs
        jobs = []
        
        sample_jobs = [
            {
                'title': 'Senior Frontend Developer',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'job_type': 'Full-time',
                'remote': True,
                'salary': '$120k - $160k',
                'tags': 'React, TypeScript, Next.js, GraphQL, Jest',
                'urgent': False,
                'description': 'We\'re looking for a Senior Frontend Developer to join our team and help build amazing user experiences. You\'ll work on cutting-edge web applications and collaborate with designers and backend developers.',
                'requirements': '5+ years of frontend development experience\nExpert knowledge of React and TypeScript\nExperience with modern build tools and testing frameworks\nStrong understanding of web performance and accessibility\nExcellent communication and collaboration skills',
                'benefits': 'Competitive salary and equity\nComprehensive health insurance\nFlexible work arrangements\nProfessional development budget\nRegular team events and activities',
                'category': 'technology',
                'employer_id': next(u.id for u in users if u.role == 'employer' and 'techcorp' in u.email.lower())
            },
            {
                'title': 'Product Designer',
                'company': 'Design Studio',
                'location': 'New York, NY',
                'job_type': 'Full-time',
                'remote': False,
                'salary': '$90k - $130k',
                'tags': 'Figma, Sketch, Prototyping, User Research',
                'urgent': True,
                'description': 'Join our creative team as a Product Designer and help shape the future of digital products. You\'ll work on user experience design, create beautiful interfaces, and conduct user research.',
                'requirements': '3+ years of product design experience\nProficiency in Figma and other design tools\nExperience with user research and testing\nStrong portfolio showcasing your work\nAbility to work in a fast-paced environment',
                'benefits': 'Creative and collaborative work environment\nOpportunity to work on exciting projects\nProfessional development and training\nFlexible work hours\nBeautiful office in Manhattan',
                'category': 'design',
                'employer_id': next(u.id for u in users if u.role == 'employer' and 'designstudio' in u.email.lower())
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudTech Solutions',
                'location': 'Austin, TX',
                'job_type': 'Full-time',
                'remote': True,
                'salary': '$110k - $150k',
                'tags': 'AWS, Docker, Kubernetes, Terraform',
                'urgent': False,
                'description': 'We\'re seeking a DevOps Engineer to help scale our infrastructure and automate our deployment processes. You\'ll work with cutting-edge cloud technologies and help improve our development workflow.',
                'requirements': '3+ years of DevOps experience\nStrong knowledge of AWS services\nExperience with Docker and Kubernetes\nProficiency in infrastructure as code (Terraform)\nPython or Bash scripting skills',
                'benefits': 'Remote-first work environment\nCompetitive salary and benefits\nLatest tools and technologies\nProfessional development opportunities\nCollaborative team culture',
                'category': 'technology',
                'employer_id': next(u.id for u in users if u.role == 'employer' and 'cloudtech' in u.email.lower())
            },
            {
                'title': 'Marketing Manager',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'job_type': 'Full-time',
                'remote': False,
                'salary': '$80k - $120k',
                'tags': 'Digital Marketing, SEO, Social Media, Analytics',
                'urgent': False,
                'description': 'Join our marketing team and help drive growth through innovative digital marketing strategies. You\'ll manage campaigns, analyze performance, and work with cross-functional teams.',
                'requirements': '4+ years of digital marketing experience\nExperience with SEO and social media marketing\nProficiency in Google Analytics and marketing tools\nStrong analytical and communication skills\nExperience in B2B marketing preferred',
                'benefits': 'Competitive salary and benefits\nOpportunity to work with cutting-edge technology\nCollaborative team environment\nProfessional growth opportunities\nRegular team events',
                'category': 'marketing',
                'employer_id': next(u.id for u in users if u.role == 'employer' and 'techcorp' in u.email.lower())
            },
            {
                'title': 'Sales Representative',
                'company': 'CloudTech Solutions',
                'location': 'Austin, TX',
                'job_type': 'Full-time',
                'remote': False,
                'salary': '$60k - $90k + Commission',
                'tags': 'Sales, B2B, CRM, Customer Relations',
                'urgent': True,
                'description': 'We\'re looking for a motivated Sales Representative to help grow our customer base. You\'ll work with potential clients, understand their needs, and present our cloud solutions.',
                'requirements': '2+ years of B2B sales experience\nStrong communication and presentation skills\nExperience with CRM systems\nAbility to work independently and in teams\nBachelor\'s degree preferred',
                'benefits': 'Competitive base salary plus commission\nUnlimited earning potential\nComprehensive training program\nCareer advancement opportunities\nTeam-based work environment',
                'category': 'sales',
                'employer_id': next(u.id for u in users if u.role == 'employer' and 'cloudtech' in u.email.lower())
            }
        ]
        
        for job_data in sample_jobs:
            job = Job(
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                job_type=job_data['job_type'],
                remote=job_data['remote'],
                salary=job_data['salary'],
                tags=job_data['tags'],
                urgent=job_data['urgent'],
                description=job_data['description'],
                requirements=job_data['requirements'],
                benefits=job_data['benefits'],
                category=job_data['category'],
                employer_id=job_data['employer_id'],
                employer_email=next(u.email for u in users if u.id == job_data['employer_id']),
                posted_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                applications_count=random.randint(0, 15)
            )
            db.session.add(job)
            jobs.append(job)
            print(f"Created job: {job.title} at {job.company}")
        
        db.session.commit()
        
        # Create sample applications
        job_seeker_users = [u for u in users if u.role == 'jobseeker']
        
        for job in jobs:
            # Create 2-5 applications per job
            num_applications = random.randint(2, 5)
            for _ in range(num_applications):
                applicant = random.choice(job_seeker_users)
                application = Application(
                    job_id=job.id,
                    job_title=job.title,
                    applicant_id=applicant.id,
                    applicant_name=f"{applicant.first_name} {applicant.last_name}",
                    applicant_email=applicant.email,
                    employer_id=job.employer_id,
                    cover_letter=f"I'm excited to apply for the {job.title} position at {job.company}. I believe my skills and experience make me a great fit for this role.",
                    status=random.choice(['new', 'reviewed', 'interview', 'rejected']),
                    applied_at=datetime.utcnow() - timedelta(days=random.randint(1, 14))
                )
                db.session.add(application)
                print(f"Created application from {applicant.display_name} for {job.title}")
        
        db.session.commit()
        
        # Create sample interviews
        print("Creating sample interviews...")
        applications = Application.query.all()
        
        for application in applications[:8]:  # Create interviews for first 8 applications
            if application.status in ['new', 'reviewed']:
                # Schedule interview for some applications
                interview = Interview(
                    application_id=application.id,
                    job_id=application.job_id,
                    applicant_id=application.applicant_id,
                    employer_id=application.employer_id,
                    scheduled_at=datetime.utcnow() + timedelta(days=random.randint(1, 14)),
                    duration=random.choice([30, 45, 60, 90]),
                    interview_type=random.choice(['video', 'phone', 'onsite']),
                    location='San Francisco Office' if random.choice([True, False]) else None,
                    meeting_link='https://zoom.us/j/123456789' if random.choice([True, False]) else None,
                    notes='Initial screening interview to discuss experience and fit for the role.',
                    status='scheduled'
                )
                
                # Update application status to shortlisted
                application.status = 'shortlisted'
                
                db.session.add(interview)
                print(f"Created interview for {application.applicant_name} - {application.job_title}")
        
        db.session.commit()
        
        # Create sample analytics data
        print("Creating sample analytics...")
        for job in jobs:
            job_applications = Application.query.filter_by(job_id=job.id).all()
            
            analytics = ApplicationAnalytics(
                job_id=job.id,
                total_applications=len(job_applications),
                applications_today=sum(1 for app in job_applications if app.applied_at.date() == datetime.utcnow().date()),
                applications_this_week=sum(1 for app in job_applications if app.applied_at >= datetime.utcnow() - timedelta(days=7)),
                applications_this_month=sum(1 for app in job_applications if app.applied_at >= datetime.utcnow() - timedelta(days=30)),
                shortlisted_count=sum(1 for app in job_applications if app.status == 'shortlisted'),
                interview_count=sum(1 for app in job_applications if app.status == 'shortlisted'),
                hired_count=sum(1 for app in job_applications if app.status == 'hired'),
                rejected_count=sum(1 for app in job_applications if app.status == 'rejected'),
                average_rating=round(random.uniform(3.0, 5.0), 1)
            )
            db.session.add(analytics)
            print(f"Created analytics for {job.title}")
        
        db.session.commit()
        
        print("\nSample data created successfully!")
        print(f"Created {len(users)} users")
        print(f"Created {len(jobs)} jobs")
        print(f"Created {len(jobs) * 3} applications")
        print(f"Created {len(applications[:8])} interviews")
        print(f"Created {len(jobs)} analytics records")
        print("\nDefault login credentials:")
        print("Email: john.doe@example.com, Password: password123")
        print("Email: hr@techcorp.com, Password: password123")

if __name__ == '__main__':
    create_sample_data()
