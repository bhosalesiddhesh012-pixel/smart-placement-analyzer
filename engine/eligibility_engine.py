import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import query_db

def evaluate_student_drive_eligibility(student_id, drive_id):
    """
    Evaluates student record against live dynamic placement drive criteria from SQL DB.
    Returns:
        is_eligible: bool
        status: 'ELIGIBLE' | 'BORDERLINE' | 'INELIGIBLE'
        criteria: dict of drive criteria
        checks: dict of per-parameter checks with pass/fail and deficits
        deficits: list of human-readable deficit strings
    """
    # 1. Fetch student
    student = query_db("SELECT * FROM students WHERE id = ?", (student_id,), one=True)
    if not student:
        raise ValueError(f"Student with ID {student_id} not found")

    # 2. Fetch drive and dynamic criteria
    drive_info = query_db("""
        SELECT d.*, c.name as company_name, c.tier as company_tier,
               cr.min_cgpa, cr.max_active_backlogs, cr.min_dsa_score,
               cr.min_readiness_index, cr.min_soft_skills_score,
               cr.allowed_branches, cr.required_technical_skills
        FROM placement_drives d
        JOIN companies c ON d.company_id = c.id
        LEFT JOIN drive_criteria cr ON d.id = cr.drive_id
        WHERE d.id = ?
    """, (drive_id,), one=True)

    if not drive_info:
        raise ValueError(f"Placement drive with ID {drive_id} not found")

    # Default criteria fallbacks if not configured
    min_cgpa = float(drive_info.get('min_cgpa') or 7.0)
    max_backlogs = int(drive_info.get('max_active_backlogs') if drive_info.get('max_active_backlogs') is not None else 0)
    min_dsa = float(drive_info.get('min_dsa_score') or 60.0)
    min_readiness = float(drive_info.get('min_readiness_index') or 65.0)
    min_soft = float(drive_info.get('min_soft_skills_score') or 60.0)
    allowed_branches_str = str(drive_info.get('allowed_branches') or 'All Engineering Branches')

    # Current student metrics
    s_cgpa = float(student['cgpa'])
    s_backlogs = int(student['active_backlogs'])
    s_dsa = float(student['dsa_score'])
    s_readiness = float(student['placement_readiness_index'])
    s_soft = float(student['soft_skills_score'] if student.get('soft_skills_score') is not None else 0.0)
    s_branch = student['department']

    checks = []
    deficits = []

    # Check 1: CGPA
    cgpa_pass = s_cgpa >= min_cgpa
    cgpa_diff = round(s_cgpa - min_cgpa, 2)
    if not cgpa_pass:
        deficits.append(f"CGPA is {abs(cgpa_diff):.2f} points below required cutoff (Current: {s_cgpa:.2f}, Required: {min_cgpa:.2f})")
    checks.append({
        'parameter': 'Minimum CGPA',
        'student_val': f"{s_cgpa:.2f}",
        'required_val': f"{min_cgpa:.2f}",
        'passed': cgpa_pass,
        'difference': cgpa_diff,
        'unit': 'CGPA'
    })

    # Check 2: Active Backlogs
    backlogs_pass = s_backlogs <= max_backlogs
    if not backlogs_pass:
        deficits.append(f"Active backlogs exceed maximum allowed by {s_backlogs - max_backlogs} (Current: {s_backlogs}, Allowed: {max_backlogs})")
    checks.append({
        'parameter': 'Active Backlogs',
        'student_val': str(s_backlogs),
        'required_val': f"<= {max_backlogs}",
        'passed': backlogs_pass,
        'difference': s_backlogs - max_backlogs,
        'unit': 'Backlogs'
    })

    # Check 3: DSA Score
    dsa_pass = s_dsa >= min_dsa
    dsa_diff = round(s_dsa - min_dsa, 1)
    if not dsa_pass:
        dsa_pct_deficit = round(((min_dsa - s_dsa) / min_dsa) * 100, 1)
        deficits.append(f"DSA & Coding score is {dsa_pct_deficit}% below threshold (Current: {s_dsa:.1f}, Cutoff: {min_dsa:.1f})")
    checks.append({
        'parameter': 'DSA Technical Score',
        'student_val': f"{s_dsa:.1f}%",
        'required_val': f"{min_dsa:.1f}%",
        'passed': dsa_pass,
        'difference': dsa_diff,
        'unit': '%'
    })

    # Check 4: Placement Readiness Index
    readiness_pass = s_readiness >= min_readiness
    readiness_diff = round(s_readiness - min_readiness, 1)
    if not readiness_pass:
        deficits.append(f"Placement Readiness Index is {abs(readiness_diff):.1f} pts below benchmark (Current: {s_readiness:.1f}, Benchmark: {min_readiness:.1f})")
    checks.append({
        'parameter': 'Placement Readiness Index',
        'student_val': f"{s_readiness:.1f}",
        'required_val': f"{min_readiness:.1f}",
        'passed': readiness_pass,
        'difference': readiness_diff,
        'unit': 'pts'
    })

    # Check 5: Soft Skills / Fluency
    soft_pass = s_soft >= min_soft
    soft_diff = round(s_soft - min_soft, 1)
    if not soft_pass:
        deficits.append(f"Interview speech & soft-skills score is {abs(soft_diff):.1f} pts below target (Current: {s_soft:.1f}, Target: {min_soft:.1f})")
    checks.append({
        'parameter': 'Interview Soft-Skills',
        'student_val': f"{s_soft:.1f}",
        'required_val': f"{min_soft:.1f}",
        'passed': soft_pass,
        'difference': soft_diff,
        'unit': 'pts'
    })

    # Check 6: Branch Eligibility
    branch_pass = ('All' in allowed_branches_str) or any(b.strip().lower() in s_branch.lower() for b in allowed_branches_str.split(','))
    if not branch_pass:
        deficits.append(f"Department '{s_branch}' is not currently in the recruiter eligible branches list ({allowed_branches_str})")
    checks.append({
        'parameter': 'Eligible Branches',
        'student_val': s_branch,
        'required_val': allowed_branches_str,
        'passed': branch_pass,
        'difference': 0,
        'unit': ''
    })

    # Overall Status Determination
    all_mandatory_passed = cgpa_pass and backlogs_pass and dsa_pass and branch_pass
    is_eligible = all_mandatory_passed and readiness_pass and soft_pass

    if is_eligible:
        status = 'ELIGIBLE'
    elif all_mandatory_passed and (not readiness_pass or not soft_pass):
        status = 'BORDERLINE'
    else:
        status = 'INELIGIBLE'

    return {
        'student': student,
        'drive': drive_info,
        'is_eligible': is_eligible,
        'status': status,
        'checks': checks,
        'deficits': deficits,
        'passed_count': sum(1 for c in checks if c['passed']),
        'total_checks': len(checks)
    }

