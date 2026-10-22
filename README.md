# Smart Campus Placement Analyser and Predictor using Machine Learning and Explainable AI

**Vishwakarma Institute of Technology (VIT), Pune**  
**Department of Computer Engineering** | Academic Year: 2026–27 | Semester: 3  
**Group No.**: SY-K-17 | **FF No.**: 180  

### Project Team Members:
1. **Siddhesh Bhosale** (Roll No: 2071126, G.R. No: 1251070128) - `siddhesh.1251070128@vit.edu`
2. **Meghraj Sirsat** (Roll No: 2071129, G.R. No: 1251070283) - `meghraj.1251070283@vit.edu`
3. **Soham Ombale** (Roll No: 2071134, G.R. No: 1251070915) - `soham.1251070915@vit.edu`
4. **Arpit Tale** (Roll No: 2071161, G.R. No: 1251070081) - `arpit.1251070081@vit.edu`

**Project Guide**: Prof. Sachin Jadhav (`sachin.jadhav@vit.edu`)

---

## 📌 Executive Summary & Key Innovations

Traditional campus placement portals act like "black boxes"—merely returning binary pass/fail results without explaining reasons for disqualification or providing guidance on how students can bridge identified deficiencies.

This project delivers an end-to-end AI-powered placement framework that solves these flaws:
1. **ML-Driven Predictive Classifier**: Calculates an objective **Placement Readiness Index (0–100)** and predicts placement tiers (**Tier 1 Product**, **Tier 2 Core**, **Mass Recruiter**, **Needs Remediation**) using a balanced Random Forest model.
2. **Explainable AI (TreeSHAP)**: Computes local Shapley feature attribution values showing the exact positive (+ve) drivers (e.g. `+14.2 pts` from DSA) and negative (-ve) drags (e.g. `-8.6 pts` from active backlogs).
3. **Acoustic Signal Processing (Librosa)**: Evaluates mock interview audio in real-time via browser microphone capture or audio file upload (`.wav`, `.mp3`). Extracts pitch variation ($F_0$), silent pause duration ratio, speaking cadence (WPM), and vocal energy to generate an objective soft-skills rating.
4. **Dynamic Recruiter Eligibility Engine**: Placement officers (TPO) can update company cutoffs (CGPA, backlogs, DSA score, branch) in real time directly inside SQL without restarting the application.
5. **Actionable Skill-Gap Diagnostics & Remediation Engine**: Pinpoints precise numerical deficits for students (e.g., *"DSA score is 27.5% below cutoff"*, *"CGPA is 0.85 below threshold"*) and generates a customized **4-week DSA sprint**, project blueprints, and interview drills.
6. **Third Normal Form (3NF) Relational Database**: Normalized relational architecture with dual-mode support (**MySQL** via `mysql-connector` + automatic **SQLite** fallback for zero-setup execution).

---

## 🏗 System Architecture & Technology Stack

```
+-----------------------------------------------------------------------------------+
|                           Smart Placement Web Dashboard                           |
|      (Student Portal | TPO Admin Portal | Real-time Interactive Visualizations)   |
+-----------------------------------------------------------------------------------+
        |                                       |                          |
        v                                       v                          v
+-----------------------+           +-----------------------+   +-------------------+
|  Predictive ML Engine |           |  Explainable AI (XAI) |   | Acoustic Analysis |
| - Random Forest       |           | - TreeSHAP Explainer  |   | - Librosa Audio   |
| - Placement Readiness |           | - Feature Impact +ve/-|   | - Pitch & Energy  |
|   Index (0-100)       |           | - Waterfall & Summary |   | - Fluency & WPM   |
| - Tier Classification |           |   Attribution Charts  |   | - Pause Detection |
+-----------------------+           +-----------------------+   +-------------------+
        |                                       |                          |
        +-------------------+-------------------+--------------------------+
                            |
                            v
+-----------------------------------------------------------------------------------+
|                          Dynamic Rule & Diagnostic Engine                         |
|  - Dynamic Recruiter Eligibility Check against live Placement Drive criteria      |
|  - Actionable Skill-Gap Diagnostics (Exact % deficits, missing skills, backlogs)  |
|  - Personalized Profile Remediation & Roadmap Generator                           |
+-----------------------------------------------------------------------------------+
                            |
                            v
+-----------------------------------------------------------------------------------+
|                    Database Layer (3NF Relational Architecture)                   |
|  - Dual Mode: Native MySQL (via mysql-connector) + Automatic SQLite Fallback     |
|  - Tables: users, students, companies, placement_drives, drive_criteria,          |
|    readiness_evaluations, audio_evaluations, actionable_roadmaps                  |
+-----------------------------------------------------------------------------------+
```

