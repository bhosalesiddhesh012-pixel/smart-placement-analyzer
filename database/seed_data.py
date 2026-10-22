import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import hashlib
from database.db import query_db, execute_db, init_db

def hash_pw(pw):
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()

def seed():
    print("Checking database tables...")
    init_db()

    # Check if already seeded
    # Data consistency fix: a readiness index below 52 maps to 'Needs Remediation'
    # (same rule used to train the ML classifier). Idempotent, safe on every launch.
    execute_db(
        "UPDATE students SET target_tier = 'Needs Remediation' "
        "WHERE placement_readiness_index < 52 AND target_tier != 'Needs Remediation'"
    )

    existing_user = query_db("SELECT id FROM users WHERE email = ?", ('sachin.jadhav@vit.edu',), one=True)
    if existing_user:
        # Guarantee all student passwords match their PRN / GR No
        existing_students = query_db("SELECT user_id, gr_no FROM students")
        for s in existing_students:
            execute_db("UPDATE users SET password_hash = ? WHERE id = ?", (hash_pw(str(s['gr_no'])), s['user_id']))
        print("Database already seeded with core accounts. Verified student PRN password hashes.")
        return

    print("Seeding Users & Roles (Admin/TPO and VIT Computer Engineering Students)...")

    # 1. Admin / TPO Guide Account
    tpo_pw = hash_pw("vitadmin123")
    tpo_user_id = execute_db(
        "INSERT INTO users (email, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
        ('sachin.jadhav@vit.edu', tpo_pw, 'TPO', 'Prof. Sachin Jadhav (TPO / Internal Guide)')
    )

    # 2. Student Accounts (Group Members from Project Proposal)
    group_students = [
        {
            'email': 'siddhesh.1251070128@vit.edu',
            'name': 'Siddhesh Bhosale',
            'roll_no': '2071126',
            'gr_no': '1251070128',
            'phone': '9152571938',
            'dept': 'Computer Engineering',
            'sem': 3,
            'cgpa': 9.25,
            'ssc': 91.40,
            'hsc': 89.60,
            'active_backlogs': 0,
            'history_backlogs': 0,
            'dsa_score': 88.5,
            'leetcode': 320,
            'hackathons': 2,
            'projects': 4,
            'certifications': 3,
            'soft_skills': 85.0,
            'readiness_index': 92.4,
            'target_tier': 'Tier 1 Product'
        },
        {
            'email': 'meghraj.1251070283@vit.edu',
            'name': 'Meghraj Sirsat',
            'roll_no': '2071129',
            'gr_no': '1251070283',
            'phone': '7666641855',
            'dept': 'Computer Engineering',
            'sem': 3,
            'cgpa': 8.70,
            'ssc': 88.20,
            'hsc': 85.00,
            'active_backlogs': 0,
            'history_backlogs': 0,
            'dsa_score': 78.0,
            'leetcode': 210,
            'hackathons': 1,
            'projects': 3,
            'certifications': 2,
            'soft_skills': 80.0,
            'readiness_index': 83.5,
            'target_tier': 'Tier 1 Product'
        },
        {
            'email': 'soham.1251070915@vit.edu',
            'name': 'Soham Ombale',
            'roll_no': '2071134',
            'gr_no': '1251070915',
            'phone': '9284595670',
            'dept': 'Computer Engineering',
            'sem': 3,
            'cgpa': 8.10,
            'ssc': 84.50,
            'hsc': 81.20,
            'active_backlogs': 0,
            'history_backlogs': 1,
            'dsa_score': 71.0,
            'leetcode': 140,
            'hackathons': 1,
            'projects': 2,
            'certifications': 2,
            'soft_skills': 75.0,
            'readiness_index': 74.8,
            'target_tier': 'Tier 2 Core'
        },
        {
            'email': 'arpit.1251070081@vit.edu',
            'name': 'Arpit Tale',
            'roll_no': '2071161',
            'gr_no': '1251070081',
            'phone': '9579816991',
            'dept': 'Computer Engineering',
            'sem': 3,
            'cgpa': 7.65,
            'ssc': 82.00,
            'hsc': 78.50,
            'active_backlogs': 1,
            'history_backlogs': 1,
            'dsa_score': 58.0,
            'leetcode': 85,
            'hackathons': 0,
            'projects': 2,
            'certifications': 1,
            'soft_skills': 68.0,
            'readiness_index': 61.2,
            'target_tier': 'Mass Recruiter'
        },
        # Additional cohort students for institutional analytics & gap testing
        {
            'email': 'ananya.deshmukh@vit.edu',
            'name': 'Ananya Deshmukh',
            'roll_no': '2071105',
            'gr_no': '1251070102',
            'phone': '9822012345',
            'dept': 'Computer Engineering',
            'sem': 3,
            'cgpa': 9.60,
            'ssc': 94.00,
            'hsc': 92.50,
            'active_backlogs': 0,
            'history_backlogs': 0,
            'dsa_score': 95.0,
            'leetcode': 450,
            'hackathons': 3,
            'projects': 5,
            'certifications': 4,
            'soft_skills': 92.0,
            'readiness_index': 97.0,
            'target_tier': 'Tier 1 Product'
        },
        {
            'email': 'rohit.patil@vit.edu',
            'name': 'Rohit Patil',
            'roll_no': '2071142',
            'gr_no': '1251070340',
            'phone': '9422054321',
            'dept': 'Computer Engineering',
            'sem': 3,
            'cgpa': 6.40,
            'ssc': 72.00,
            'hsc': 69.50,
            'active_backlogs': 2,
            'history_backlogs': 3,
            'dsa_score': 42.0,
            'leetcode': 30,
            'hackathons': 0,
            'projects': 1,
            'certifications': 0,
            'soft_skills': 55.0,
            'readiness_index': 44.5,
            'target_tier': 'Needs Remediation'
        }
    ]

    for s in group_students:
        student_pw = hash_pw(str(s['gr_no']))
        uid = execute_db(
            "INSERT INTO users (email, password_hash, role, full_name) VALUES (?, ?, 'STUDENT', ?)",
            (s['email'], student_pw, s['name'])
        )
        execute_db(
            """INSERT INTO students (
                user_id, roll_no, gr_no, full_name, email, phone, department, semester,
                cgpa, ssc_percentage, hsc_percentage, active_backlogs, history_backlogs,
                dsa_score, leetcode_solved, hackathons_won, projects_count, certifications_count,
                soft_skills_score, placement_readiness_index, target_tier
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                uid, s['roll_no'], s['gr_no'], s['name'], s['email'], s['phone'], s['dept'], s['sem'],
                s['cgpa'], s['ssc'], s['hsc'], s['active_backlogs'], s['history_backlogs'],
                s['dsa_score'], s['leetcode'], s['hackathons'], s['projects'], s['certifications'],
                s['soft_skills'], s['readiness_index'], s['target_tier']
            )
        )

    print("Seeding Companies...")
    companies = [
        # name, domain, tier, HQ, website, icon, min_lpa, max_lpa, min_cgpa_cutoff, min_dsa_cutoff, min_readiness_cutoff
        ('Google India', 'Cloud & AI Systems', 'Tier 1 Product', 'Bangalore / Hyderabad', 'https://careers.google.com', 'fa-brands fa-google', 32.00, 48.00, 8.50, 80.0, 85.0),
        ('Microsoft IDC', 'Operating Systems & Enterprise Cloud', 'Tier 1 Product', 'Hyderabad / Bangalore', 'https://careers.microsoft.com', 'fa-brands fa-microsoft', 28.00, 44.00, 8.00, 75.0, 80.0),
        ('NVIDIA', 'Graphics & Accelerated Computing', 'Tier 1 Product', 'Pune / Bangalore', 'https://nvidia.com/careers', 'fa-solid fa-microchip', 24.00, 36.00, 8.00, 75.0, 80.0),
        ('Barclays Technology Centre', 'FinTech & Banking Infrastructure', 'Tier 2 Core', 'Pune (EON Kharadi)', 'https://barclays.com', 'fa-solid fa-building-columns', 14.00, 20.00, 7.50, 65.0, 70.0),
        ('Mastercard', 'Payment Networks & Cybersecurity', 'Tier 2 Core', 'Pune', 'https://mastercard.com', 'fa-brands fa-cc-mastercard', 12.00, 18.00, 7.20, 65.0, 68.0),
        ('Tata Consultancy Services (TCS Digital/Ninja)', 'IT Services & Consulting', 'Mass Recruiter', 'Mumbai / Pune', 'https://tcs.com/careers', 'fa-solid fa-server', 3.80, 7.50, 6.00, 50.0, 55.0),
        ('Infosys Ltd (Power Programmer & SE)', 'Enterprise Software', 'Mass Recruiter', 'Pune Hinjewadi', 'https://infosys.com', 'fa-solid fa-laptop-code', 3.60, 9.50, 6.00, 50.0, 55.0)
    ]

    company_ids = {}
    for c in companies:
        cid = execute_db(
            """INSERT INTO companies (
                name, domain, tier, headquarters, website, logo_icon,
                min_package_lpa, max_package_lpa, min_cgpa_cutoff, min_dsa_cutoff, min_readiness_cutoff
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            c
        )
        company_ids[c[0]] = cid

    print("Seeding Placement Drives & Dynamic Criteria...")
    drives = [
        {
            'company': 'Google India',
            'title': 'Software Engineering Campus Hiring 2026',
            'role': 'Associate Software Engineer (L3)',
            'package': 36.50,
            'date': '2026-10-15',
            'deadline': '2026-10-05',
            'loc': 'Hyderabad / Bangalore',
            'type': 'Full Time',
            'desc': 'Recruitment for Core Systems, Distributed Computing, and Cloud Infrastructure.',
            'criteria': {
                'min_cgpa': 8.50,
                'max_backlogs': 0,
                'min_dsa': 80.0,
                'min_readiness': 85.0,
                'min_soft': 75.0,
                'branches': 'Computer Engineering, IT, AI and DS',
                'skills': 'Advanced Data Structures, Graph Algorithms, System Design, C++/Java/Python'
            }
        },
        {
            'company': 'Microsoft IDC',
            'title': 'Campus University Hire - Software Engineer',
            'role': 'Software Development Engineer 1',
            'package': 32.00,
            'date': '2026-10-22',
            'deadline': '2026-10-10',
            'loc': 'Bangalore IDC',
            'type': 'Full Time',
            'desc': 'Building planetary scale cloud infrastructure on Azure and AI Copilot foundations.',
            'criteria': {
                'min_cgpa': 8.00,
                'max_backlogs': 0,
                'min_dsa': 75.0,
                'min_readiness': 80.0,
                'min_soft': 70.0,
                'branches': 'Computer Engineering, IT, AI and DS',
                'skills': 'OOP, Tree & Graph Algorithms, Concurrency, SQL, Python'
            }
        },
        {
            'company': 'Barclays Technology Centre',
            'title': 'Graduate Analyst - Developer & DevSecOps',
            'role': 'Graduate Technology Analyst',
            'package': 16.50,
            'date': '2026-10-28',
            'deadline': '2026-10-15',
            'loc': 'Pune (EON Free Zone)',
            'type': 'Full Time',
            'desc': 'Global payment channels, resilient microservices, and transaction banking.',
            'criteria': {
                'min_cgpa': 7.50,
                'max_backlogs': 0,
                'min_dsa': 65.0,
                'min_readiness': 70.0,
                'min_soft': 65.0,
                'branches': 'Computer Engineering, IT, AI and DS, ENTC',
                'skills': 'Core Java / Python, Relational DBs (MySQL), REST APIs, Git'
            }
        },
        {
            'company': 'Mastercard',
            'title': 'Associate Software Engineer Campus Recruitment',
            'role': 'Associate Software Engineer',
            'package': 14.00,
            'date': '2026-11-05',
            'deadline': '2026-10-20',
            'loc': 'Pune Tech Hub',
            'type': 'Full Time',
            'desc': 'Real-time payment authorization and transaction security platforms.',
            'criteria': {
                'min_cgpa': 7.20,
                'max_backlogs': 0,
                'min_dsa': 65.0,
                'min_readiness': 68.0,
                'min_soft': 65.0,
                'branches': 'Computer Engineering, IT, AI and DS',
                'skills': 'Spring Boot, Python, SQL, Cryptography Basics'
            }
        },
        {
            'company': 'Tata Consultancy Services (TCS Digital/Ninja)',
            'title': 'TCS National Qualifier Drive (Digital & Prime Tracks)',
            'role': 'Systems Engineer / Digital Cadre',
            'package': 7.50,
            'date': '2026-11-12',
            'deadline': '2026-10-25',
            'loc': 'Pan India / Pune',
            'type': 'Full Time',
            'desc': 'High-volume campus hiring for Enterprise Digital Transformation projects.',
            'criteria': {
                'min_cgpa': 6.00,
                'max_backlogs': 1,
                'min_dsa': 50.0,
                'min_readiness': 55.0,
                'min_soft': 55.0,
                'branches': 'All Engineering Branches',
                'skills': 'Aptitude, Core Programming (C/Java/Python), Basic SQL'
            }
        }
    ]

    for d in drives:
        cid = company_ids[d['company']]
        did = execute_db(
            """INSERT INTO placement_drives (
                company_id, job_title, job_role, package_lpa, drive_date, deadline,
                location, drive_type, description, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE')""",
            (cid, d['title'], d['role'], d['package'], d['date'], d['deadline'], d['loc'], d['type'], d['desc'])
        )
        crit = d['criteria']
        execute_db(
            """INSERT INTO drive_criteria (
                drive_id, min_cgpa, max_active_backlogs, min_dsa_score, min_readiness_index,
                min_soft_skills_score, allowed_branches, required_technical_skills
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (did, crit['min_cgpa'], crit['max_backlogs'], crit['min_dsa'], crit['min_readiness'],
             crit['min_soft'], crit['branches'], crit['skills'])
        )

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed()