def get_all_drives_for_student(student_id):
    """Returns all active placement drives with evaluated eligibility for the given student"""
    drives = query_db("""
        SELECT d.id, d.job_title, d.job_role, d.package_lpa, d.drive_date, d.deadline,
               d.drive_type, d.status, c.name as company_name, c.tier as company_tier, c.logo_icon,
               cr.min_cgpa, cr.max_active_backlogs, cr.min_dsa_score, cr.min_readiness_index,
               cr.required_technical_skills
        FROM placement_drives d
        JOIN companies c ON d.company_id = c.id
        LEFT JOIN drive_criteria cr ON d.id = cr.drive_id
        WHERE d.status = 'ACTIVE'
        ORDER BY d.package_lpa DESC
    """)

    apps = query_db(
        "SELECT drive_id, application_status, applied_at FROM student_applications WHERE student_id = ?",
        (student_id,)
    ) or []
    apps_by_drive = {a['drive_id']: a for a in apps}

    results = []
    for d in drives:
        eval_res = evaluate_student_drive_eligibility(student_id, d['id'])
        d_copy = dict(d)
        d_copy['eligibility'] = eval_res
        d_copy['application'] = apps_by_drive.get(d['id'])
        results.append(d_copy)

    return results

if __name__ == '__main__':
    # Test for Siddhesh Bhosale (Student ID 1) and Arpit Tale (Student ID 4)
    print("Testing eligibility for Student 1 (Siddhesh Bhosale) on Drive 1:")
    e1 = evaluate_student_drive_eligibility(1, 1)
    print("Status:", e1['status'], "| Deficits:", e1['deficits'])

    print("\nTesting eligibility for Student 4 (Arpit Tale) on Drive 1 (Google):")
    e4 = evaluate_student_drive_eligibility(4, 1)
    print("Status:", e4['status'], "| Deficits:", e4['deficits'])
