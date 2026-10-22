import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import uuid
import hashlib
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.utils import secure_filename

import config
from database.db import query_db, execute_db, init_db, get_db_info
from database.seed_data import seed
from ml.predictor import predict_student_readiness
from ml.explainer import explain_student_prediction
from ml.audio_analyzer import analyze_audio_fluency
from engine.eligibility_engine import evaluate_student_drive_eligibility, get_all_drives_for_student
from engine.diagnostic_engine import generate_personalized_remediation
from engine.dsa_quiz_engine import get_quiz_questions, score_quiz, VALID_QUESTION_COUNTS, DEFAULT_QUESTION_COUNT
from engine.ocr_engine import process_and_verify_document
from engine.notification_engine import send_tpo_application_alert

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['DOCUMENTS_FOLDER'] = config.DOCUMENTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOCUMENTS_FOLDER'], exist_ok=True)

# ----------------------------------------------------------------------------
# Authentication & Access Control Helpers
# ----------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this portal.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('role') not in allowed_roles:
                flash('Access restricted to authorized roles.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_student():
    if session.get('role') != 'STUDENT':
        return None
    return query_db("SELECT * FROM students WHERE user_id = ?", (session['user_id'],), one=True)

# ----------------------------------------------------------------------------
# Public & Auth Routes
# ----------------------------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') in ('ADMIN', 'TPO'):
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

        # 1. Lookup user by institutional email
        user = query_db("SELECT * FROM users WHERE LOWER(email) = ?", (identifier,), one=True)

        # 2. If not found by email, check if identifier is PRN / GR No or Roll No
        if not user:
            stu = query_db("SELECT user_id FROM students WHERE LOWER(gr_no) = ? OR LOWER(roll_no) = ?", (identifier, identifier), one=True)
            if stu:
                user = query_db("SELECT * FROM users WHERE id = ?", (stu['user_id'],), one=True)
            elif '@' in identifier:
                local_part = identifier.split('@')[0]
                stu_search = query_db("""
                    SELECT user_id FROM students 
                    WHERE LOWER(email) = ? OR gr_no = ? OR roll_no = ?
                """, (identifier, local_part, local_part), one=True)
                if stu_search:
                    user = query_db("SELECT * FROM users WHERE id = ?", (stu_search['user_id'],), one=True)

        is_authenticated = False
        if user:
            # Standard hash check
            if user['password_hash'] == pw_hash:
                is_authenticated = True
            elif user['role'] == 'STUDENT':
                # Check if password matches student's PRN / GR No or roll_no directly
                stu_rec = query_db("SELECT * FROM students WHERE user_id = ?", (user['id'],), one=True)
                if stu_rec and (password == str(stu_rec['gr_no']) or password == str(stu_rec['roll_no'])):
                    is_authenticated = True
                    # Sync password hash in users table
                    execute_db("UPDATE users SET password_hash = ? WHERE id = ?", (pw_hash, user['id']))

        if is_authenticated:
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            flash(f"Welcome back, {user['full_name']}!", 'success')
            if user['role'] in ('ADMIN', 'TPO'):
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials. Students: Use your @vit.edu email and PRN number as password.', 'danger')

    # Quick demo accounts for testing
    demo_accounts = query_db("""
        SELECT u.id, u.email, u.role, u.full_name, s.roll_no, s.gr_no, s.cgpa, s.placement_readiness_index
        FROM users u
        LEFT JOIN students s ON u.id = s.user_id
        ORDER BY u.role DESC, u.id ASC
    """)
    db_info = get_db_info()
    return render_template('login.html', demo_accounts=demo_accounts, db_info=db_info)

@app.route('/demo-login/<int:user_id>')
def demo_login(user_id):
    user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    if user:
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['full_name'] = user['full_name']
        session['role'] = user['role']
        flash(f"Switched session to {user['full_name']} ({user['role']})", 'info')
        if user['role'] in ('ADMIN', 'TPO'):
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    flash('User not found', 'danger')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        roll_no = request.form.get('roll_no', '').strip()
        gr_no = request.form.get('gr_no', '').strip()
        department = request.form.get('department', 'Computer Engineering').strip()
        semester = int(request.form.get('semester', 3) or 3)
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip() or gr_no

        if not full_name or not email or not roll_no or not gr_no:
            flash('Please fill all required registration fields.', 'danger')
            return render_template('register.html')

        # Check existing user
        if query_db("SELECT id FROM users WHERE LOWER(email) = ?", (email,), one=True):
            flash('An account with this email already exists. Please sign in.', 'danger')
            return redirect(url_for('login'))

        if query_db("SELECT id FROM students WHERE LOWER(roll_no) = ? OR LOWER(gr_no) = ?", (roll_no.lower(), gr_no.lower()), one=True):
            flash('A student with this Roll No or PRN/GR No already exists.', 'danger')
            return render_template('register.html')

        pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        user_id = execute_db(
            "INSERT INTO users (email, password_hash, role, full_name) VALUES (?, ?, 'STUDENT', ?)",
            (email, pw_hash, full_name)
        )

        # Initialize student profile with clean uninitialized metrics
        execute_db("""
            INSERT INTO students (
                user_id, roll_no, gr_no, full_name, email, phone,
                department, semester, cgpa, ssc_percentage, hsc_percentage,
                active_backlogs, history_backlogs, dsa_score, leetcode_solved,
                hackathons_won, projects_count, certifications_count,
                soft_skills_score, placement_readiness_index, target_tier
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.0, 0.0, 0.0, 0, 0, 0.0, 0, 0, 0, 0, 0.0, 0.0, 'Uninitialized')
        """, (user_id, roll_no, gr_no, full_name, email, phone, department, semester))

        session['user_id'] = user_id
        session['email'] = email
        session['full_name'] = full_name
        session['role'] = 'STUDENT'

        flash(f'Welcome, {full_name}! Your student profile has been created with a clean slate. Upload your documents, take the DSA quiz, and evaluate speech fluency to compute your Readiness Index.', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('register.html')

# ----------------------------------------------------------------------------
# Student Portal Routes
# ----------------------------------------------------------------------------
@app.route('/dashboard')
@login_required
@role_required('STUDENT')
def student_dashboard():
    student = get_current_student()
    if not student:
        flash('Student profile not found.', 'danger')
        return redirect(url_for('login'))

    # Run ML prediction to keep metrics fresh
    pred = predict_student_readiness(student)
    # Get active drives
    drives = get_all_drives_for_student(student['id'])
    eligible_count = sum(1 for d in drives if d['eligibility']['is_eligible'])

    # Recent audio evaluation if exists
    latest_audio = query_db("""
        SELECT * FROM audio_evaluations
        WHERE student_id = ?
        ORDER BY id DESC LIMIT 1
    """, (student['id'],), one=True)

    db_info = get_db_info()

    return render_template(
        'student_dashboard.html',
        student=student,
        prediction=pred,
        drives=drives,
        eligible_count=eligible_count,
        total_drives=len(drives),
        latest_audio=latest_audio,
        db_info=db_info
    )

@app.route('/shap')
@app.route('/explainability')
@login_required
@role_required('STUDENT')
def explainability_view():
    student = get_current_student()
    if not student:
        return redirect(url_for('login'))

    shap_result = explain_student_prediction(student)
    return render_template('explainability.html', student=student, shap=shap_result)

@app.route('/speech')
@app.route('/interview-lab')
@login_required
@role_required('STUDENT')
def interview_lab():
    student = get_current_student()
    past_evals = query_db("""
        SELECT * FROM audio_evaluations
        WHERE student_id = ?
        ORDER BY id DESC
    """, (student['id'],))

    topics = [
        "Introduce yourself and highlight your key engineering achievements.",
        "Explain the architecture and technical challenges of your primary software project.",
        "How do you approach debugging a race condition or memory leak in production?",
        "Why are you interested in software engineering at our company?"
    ]

    return render_template('interview_lab.html', student=student, past_evals=past_evals, topics=topics)

@app.route('/api/analyze-audio', methods=['POST'])
@login_required
@role_required('STUDENT')
def api_analyze_audio():
    student = get_current_student()
    if not student:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    topic = request.form.get('topic', 'General Technical & HR Speech Evaluation')

    # Save audio file
    filename = f"audio_{student['id']}_{uuid.uuid4().hex[:8]}.wav"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(filepath)

    try:
        results = analyze_audio_fluency(filepath)

        # Update student record with new soft skills score
        new_soft_score = results['soft_skills_score']
        execute_db(
            "UPDATE students SET soft_skills_score = ? WHERE id = ?",
            (new_soft_score, student['id'])
        )

        # Recompute overall readiness index
        student_updated = query_db("SELECT * FROM students WHERE id = ?", (student['id'],), one=True)
        new_pred = predict_student_readiness(student_updated)
        execute_db(
            "UPDATE students SET placement_readiness_index = ?, target_tier = ? WHERE id = ?",
            (new_pred['readiness_index'], new_pred['predicted_tier'], student['id'])
        )

        # Save to audio_evaluations table
        execute_db("""
            INSERT INTO audio_evaluations (
                student_id, prompt_topic, audio_filename, pitch_mean_hz, pitch_std_hz,
                speech_duration_sec, pause_duration_sec, pause_ratio, speaking_rate_wpm,
                vocal_energy, soft_skills_score, confidence_level, feedback_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student['id'], topic, filename,
            results['pitch_mean_hz'], results['pitch_std_hz'],
            results['speech_duration'], results['pause_duration'],
            results['pause_ratio'], results['speaking_rate_wpm'],
            results['vocal_energy'], results['soft_skills_score'],
            results['confidence_level'], json.dumps(results['feedback_notes'])
        ))

        results['new_readiness_index'] = new_pred['readiness_index']
        results['new_predicted_tier'] = new_pred['predicted_tier']
        results['audio_url'] = url_for('static', filename=f"audio/{filename}")

        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/drives')
@login_required
@role_required('STUDENT')
def student_drives():
    student = get_current_student()
    drives = get_all_drives_for_student(student['id'])
    return render_template('drives.html', student=student, drives=drives)

@app.route('/drives/apply/<int:drive_id>', methods=['POST'])
@login_required
@role_required('STUDENT')
def apply_to_drive(drive_id):
    student = get_current_student()

    # Check existing application
    existing = query_db(
        "SELECT * FROM student_applications WHERE student_id = ? AND drive_id = ?",
        (student['id'], drive_id), one=True
    )
    if existing:
        flash('You have already applied for this placement drive.', 'info')
        return redirect(url_for('student_drives'))

    # Verify eligibility against live dynamic recruiter criteria
    eval_res = evaluate_student_drive_eligibility(student['id'], drive_id)
    if not eval_res['is_eligible']:
        deficits_msg = ", ".join(eval_res['deficits'][:2]) if eval_res['deficits'] else "Criteria not satisfied"
        flash(f"Application rejected: You do not meet the dynamic recruiter criteria ({deficits_msg}).", 'danger')
        return redirect(url_for('student_drives'))

    # Insert into student_applications
    app_id = execute_db("""
        INSERT INTO student_applications (
            student_id, drive_id, is_eligible, eligibility_status,
            deficit_summary_json, application_status, applied_at
        ) VALUES (?, ?, 1, 'ELIGIBLE', ?, 'Pending TPO Review', CURRENT_TIMESTAMP)
    """, (student['id'], drive_id, json.dumps(eval_res['deficits'])))

    # Fetch drive and company info
    drive_info = query_db("""
        SELECT d.*, c.name as company_name, c.tier as company_tier
        FROM placement_drives d
        JOIN companies c ON d.company_id = c.id
        WHERE d.id = ?
    """, (drive_id,), one=True)

    # Trigger automated TPO email alert via smtplib
    send_tpo_application_alert(student, drive_info, app_id)

    flash(f"Application successfully submitted for {drive_info['company_name']} ({drive_info['job_role']})! TPO Officer Prof. Sachin Jadhav has been notified via email alert.", 'success')
    return redirect(url_for('student_drives'))

@app.route('/documents', methods=['GET'])
@login_required
@role_required('STUDENT')
def student_documents():
    student = get_current_student()
    documents = query_db(
        "SELECT * FROM student_documents WHERE student_id = ? ORDER BY uploaded_at DESC",
        (student['id'],)
    ) or []
    for doc in documents:
        if doc.get('extracted_data_json'):
            try:
                doc['extracted'] = json.loads(doc['extracted_data_json'])
            except Exception:
                doc['extracted'] = {}
        else:
            doc['extracted'] = {}
    return render_template('documents.html', student=student, documents=documents)

@app.route('/documents/upload', methods=['POST'])
@login_required
@role_required('STUDENT')
def upload_document():
    student = get_current_student()
    file = request.files.get('document_file')
    doc_type = request.form.get('doc_type', '10TH_MARKSHEET').strip()
    title = request.form.get('title', '').strip()

    if not file or not file.filename:
        flash('Please select a file to upload.', 'danger')
        return redirect(url_for('student_documents'))

    ext = os.path.splitext(file.filename)[1].lower().lstrip('.')
    if ext not in config.ALLOWED_DOCUMENT_EXTENSIONS:
        flash(f'Invalid file format (.{ext}). Allowed formats: {", ".join(config.ALLOWED_DOCUMENT_EXTENSIONS)}', 'danger')
        return redirect(url_for('student_documents'))

    if not title:
        title = {
            '10TH_MARKSHEET': '10th (SSC) Marksheet Proof',
            '12TH_MARKSHEET': '12th (HSC) / Diploma Marksheet Proof',
            'HACKATHON_CERTIFICATE': 'Hackathon Winning Certificate Proof',
            'OTHER': 'Academic / Technical Certification'
        }.get(doc_type, 'Uploaded Document Proof')

    os.makedirs(config.DOCUMENTS_FOLDER, exist_ok=True)
    raw_filename = secure_filename(file.filename)
    safe_name = f"PRN{student['gr_no']}_{doc_type}_{int(datetime.now().timestamp())}_{raw_filename}"
    saved_path = os.path.join(config.DOCUMENTS_FOLDER, safe_name)
    file.save(saved_path)

    file_size_kb = int(os.path.getsize(saved_path) / 1024)

    # Run Backend OCR / Document parser
    parsed = process_and_verify_document(saved_path, doc_type)
    extracted_json = json.dumps(parsed)

    # Insert into student_documents with is_verified = 0 (Pending TPO Verification)
    doc_id = execute_db("""
        INSERT INTO student_documents (
            student_id, doc_type, title, file_path, original_filename,
            file_size_kb, mime_type, extracted_data_json, is_verified, uploaded_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
    """, (
        student['id'], doc_type, title, safe_name, raw_filename,
        file_size_kb, file.content_type, extracted_json
    ))

    # Auto-populate student profile metric from extracted OCR
    recalc_needed = False
    ocr_msg_parts = []
    if doc_type == '10TH_MARKSHEET' and parsed.get('percentage'):
        pct = float(parsed['percentage'])
        execute_db("UPDATE students SET ssc_percentage = ? WHERE id = ?", (pct, student['id']))
        ocr_msg_parts.append(f"Auto-populated 10th (SSC) Percentage to {pct}% (from {parsed.get('board', 'Board')})")
        recalc_needed = True

    elif doc_type == '12TH_MARKSHEET' and parsed.get('percentage'):
        pct = float(parsed['percentage'])
        execute_db("UPDATE students SET hsc_percentage = ? WHERE id = ?", (pct, student['id']))
        ocr_msg_parts.append(f"Auto-populated 12th (HSC) Percentage to {pct}% (from {parsed.get('board', 'Board')})")
        recalc_needed = True

    elif doc_type == 'HACKATHON_CERTIFICATE' and parsed.get('is_winner'):
        execute_db("UPDATE students SET hackathons_won = hackathons_won + 1 WHERE id = ?", (student['id'],))
        ocr_msg_parts.append(f"Auto-incremented Hackathons Won count (+1) for verified award: {parsed.get('achievement_title')}")
        recalc_needed = True

    if recalc_needed:
        updated_student = query_db("SELECT * FROM students WHERE id = ?", (student['id'],), one=True)
        pred = predict_student_readiness(updated_student)
        execute_db(
            "UPDATE students SET placement_readiness_index = ?, target_tier = ? WHERE id = ?",
            (pred['readiness_index'], pred['predicted_tier'], student['id'])
        )

    msg = f"Document '{title}' uploaded successfully! Status: Pending TPO Verification."
    if ocr_msg_parts:
        msg += " OCR Extraction: " + " & ".join(ocr_msg_parts)
    flash(msg, 'success')
    return redirect(url_for('student_documents'))

@app.route('/documents/view/<int:doc_id>')
@login_required
def view_document(doc_id):
    doc = query_db("SELECT * FROM student_documents WHERE id = ?", (doc_id,), one=True)
    if not doc:
        flash('Document not found.', 'danger')
        return redirect(url_for('index'))

    # Security check: Student can view their own document; TPO/Admin can view any document
    if session.get('role') == 'STUDENT':
        student = get_current_student()
        if doc['student_id'] != student['id']:
            flash('Access denied.', 'danger')
            return redirect(url_for('student_dashboard'))

    file_path = os.path.join(config.DOCUMENTS_FOLDER, doc['file_path'])
    if not os.path.exists(file_path):
        flash('Physical file not found on server.', 'danger')
        return redirect(url_for('student_documents'))

    return send_file(file_path, as_attachment=False)

@app.route('/documents/delete/<int:doc_id>', methods=['POST'])
@login_required
@role_required('STUDENT')
def delete_document(doc_id):
    student = get_current_student()
    doc = query_db("SELECT * FROM student_documents WHERE id = ? AND student_id = ?", (doc_id, student['id']), one=True)
    if not doc:
        flash('Document not found.', 'danger')
        return redirect(url_for('student_documents'))

    if doc['is_verified'] == 1:
        flash('Cannot delete a verified document. Please contact TPO.', 'warning')
        return redirect(url_for('student_documents'))

    file_path = os.path.join(config.DOCUMENTS_FOLDER, doc['file_path'])
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    execute_db("DELETE FROM student_documents WHERE id = ?", (doc_id,))
    flash('Document deleted from vault.', 'info')
    return redirect(url_for('student_documents'))

@app.route('/profile/reset', methods=['POST'])
@login_required
@role_required('STUDENT')
def reset_student_profile():
    student = get_current_student()
    execute_db("""
        UPDATE students SET
            cgpa = 0.0, ssc_percentage = 0.0, hsc_percentage = 0.0,
            active_backlogs = 0, history_backlogs = 0,
            dsa_score = 0.0, leetcode_solved = 0, hackathons_won = 0,
            projects_count = 0, certifications_count = 0,
            soft_skills_score = 0.0, placement_readiness_index = 0.0,
            target_tier = 'Uninitialized'
        WHERE id = ?
    """, (student['id'],))
    execute_db("DELETE FROM dsa_quiz_attempts WHERE student_id = ?", (student['id'],))
    execute_db("DELETE FROM student_documents WHERE student_id = ? AND is_verified = 0", (student['id'],))
    flash('Profile metrics reset to clean uninitialized state. You can now build your profile from scratch!', 'info')
    return redirect(url_for('student_dashboard'))

@app.route('/roadmap')
@login_required
@role_required('STUDENT')
def student_roadmap():
    student = get_current_student()
    target_tier = request.args.get('tier', student['target_tier'] or 'Tier 1 Product')
    remediation = generate_personalized_remediation(student['id'], target_tier=target_tier)
    return render_template('roadmap.html', student=student, remediation=remediation, target_tier=target_tier)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('STUDENT')
def student_profile():
    student = get_current_student()

    # Query verified documents to protect verified metrics
    verified_records = query_db(
        "SELECT doc_type, is_verified, original_filename FROM student_documents WHERE student_id = ? AND is_verified = 1",
        (student['id'],)
    ) or []
    verified_docs = {v['doc_type']: v for v in verified_records}

    if request.method == 'POST':
        cgpa = float(request.form.get('cgpa', student['cgpa']))

        # If officially verified by TPO, protect against fraudulent edits
        if '10TH_MARKSHEET' in verified_docs:
            ssc_percentage = float(student['ssc_percentage'])
        else:
            ssc_percentage = float(request.form.get('ssc_percentage', student['ssc_percentage']))

        if '12TH_MARKSHEET' in verified_docs:
            hsc_percentage = float(student['hsc_percentage'])
        else:
            hsc_percentage = float(request.form.get('hsc_percentage', student['hsc_percentage']))

        active_backlogs = int(request.form.get('active_backlogs', student['active_backlogs']))
        history_backlogs = int(request.form.get('history_backlogs', student['history_backlogs']))
        # DSA score is quiz-controlled only; manual edits are ignored.
        dsa_score = float(student['dsa_score'])
        leetcode_solved = int(request.form.get('leetcode_solved', student['leetcode_solved']))
        hackathons_won = int(request.form.get('hackathons_won', student['hackathons_won']))
        projects_count = int(request.form.get('projects_count', student['projects_count']))
        certifications_count = int(request.form.get('certifications_count', student['certifications_count']))

        execute_db("""
            UPDATE students SET
                cgpa = ?, ssc_percentage = ?, hsc_percentage = ?,
                active_backlogs = ?, history_backlogs = ?,
                dsa_score = ?, leetcode_solved = ?, hackathons_won = ?,
                projects_count = ?, certifications_count = ?
            WHERE id = ?
        """, (
            cgpa, ssc_percentage, hsc_percentage,
            active_backlogs, history_backlogs, dsa_score,
            leetcode_solved, hackathons_won, projects_count, certifications_count,
            student['id']
        ))

        # Re-run ML prediction
        updated_student = query_db("SELECT * FROM students WHERE id = ?", (student['id'],), one=True)
        pred = predict_student_readiness(updated_student)
        execute_db(
            "UPDATE students SET placement_readiness_index = ?, target_tier = ? WHERE id = ?",
            (pred['readiness_index'], pred['predicted_tier'], student['id'])
        )

        flash('Academic & Coding metrics updated! Readiness Index recalculated.', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('profile.html', student=student, verified_docs=verified_docs)

# ----------------------------------------------------------------------------
# DSA Technical Assessment Quiz (20/30 Questions -> Auto-Graded DSA Score)
# ----------------------------------------------------------------------------
@app.route('/dsa-quiz', methods=['GET'])
@login_required
@role_required('STUDENT')
def dsa_quiz():
    student = get_current_student()
    quiz_state = session.get('dsa_quiz')

    if quiz_state:
        # An in-progress quiz exists in this session; resume it.
        return render_template('dsa_quiz.html', student=student, quiz=quiz_state, in_progress=True)

    return render_template('dsa_quiz.html', student=student, quiz=None, in_progress=False,
                            valid_counts=VALID_QUESTION_COUNTS)

@app.route('/dsa-quiz/start', methods=['POST'])
@login_required
@role_required('STUDENT')
def dsa_quiz_start():
    try:
        count = int(request.form.get('question_count', DEFAULT_QUESTION_COUNT))
    except (TypeError, ValueError):
        count = DEFAULT_QUESTION_COUNT

    if count not in VALID_QUESTION_COUNTS:
        count = DEFAULT_QUESTION_COUNT

    questions, answer_key = get_quiz_questions(count=count)

    session['dsa_quiz'] = {
        'questions': questions,
        'answer_key': answer_key,
        'count': count
    }
    return redirect(url_for('dsa_quiz'))

@app.route('/dsa-quiz/cancel', methods=['POST'])
@login_required
@role_required('STUDENT')
def dsa_quiz_cancel():
    session.pop('dsa_quiz', None)
    flash('DSA assessment discarded. You can restart anytime.', 'info')
    return redirect(url_for('dsa_quiz'))

@app.route('/dsa-quiz/submit', methods=['POST'])
@login_required
@role_required('STUDENT')
def dsa_quiz_submit():
    student = get_current_student()
    quiz_state = session.get('dsa_quiz')

    if not quiz_state:
        flash('Your DSA assessment session expired. Please start again.', 'warning')
        return redirect(url_for('dsa_quiz'))

    answer_key = quiz_state['answer_key']
    submitted_answers = {}
    for qid_str in answer_key.keys():
        val = request.form.get(f'q_{qid_str}')
        if val is not None:
            submitted_answers[qid_str] = int(val)

    result = score_quiz(submitted_answers, answer_key)

    previous_dsa_score = float(student['dsa_score'])
    updated_dsa_score = result['score_percentage']

    # Persist the quiz-assessed DSA score as the student's official DSA Score.
    execute_db("UPDATE students SET dsa_score = ? WHERE id = ?", (updated_dsa_score, student['id']))

    execute_db("""
        INSERT INTO dsa_quiz_attempts (
            student_id, total_questions, correct_answers, quiz_score,
            previous_dsa_score, updated_dsa_score, topic_breakdown_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        student['id'], result['total_questions'], result['correct_answers'], result['score_percentage'],
        previous_dsa_score, updated_dsa_score, json.dumps(result['topic_breakdown'])
    ))

    # Recompute overall AI Placement Readiness Index using the freshly-assessed DSA score.
    student_updated = query_db("SELECT * FROM students WHERE id = ?", (student['id'],), one=True)
    new_pred = predict_student_readiness(student_updated)
    execute_db(
        "UPDATE students SET placement_readiness_index = ?, target_tier = ? WHERE id = ?",
        (new_pred['readiness_index'], new_pred['predicted_tier'], student['id'])
    )

    session.pop('dsa_quiz', None)

    result['previous_dsa_score'] = previous_dsa_score
    result['updated_dsa_score'] = updated_dsa_score
    result['new_readiness_index'] = new_pred['readiness_index']
    result['new_predicted_tier'] = new_pred['predicted_tier']

    flash(f"DSA Assessment complete! Scored {result['correct_answers']}/{result['total_questions']} "
          f"({updated_dsa_score}%). Your DSA Score & Readiness Index have been recalculated.", 'success')

    return render_template('dsa_quiz_result.html', student=student, result=result)

# ----------------------------------------------------------------------------
# Placement Officer / Admin Portal Routes
# ----------------------------------------------------------------------------
@app.route('/admin')
@login_required
@role_required('ADMIN', 'TPO')
def admin_dashboard():
    # KPI Metrics
    total_students = query_db("SELECT count(*) as c FROM students", one=True)['c']
    avg_readiness = query_db("SELECT AVG(placement_readiness_index) as a FROM students", one=True)['a'] or 0.0
    avg_cgpa = query_db("SELECT AVG(cgpa) as a FROM students", one=True)['a'] or 0.0
    total_drives = query_db("SELECT count(*) as c FROM placement_drives WHERE status = 'ACTIVE'", one=True)['c']

    # Tier Breakdown
    tier_counts = query_db("""
        SELECT target_tier, count(*) as count
        FROM students
        GROUP BY target_tier
    """)

    # Student Roster
    students = query_db("""
        SELECT s.*, u.email
        FROM students s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.placement_readiness_index DESC
    """)

    # Active Drives with criteria
    drives = query_db("""
        SELECT d.*, c.name as company_name, c.tier as company_tier,
               cr.min_cgpa, cr.max_active_backlogs, cr.min_dsa_score, cr.min_readiness_index,
               cr.allowed_branches, cr.required_technical_skills
        FROM placement_drives d
        JOIN companies c ON d.company_id = c.id
        LEFT JOIN drive_criteria cr ON d.id = cr.drive_id
        ORDER BY d.package_lpa DESC
    """)

    # Company Directory (TPO-managed: add new recruiters, edit tier & eligibility cutoffs)
    companies = query_db("SELECT * FROM companies ORDER BY tier ASC, name ASC")

    # Multi-year Placement Analytics Data (Institutional 5-Year Trends)
    yearly_trends = {
        'years': ['2022', '2023', '2024', '2025', '2026 (Projected)'],
        'placed_rate': [84.5, 87.2, 89.6, 91.8, 94.2],
        'avg_package': [7.2, 8.4, 9.6, 11.2, 12.8],
        'highest_package': [33.0, 38.0, 42.0, 44.0, 48.0]
    }

    # Live Student Applications
    applications = query_db("""
        SELECT a.*, s.full_name as student_name, s.roll_no, s.gr_no, s.cgpa, s.dsa_score,
               s.placement_readiness_index, s.target_tier,
               d.job_role, d.package_lpa, c.name as company_name, c.logo_icon
        FROM student_applications a
        JOIN students s ON a.student_id = s.id
        JOIN placement_drives d ON a.drive_id = d.id
        JOIN companies c ON d.company_id = c.id
        ORDER BY a.applied_at DESC
    """) or []

    # Student Uploaded Documents for Verification
    student_documents = query_db("""
        SELECT doc.*, s.full_name as student_name, s.roll_no, s.gr_no, s.email as student_email
        FROM student_documents doc
        JOIN students s ON doc.student_id = s.id
        ORDER BY doc.is_verified ASC, doc.uploaded_at DESC
    """) or []
    for doc in student_documents:
        if doc.get('extracted_data_json'):
            try:
                doc['extracted'] = json.loads(doc['extracted_data_json'])
            except Exception:
                doc['extracted'] = {}
        else:
            doc['extracted'] = {}

    db_info = get_db_info()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        avg_readiness=round(float(avg_readiness), 1),
        avg_cgpa=round(float(avg_cgpa), 2),
        total_drives=total_drives,
        tier_counts=tier_counts,
        students=students,
        drives=drives,
        companies=companies,
        applications=applications,
        student_documents=student_documents,
        yearly_trends=yearly_trends,
        db_info=db_info
    )

@app.route('/admin/documents/<int:doc_id>/verify', methods=['POST'])
@login_required
@role_required('ADMIN', 'TPO')
def admin_verify_document(doc_id):
    tpo_name = session.get('full_name', 'Prof. Sachin Jadhav (TPO)')
    execute_db("""
        UPDATE student_documents
        SET is_verified = 1, verified_by = ?, verified_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (tpo_name, doc_id))
    flash('Document marked as Verified! Student profile metric is now officially verified against fraudulent tampering.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/documents/<int:doc_id>/reject', methods=['POST'])
@login_required
@role_required('ADMIN', 'TPO')
def admin_reject_document(doc_id):
    notes = request.form.get('notes', 'Document illegible or failed verification criteria.').strip()
    execute_db("""
        UPDATE student_documents
        SET is_verified = -1, verification_notes = ?
        WHERE id = ?
    """, (notes, doc_id))
    flash(f'Document rejected and marked for student resubmission ({notes}).', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/applications/<int:app_id>/status', methods=['POST'])
@login_required
@role_required('ADMIN', 'TPO')
def admin_update_application_status(app_id):
    status = request.form.get('status', 'Pending TPO Review').strip()
    execute_db("UPDATE student_applications SET application_status = ? WHERE id = ?", (status, app_id))
    flash(f'Application #{app_id} status updated to "{status}".', 'success')
    return redirect(url_for('admin_dashboard'))

# ----------------------------------------------------------------------------
# TPO Company Directory Management (Add Recruiters / Edit Tier & Cutoffs)
# ----------------------------------------------------------------------------
COMPANY_TIERS = ('Tier 1 Product', 'Tier 2 Core', 'Mass Recruiter')

@app.route('/admin/companies/add', methods=['POST'])
@login_required
@role_required('ADMIN', 'TPO')
def admin_add_company():
    name = request.form.get('name', '').strip()
    domain = request.form.get('domain', '').strip()
    tier = request.form.get('tier', 'Mass Recruiter')
    headquarters = request.form.get('headquarters', '').strip()
    website = request.form.get('website', '').strip()
    logo_icon = request.form.get('logo_icon', '').strip() or 'fa-solid fa-building'

    if not name or not domain:
        flash('Company name and domain are required.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if tier not in COMPANY_TIERS:
        tier = 'Mass Recruiter'

    try:
        min_package_lpa = float(request.form.get('min_package_lpa', 0) or 0)
        max_package_lpa = float(request.form.get('max_package_lpa', 0) or 0)
        min_cgpa_cutoff = float(request.form.get('min_cgpa_cutoff', 6.0) or 6.0)
        min_dsa_cutoff = float(request.form.get('min_dsa_cutoff', 50.0) or 50.0)
        min_readiness_cutoff = float(request.form.get('min_readiness_cutoff', 55.0) or 55.0)
    except ValueError:
        flash('Please enter valid numeric values for package and cutoff fields.', 'danger')
        return redirect(url_for('admin_dashboard'))

    existing = query_db("SELECT id FROM companies WHERE LOWER(name) = ?", (name.lower(),), one=True)
    if existing:
        flash(f'A company named "{name}" already exists in the recruiter directory.', 'warning')
        return redirect(url_for('admin_dashboard'))

    execute_db("""
        INSERT INTO companies (
            name, domain, tier, headquarters, website, logo_icon,
            min_package_lpa, max_package_lpa, min_cgpa_cutoff, min_dsa_cutoff, min_readiness_cutoff
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, domain, tier, headquarters, website, logo_icon,
        min_package_lpa, max_package_lpa, min_cgpa_cutoff, min_dsa_cutoff, min_readiness_cutoff
    ))

    flash(f'Recruiter "{name}" added to the company directory as {tier}.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/companies/<int:company_id>/update', methods=['POST'])
@login_required
@role_required('ADMIN', 'TPO')
def admin_update_company(company_id):
    company = query_db("SELECT * FROM companies WHERE id = ?", (company_id,), one=True)
    if not company:
        flash('Company not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    tier = request.form.get('tier', company['tier'])
    if tier not in COMPANY_TIERS:
        tier = company['tier']

    try:
        min_package_lpa = float(request.form.get('min_package_lpa', company['min_package_lpa']))
        max_package_lpa = float(request.form.get('max_package_lpa', company['max_package_lpa']))
        min_cgpa_cutoff = float(request.form.get('min_cgpa_cutoff', company['min_cgpa_cutoff']))
        min_dsa_cutoff = float(request.form.get('min_dsa_cutoff', company['min_dsa_cutoff']))
        min_readiness_cutoff = float(request.form.get('min_readiness_cutoff', company['min_readiness_cutoff']))
    except (ValueError, TypeError):
        flash('Please enter valid numeric values for package and cutoff fields.', 'danger')
        return redirect(url_for('admin_dashboard'))

    execute_db("""
        UPDATE companies SET
            tier = ?, min_package_lpa = ?, max_package_lpa = ?,
            min_cgpa_cutoff = ?, min_dsa_cutoff = ?, min_readiness_cutoff = ?
        WHERE id = ?
    """, (tier, min_package_lpa, max_package_lpa, min_cgpa_cutoff, min_dsa_cutoff, min_readiness_cutoff, company_id))

    flash(f'"{company["name"]}" updated: Tier = {tier}, Cutoffs saved successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update-criteria', methods=['POST'])
@login_required
@role_required('ADMIN', 'TPO')
def admin_update_criteria():
    drive_id = int(request.form.get('drive_id'))
    min_cgpa = float(request.form.get('min_cgpa'))
    max_backlogs = int(request.form.get('max_active_backlogs'))
    min_dsa = float(request.form.get('min_dsa_score'))
    min_readiness = float(request.form.get('min_readiness_index'))

    execute_db("""
        UPDATE drive_criteria SET
            min_cgpa = ?,
            max_active_backlogs = ?,
            min_dsa_score = ?,
            min_readiness_index = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE drive_id = ?
    """, (min_cgpa, max_backlogs, min_dsa, min_readiness, drive_id))

    flash(f'Dynamic eligibility criteria for Drive #{drive_id} updated successfully in real time!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/student/<int:student_id>')
@login_required
@role_required('ADMIN', 'TPO')
def admin_student_detail(student_id):
    student = query_db("SELECT * FROM students WHERE id = ?", (student_id,), one=True)
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('admin_dashboard'))

    shap_res = explain_student_prediction(student)
    drives = get_all_drives_for_student(student_id)
    remediation = generate_personalized_remediation(student_id, target_tier=student['target_tier'] or 'Tier 1 Product')
    past_audio = query_db("SELECT * FROM audio_evaluations WHERE student_id = ? ORDER BY id DESC", (student_id,))

    return render_template(
        'admin_student_detail.html',
        student=student,
        shap=shap_res,
        drives=drives,
        remediation=remediation,
        past_audio=past_audio
    )

# ----------------------------------------------------------------------------
# System Initialization on Launch
# ----------------------------------------------------------------------------
init_db()
seed()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting Smart Campus Placement Analyser on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