- **Backend & AI/ML**: Python 3.13, Flask 3.1, Scikit-learn 1.9, SHAP 0.52, Librosa 0.11, SoundFile 0.14, NumPy, Pandas.
- **Database**: MySQL 8.0+ / SQLite3 (Normalized 3NF schema, foreign keys, cascade constraints).
- **Frontend**: HTML5, CSS3, Tailwind CSS, FontAwesome 6, Chart.js, HTML5 Web Audio API (MediaRecorder).

---

## 🚀 Quickstart Guide

### 1. Requirements
Ensure Python 3.10+ is installed:
```bash
python3 --version
```

### 2. Navigate to Project Directory
```bash
cd /Users/siddheshbhosale/.gemini/antigravity/scratch/smart_placement_analyzer
```

### 3. Launch the Application
Run the all-in-one startup script:
```bash
python3 start.py
```
This script will automatically:
- Detect your database (connects to MySQL if running on port 3306, or initializes SQLite 3NF fallback).
- Create all 9 normalized relational tables.
- Seed the initial student cohort, recruiters, and placement drives.
- Verify the pre-trained Random Forest and SHAP model bundle.
- Start the web portal at **http://127.0.0.1:5001** (or next available port).

---

## 🗄 MySQL Configuration (Optional)

The application automatically connects to MySQL if running. To explicitly configure your local MySQL credentials:
1. Create or edit `.env` in the project root:
   ```env
   DB_TYPE=mysql
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=smart_placement_db
   ```
2. You can also import the schema manually via MySQL CLI:
   ```bash
   mysql -u root -p < database/schema.sql
   ```

---

## 🧪 Automated Test Suite

A comprehensive test suite verifies database constraints, ML prediction, SHAP attribution values, Librosa speech processing, dynamic criteria evaluation, and web routing:
```bash
python3 test_system.py
```

Expected output:
```
Testing 3NF Relational Database tables & seeded records...
✓ Database 3NF schema & seed verification passed.
Testing RandomForest & Regressor Placement Prediction...
✓ ML Prediction passed: Index=86.8, Tier=Tier 1 Product
Testing TreeSHAP Local Feature Attribution Calculation...
✓ SHAP XAI passed: Base=53.8, Active Backlog SHAP=-8.62
Testing Librosa Acoustic Signal Processing...
✓ Librosa Audio Analysis passed: Soft Skills Score=81.0, WPM=205.2
Testing Dynamic Eligibility Screening against live DB criteria...
✓ Dynamic Eligibility passed: Siddhesh=ELIGIBLE, Arpit=INELIGIBLE (5 deficits)
Testing Flask Web Endpoints & RBAC...
✓ All Flask Web routes and RBAC transitions passed.

Ran 6 tests in 0.554s - OK
```

---

## 🔑 Demo Accounts for Quick Grading & Demonstration

The login screen provides **1-Click Evaluation Login** buttons to immediately test different student and administrative workflows without typing:

