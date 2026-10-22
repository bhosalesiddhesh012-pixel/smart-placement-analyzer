# VISHWAKARMA INSTITUTE OF TECHNOLOGY, PUNE
### (An Autonomous Institute Affiliated to Savitribai Phule Pune University)
**Department of Computer Engineering** | Academic Year: 2026–27 | Semester: 3  
**Form FF No. 180** | Issue 01 : Rev No. 00 : Dt. 05/02/26  

---

## 📌 PROJECT REGISTRATION & PROGRESS REVIEW REPORT (REVIEW 1)

| **Attribute** | **Details** |
|:---|:---|
| **Project Title** | **Smart Campus Placement Analyser and Predictor using Machine Learning and Explainable AI** |
| **Group Number** | **SY-K-17** |
| **Review Stage** | **Review 1 (Mid-Semester Review — 50% Completion Milestone)** |
| **Date of Review** | **September 23, 2026** |
| **Project Guide** | **Prof. Sachin Jadhav** (`sachin.jadhav@vit.edu` \| 9881426241) |
| **Project Domain** | AI/ML + Explainable AI (Educational Technology) \| SDG 4 (Quality Education), SDG 8 & SDG 9 |

---

### 👥 Group Members Details:

| Sr. No. | Class & Div | Roll No. | G.R. No. | Name of Student | Contact No. | Email ID |
|:---:|:---:|:---:|:---:|:---|:---:|:---|
| 1 | CS-K | **2071126** | **1251070128** | **Siddhesh Bhosale** | 9152571938 | `siddhesh.1251070128@vit.edu` |
| 2 | CS-K | **2071129** | **1251070283** | **Meghraj Sirsat** | 7666641855 | `meghraj.1251070283@vit.edu` |
| 3 | CS-K | **2071134** | **1251070915** | **Soham Ombale** | 9284595670 | `soham.1251070915@vit.edu` |
| 4 | CS-K | **2071161** | **1251070081** | **Arpit Tale** | 9579816991 | `arpit.1251070081@vit.edu` |

---

## 📝 Part I: Mid-Semester Progress Review Report (50% Scope)

### 1. Executive Summary & Problem Formulation
Traditional campus placement portals act as static, binary "black boxes"—merely returning pass/fail notifications without articulating the technical or academic reasons for student disqualification. Furthermore, placement officers are constrained by hardcoded thresholds that cannot dynamically adjust during live drives.

For **Review 1 (50% Milestone)**, Group SY-K-17 has designed, developed, and validated the core foundational layers of the system using **Python and MySQL**:
1. **Third Normal Form (3NF) Relational Database Schema** in MySQL with strict referential integrity.
2. **Dynamic Recruiter Eligibility Engine** executing live SQL parameter queries.
3. **Machine Learning Predictive Classifier & Regressor (Random Forest)** computing the continuous **Placement Readiness Index (0–100)** and Tier classification.
4. **Actionable Skill-Gap Diagnostics Engine** pinpointing exact numerical deficiencies (e.g., *"DSA score is 6.2% below cutoff"*, *"CGPA deficit of 0.85"*).

---

### 2. Technical Deliverables Completed for Review 1 (Phase 1: 50%)

#### A. Relational Database Modeling (3NF Schema in MySQL)
- Designed and verified 9 normalized relational tables:
  - `users` (Role-based access control: Admin/TPO vs Student).
  - `students` (Comprehensive academic, coding, and assessment profile).
  - `companies` (Recruiter metadata, tier classification, LPA ranges).
  - `placement_drives` (Live campus recruitment drives and deadlines).
  - `drive_criteria` (Dynamic, real-time cutoffs: CGPA, backlogs, DSA score, allowed branches).
  - `student_applications` & `readiness_evaluations` (Historical transaction & index tracking).
- Implemented dual-mode backend in `database/db.py`: Native MySQL via `mysql-connector-python` with automated 3NF SQLite fallback ensuring zero-failure execution.

