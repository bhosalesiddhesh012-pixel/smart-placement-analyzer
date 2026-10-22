-- Smart Campus Placement Analyser and Predictor
-- Relational Database Schema (Third Normal Form - 3NF)
-- Designed for MySQL / PostgreSQL with full Primary & Foreign Key Constraints

CREATE DATABASE IF NOT EXISTS smart_placement_db;
USE smart_placement_db;

-- Table 1: Users (Role-Based Access Control)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'STUDENT',
    full_name VARCHAR(150) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Students (Student Academic & Technical Profile)
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    roll_no VARCHAR(50) NOT NULL UNIQUE,
    gr_no VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(191) NOT NULL UNIQUE,
    phone VARCHAR(20),
    department VARCHAR(100) NOT NULL DEFAULT 'Computer Engineering',
    semester INT NOT NULL DEFAULT 3,
    cgpa DECIMAL(4, 2) NOT NULL,
    ssc_percentage DECIMAL(5, 2) NOT NULL,
    hsc_percentage DECIMAL(5, 2) NOT NULL,
    active_backlogs INT NOT NULL DEFAULT 0,
    history_backlogs INT NOT NULL DEFAULT 0,
    dsa_score DECIMAL(5, 2) NOT NULL DEFAULT 0.0,
    leetcode_solved INT NOT NULL DEFAULT 0,
    hackathons_won INT NOT NULL DEFAULT 0,
    projects_count INT NOT NULL DEFAULT 0,
    certifications_count INT NOT NULL DEFAULT 0,
    soft_skills_score DECIMAL(5, 2) DEFAULT 0.0,
    placement_readiness_index DECIMAL(5, 2) DEFAULT 0.0,
    target_tier VARCHAR(50) DEFAULT 'Uninitialized',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table 3: Companies (Recruiter Repository & Tier Classification)
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    domain VARCHAR(100) NOT NULL,
    tier VARCHAR(50) NOT NULL,
    headquarters VARCHAR(100),
    website VARCHAR(255),
    logo_icon VARCHAR(100) DEFAULT 'fa-building',
    min_package_lpa DECIMAL(5, 2) NOT NULL,
    max_package_lpa DECIMAL(5, 2) NOT NULL,
    min_cgpa_cutoff DECIMAL(4, 2) NOT NULL DEFAULT 6.0,
    min_dsa_cutoff DECIMAL(5, 2) NOT NULL DEFAULT 50.0,
    min_readiness_cutoff DECIMAL(5, 2) NOT NULL DEFAULT 55.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 4: Placement Drives (Active & Upcoming Campus Recruitment Drives)
CREATE TABLE IF NOT EXISTS placement_drives (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    job_role VARCHAR(100) NOT NULL,
    package_lpa DECIMAL(5, 2) NOT NULL,
    drive_date DATE NOT NULL,
    deadline DATE NOT NULL,
    location VARCHAR(100) DEFAULT 'On Campus / Hybrid',
    drive_type VARCHAR(50) DEFAULT 'Full Time',
    description TEXT,
    status VARCHAR(30) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Table 5: Dynamic Drive Criteria (Configurable in real-time by TPO)
CREATE TABLE IF NOT EXISTS drive_criteria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drive_id INT NOT NULL UNIQUE,
    min_cgpa DECIMAL(4, 2) NOT NULL DEFAULT 7.0,
    max_active_backlogs INT NOT NULL DEFAULT 0,
    min_dsa_score DECIMAL(5, 2) NOT NULL DEFAULT 60.0,
    min_readiness_index DECIMAL(5, 2) NOT NULL DEFAULT 65.0,
    min_soft_skills_score DECIMAL(5, 2) NOT NULL DEFAULT 60.0,
    allowed_branches VARCHAR(255) DEFAULT 'Computer Engineering, IT, AI&DS',
    required_technical_skills VARCHAR(255) DEFAULT 'Data Structures, Algorithms, Python/Java, SQL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (drive_id) REFERENCES placement_drives(id) ON DELETE CASCADE
);

-- Table 6: Student Applications (Eligibility & Status Tracking)
CREATE TABLE IF NOT EXISTS student_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    drive_id INT NOT NULL,
    is_eligible INT NOT NULL DEFAULT 0,
    eligibility_status VARCHAR(50) NOT NULL,
    deficit_summary_json TEXT,
    application_status VARCHAR(50) DEFAULT 'APPLIED',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (drive_id) REFERENCES placement_drives(id) ON DELETE CASCADE,
    UNIQUE (student_id, drive_id)
);

-- Table 7: Readiness Evaluations (ML Predictions & SHAP Values)
CREATE TABLE IF NOT EXISTS readiness_evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    readiness_score DECIMAL(5, 2) NOT NULL,
    predicted_tier VARCHAR(50) NOT NULL,
    shap_values_json TEXT NOT NULL,
    base_value DECIMAL(5, 2) NOT NULL,
    feature_contributions_json TEXT NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Table 8: Audio Mock Interview Evaluations (Librosa Acoustic Analysis)
CREATE TABLE IF NOT EXISTS audio_evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    prompt_topic VARCHAR(255) NOT NULL,
    audio_filename VARCHAR(255) NOT NULL,
    pitch_mean_hz DECIMAL(6, 2) NOT NULL,
    pitch_std_hz DECIMAL(6, 2) NOT NULL,
    speech_duration_sec DECIMAL(6, 2) NOT NULL,
    pause_duration_sec DECIMAL(6, 2) NOT NULL,
    pause_ratio DECIMAL(5, 2) NOT NULL,
    speaking_rate_wpm DECIMAL(5, 2) NOT NULL,
    vocal_energy DECIMAL(6, 4) NOT NULL,
    soft_skills_score DECIMAL(5, 2) NOT NULL,
    confidence_level VARCHAR(50) NOT NULL,
    feedback_json TEXT NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Table 9: Actionable Profile Roadmaps (Diagnostic Skill-Gap Solutions)
CREATE TABLE IF NOT EXISTS actionable_roadmaps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    target_tier VARCHAR(50) NOT NULL,
    weakness_areas_json TEXT NOT NULL,
    dsa_plan_json TEXT NOT NULL,
    project_recommendations_json TEXT NOT NULL,
    interview_prep_json TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Table 10: DSA Quiz Attempts (20/30 Question Auto-Graded Assessments)
CREATE TABLE IF NOT EXISTS dsa_quiz_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    total_questions INT NOT NULL,
    correct_answers INT NOT NULL,
    quiz_score DECIMAL(5, 2) NOT NULL,
    previous_dsa_score DECIMAL(5, 2),
    updated_dsa_score DECIMAL(5, 2) NOT NULL,
    topic_breakdown_json TEXT,
    taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Table 11: Student Document Vault (Marksheets & Verified Proofs)
CREATE TABLE IF NOT EXISTS student_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    doc_type VARCHAR(50) NOT NULL, -- '10TH_MARKSHEET', '12TH_MARKSHEET', 'HACKATHON_CERTIFICATE', 'OTHER'
    title VARCHAR(150) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size_kb INT DEFAULT 0,
    mime_type VARCHAR(100),
    extracted_data_json TEXT,
    is_verified INT NOT NULL DEFAULT 0, -- 0 = Pending, 1 = Verified, -1 = Rejected
    verified_by VARCHAR(150),
    verified_at TIMESTAMP NULL,
    verification_notes TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