| Role | Name | Email | Password | Characteristics |
|------|------|-------|----------|-----------------|
| **TPO / Guide** | Prof. Sachin Jadhav | `sachin.jadhav@vit.edu` | `vitadmin123` | Placement Cell admin, dynamic criteria editor, 5-yr analytics |
| **Student** | Siddhesh Bhosale | `siddhesh.1251070128@vit.edu` | `vitstudent123` | High CGPA (9.25), DSA 88.5, Tier 1 Product Ready, Eligible |
| **Student** | Meghraj Sirsat | `meghraj.1251070283@vit.edu` | `vitstudent123` | CGPA 8.70, DSA 78.0, 210 LeetCode, Tier 1/2 Eligible |
| **Student** | Soham Ombale | `soham.1251070915@vit.edu` | `vitstudent123` | CGPA 8.10, DSA 71.0, Tier 2 Core Eligible |
| **Student** | Arpit Tale | `arpit.1251070081@vit.edu` | `vitstudent123` | CGPA 7.65, 1 Active Backlog, demonstrates Skill-Gap Engine |

---

## 📁 Repository Structure

```
smart_placement_analyzer/
├── app.py                      # Core Flask web server, RBAC & REST APIs
├── config.py                   # Centralized configuration & environment loader
├── start.py                    # One-command server launcher
├── test_system.py              # Automated test suite (ML, SHAP, Librosa, DB)
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── database/
│   ├── schema.sql              # 3NF Relational Schema (MySQL / PostgreSQL)
│   ├── db.py                   # Dual-mode database manager (MySQL + SQLite)
│   └── seed_data.py            # Initial seed records (Students, Companies, Drives)
│
├── ml/
│   ├── train_model.py          # Model training pipeline (Random Forest & Regressor)
│   ├── predictor.py            # Real-time Placement Readiness Index predictor
│   ├── explainer.py            # SHAP TreeExplainer feature attribution engine
│   ├── audio_analyzer.py       # Librosa acoustic speech fluency evaluator
│   └── placement_model.joblib  # Serialized AI/ML & SHAP bundle
│
├── engine/
│   ├── eligibility_engine.py   # Dynamic recruiter criteria screener
│   └── diagnostic_engine.py    # Numerical skill-gap & 4-week roadmap generator
│
├── templates/                  # Frontend Jinja2 templates (Tailwind + Chart.js)
│   ├── base.html               # Master layout with VIT branding & navbar
│   ├── login.html              # Sign-in & 1-click evaluation switcher
│   ├── student_dashboard.html  # Student readiness gauge, metrics & drives
│   ├── explainability.html     # SHAP waterfall attribution charts & drivers
│   ├── interview_lab.html      # Microphone speech recorder & acoustic lab
│   ├── drives.html             # Recruiter drives board with deficit modal
│   ├── roadmap.html            # 4-week DSA sprint & project recommendations
│   ├── profile.html            # Academic & coding metrics editor
│   ├── admin_dashboard.html    # TPO institutional trends & criteria updater
│   └── admin_student_detail.html # Deep-dive diagnostic view for placement cell
│
└── static/
    ├── css/styles.css          # Custom styling & animations
    ├── js/main.js              # Client controller
    └── audio/                  # Saved audio recordings for analysis
```

---

## 🎓 Academic Alignment (VIT SY-K-17 Review Checklist)

- [x] **Predictive Classifier**: Random Forest model with 92.2% test accuracy and continuous 0–100 Readiness Index ($R^2 = 0.987$).
- [x] **Explainable AI (SHAP)**: Individual feature attribution breakdown (+ve drivers vs -ve penalties in points).
- [x] **Acoustic Signal Processing (Librosa)**: Fundamental frequency pitch ($F_0$), pause duration ratio, tempo (WPM), and energy analysis.
- [x] **Dynamic Recruiter Eligibility**: TPO can configure CGPA, backlogs, and DSA cutoffs on live drives in real time.
- [x] **Actionable Skill-Gap Diagnostics**: Exact numerical deficits and 4-week tailored DSA study plans.
- [x] **3NF Relational Database**: Strict primary and foreign keys, cascade constraints, and indexes.