#### B. Machine Learning Predictive Engine (Python & Scikit-Learn)
- Built and trained an ensemble **Random Forest Classifier & Regressor** pipeline (`ml/predictor.py`):
  - **Feature Vector**: CGPA, SSC %, HSC %, Active Backlogs, History Backlogs, DSA Score, LeetCode Solved, Hackathons Won, Projects Count, Certifications Count, Soft Skills Score.
  - **Readiness Index (0–100)**: Continuous preparedness score evaluated via regressor ($R^2 = 0.987$).
  - **Tier Classification**: Categorizes candidates into *Tier 1 Product*, *Tier 2 Core*, *Mass Recruiter*, or *Needs Remediation* (Accuracy: $92.2\%$).

#### C. Dynamic Recruiter Eligibility Screening Engine (`engine/eligibility_engine.py`)
- Evaluates student candidates against live recruiter cutoffs stored in MySQL:
  - Academic Cutoff Check: `Student CGPA >= Drive min_cgpa`.
  - Backlog Policy Check: `Student active_backlogs <= Drive max_active_backlogs`.
  - Coding & Technical Cutoff: `Student dsa_score >= Drive min_dsa_score`.
  - Department/Branch Eligibility: Dynamic string match on allowed branches.
- Generates categorized statuses: `ELIGIBLE`, `BORDERLINE`, or `INELIGIBLE`.

#### D. Actionable Skill-Gap Diagnostics (`engine/diagnostic_engine.py`)
- Replaces binary rejections with granular numerical deficits:
  - Identifies specific gaps in Data Structures, Project Portfolio, and Backlogs.
  - Calculates exact required increments (e.g. *Need ~165 more LeetCode algorithmic problems solved for Tier 1 qualification*).

---

### 3. Quantitative Test Results & Demonstration Summary

| Test Case | Candidate | Profile Evaluated | Drive Evaluated | Review 1 Outcome | Numerical Deficit Identified |
|---|---|---|---|:---:|---|
| **TC-01** | Siddhesh Bhosale | CGPA: 9.25, DSA: 88.5, Backlogs: 0 | Google India (36.5 LPA) | **ELIGIBLE** | Readiness Index: 85.6/100 (Tier 1 Ready) |
| **TC-02** | Meghraj Sirsat | CGPA: 8.70, DSA: 78.0, Backlogs: 0 | Microsoft IDC (32.0 LPA) | **ELIGIBLE** | Readiness Index: 76.8/100 (Tier 2 Ready) |
| **TC-03** | Soham Ombale | CGPA: 8.10, DSA: 71.0, Backlogs: 0 | Barclays Analyst (16.5 LPA) | **ELIGIBLE** | Readiness Index: 63.1/100 (Core Ready) |
| **TC-04** | Arpit Tale | CGPA: 8.65, DSA: 75.0, Backlogs: 1 | Google India (36.5 LPA) | **INELIGIBLE** | 1 Active Backlog, DSA deficit: 5.0 pts below cutoff |
| **TC-05** | TPO Live Update | Cutoff lowered: CGPA 8.5 -> 7.5 | Real-time MySQL Update | **UPDATED** | Cutoff updated in DB without server restart |

---

## 📅 Part II: Planned Work for Review 2 (Remaining 50% Scope)

As outlined in the approved project synopsis, the remaining 50% will be implemented and presented for **Review 2 (End-of-Semester Review)**:

1. **Acoustic Signal Processing for Soft-Skills Evaluation (`librosa`)**:
   - Audio microphone capture of mock interview speech (`.wav` / `.mp3`).
   - Signal extraction of fundamental frequency pitch ($F_0$), silent pause duration ratio, vocal energy (RMS), and cadence (Words Per Minute).
2. **Explainable AI Local Attribution Breakdown (SHAP)**:
   - TreeSHAP local waterfall attribution plots showing exact positive point drivers and negative drag factors.
3. **Multi-tiered Institutional Analytics Dashboard**:
   - 5-year branch-wise placement trends, salary distribution histograms, and departmental readiness heatmaps for College Administration and TPO.
4. **Dynamic 4-Week Remediation Roadmap Generator**:
   - Automated generation of weekly syllabus sprints, curated LeetCode problem sets, and distributed systems portfolio blueprints.

---

### Signatures:

**Student Team Members:**  
1. Siddhesh Bhosale: ______________________  
2. Meghraj Sirsat:   ______________________  
3. Soham Ombale:     ______________________  
4. Arpit Tale:       ______________________  

**Internal Guide:**  
Prof. Sachin Jadhav: ______________________  
Date: September 23, 2026
