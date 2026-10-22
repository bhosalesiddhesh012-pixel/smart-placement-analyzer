import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
import sqlite3
import config

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False
    MySQLError = Exception

_active_backend = None

def detect_backend():
    global _active_backend
    if _active_backend is not None:
        return _active_backend

    if config.DB_TYPE == 'sqlite':
        _active_backend = 'sqlite'
        return _active_backend

    if config.DB_TYPE in ('mysql', 'auto') and HAS_MYSQL:
        try:
            conn = mysql.connector.connect(
                host=config.MYSQL_HOST,
                port=config.MYSQL_PORT,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                connection_timeout=2
            )
            if conn.is_connected():
                conn.close()
                _active_backend = 'mysql'
                return _active_backend
        except Exception:
            pass

    _active_backend = 'sqlite'
    return _active_backend

def get_db_info():
    backend = detect_backend()
    if backend == 'mysql':
        return {
            'backend': 'MySQL',
            'host': f"{config.MYSQL_HOST}:{config.MYSQL_PORT}",
            'database': config.MYSQL_DB,
            'user': config.MYSQL_USER,
            'is_fallback': False
        }
    else:
        return {
            'backend': 'SQLite (Embedded 3NF)',
            'path': config.SQLITE_PATH,
            'database': os.path.basename(config.SQLITE_PATH),
            'is_fallback': (config.DB_TYPE == 'auto')
        }

def get_connection():
    backend = detect_backend()
    if backend == 'mysql':
        return mysql.connector.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB,
            autocommit=True
        )
    else:
        os.makedirs(os.path.dirname(config.SQLITE_PATH), exist_ok=True)
        conn = sqlite3.connect(config.SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

def query_db(query, args=(), one=False):
    backend = detect_backend()
    conn = get_connection()
    try:
        if backend == 'mysql':
            cursor = conn.cursor(dictionary=True)
            mysql_query = query.replace('?', '%s')
            cursor.execute(mysql_query, args)
            rv = cursor.fetchall()
            cursor.close()
            return (rv[0] if rv else None) if one else rv
        else:
            cur = conn.cursor()
            sqlite_query = query.replace('%s', '?')
            cur.execute(sqlite_query, args)
            rv = [dict(row) for row in cur.fetchall()]
            cur.close()
            return (rv[0] if rv else None) if one else rv
    finally:
        conn.close()

def execute_db(query, args=(), commit=True):
    backend = detect_backend()
    conn = get_connection()
    try:
        if backend == 'mysql':
            cursor = conn.cursor()
            mysql_query = query.replace('?', '%s')
            cursor.execute(mysql_query, args)
            last_id = cursor.lastrowid
            affected = cursor.rowcount
            if commit:
                conn.commit()
            cursor.close()
            return last_id or affected
        else:
            cur = conn.cursor()
            sqlite_query = query.replace('%s', '?')
            cur.execute(sqlite_query, args)
            last_id = cur.lastrowid
            affected = cur.rowcount
            if commit:
                conn.commit()
            cur.close()
            return last_id or affected
    finally:
        conn.close()

def init_db():
    backend = detect_backend()
    if backend == 'mysql':
        conn = mysql.connector.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD
        )
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DB} DEFAULT CHARACTER SET utf8mb4;")
        conn.commit()
        cur.close()
        conn.close()

        schema_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        conn = get_connection()
        cur = conn.cursor()
        for statement in sql_script.split(';'):
            stmt = statement.strip()
            if stmt and not stmt.upper().startswith('CREATE DATABASE') and not stmt.upper().startswith('USE'):
                try:
                    cur.execute(stmt)
                except Exception:
                    pass
        conn.commit()

        # Lightweight migration for pre-existing MySQL databases
        for alter_stmt in (
            "ALTER TABLE companies ADD COLUMN min_cgpa_cutoff DECIMAL(4,2) NOT NULL DEFAULT 6.0",
            "ALTER TABLE companies ADD COLUMN min_dsa_cutoff DECIMAL(5,2) NOT NULL DEFAULT 50.0",
            "ALTER TABLE companies ADD COLUMN min_readiness_cutoff DECIMAL(5,2) NOT NULL DEFAULT 55.0",
        ):
            try:
                cur.execute(alter_stmt)
                conn.commit()
            except Exception:
                pass  # Column already exists

        cur.close()
        conn.close()
        print("MySQL database initialized successfully.")
    else:
        conn = get_connection()
        cur = conn.cursor()
        schema = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'STUDENT',
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            roll_no TEXT NOT NULL UNIQUE,
            gr_no TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            department TEXT NOT NULL DEFAULT 'Computer Engineering',
            semester INTEGER NOT NULL DEFAULT 3,
            cgpa REAL NOT NULL,
            ssc_percentage REAL NOT NULL,
            hsc_percentage REAL NOT NULL,
            active_backlogs INTEGER NOT NULL DEFAULT 0,
            history_backlogs INTEGER NOT NULL DEFAULT 0,
            dsa_score REAL NOT NULL DEFAULT 0.0,
            leetcode_solved INTEGER NOT NULL DEFAULT 0,
            hackathons_won INTEGER NOT NULL DEFAULT 0,
            projects_count INTEGER NOT NULL DEFAULT 0,
            certifications_count INTEGER NOT NULL DEFAULT 0,
            soft_skills_score REAL DEFAULT 0.0,
            placement_readiness_index REAL DEFAULT 0.0,
            target_tier TEXT DEFAULT 'Uninitialized',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            domain TEXT NOT NULL,
            tier TEXT NOT NULL,
            headquarters TEXT,
            website TEXT,
            logo_icon TEXT DEFAULT 'fa-building',
            min_package_lpa REAL NOT NULL,
            max_package_lpa REAL NOT NULL,
            min_cgpa_cutoff REAL NOT NULL DEFAULT 6.0,
            min_dsa_cutoff REAL NOT NULL DEFAULT 50.0,
            min_readiness_cutoff REAL NOT NULL DEFAULT 55.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS placement_drives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            job_role TEXT NOT NULL,
            package_lpa REAL NOT NULL,
            drive_date TEXT NOT NULL,
            deadline TEXT NOT NULL,
            location TEXT DEFAULT 'On Campus / Hybrid',
            drive_type TEXT DEFAULT 'Full Time',
            description TEXT,
            status TEXT DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS drive_criteria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drive_id INTEGER NOT NULL UNIQUE,
            min_cgpa REAL NOT NULL DEFAULT 7.0,
            max_active_backlogs INTEGER NOT NULL DEFAULT 0,
            min_dsa_score REAL NOT NULL DEFAULT 60.0,
            min_readiness_index REAL NOT NULL DEFAULT 65.0,
            min_soft_skills_score REAL NOT NULL DEFAULT 60.0,
            allowed_branches TEXT DEFAULT 'Computer Engineering, IT, AI and DS',
            required_technical_skills TEXT DEFAULT 'Data Structures, Algorithms, Python/Java, SQL',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (drive_id) REFERENCES placement_drives(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS student_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            drive_id INTEGER NOT NULL,
            is_eligible INTEGER NOT NULL DEFAULT 0,
            eligibility_status TEXT NOT NULL,
            deficit_summary_json TEXT,
            application_status TEXT DEFAULT 'APPLIED',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (drive_id) REFERENCES placement_drives(id) ON DELETE CASCADE,
            UNIQUE (student_id, drive_id)
        );
        CREATE TABLE IF NOT EXISTS readiness_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            readiness_score REAL NOT NULL,
            predicted_tier TEXT NOT NULL,
            shap_values_json TEXT NOT NULL,
            base_value REAL NOT NULL,
            feature_contributions_json TEXT NOT NULL,
            evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS audio_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            prompt_topic TEXT NOT NULL,
            audio_filename TEXT NOT NULL,
            pitch_mean_hz REAL NOT NULL,
            pitch_std_hz REAL NOT NULL,
            speech_duration_sec REAL NOT NULL,
            pause_duration_sec REAL NOT NULL,
            pause_ratio REAL NOT NULL,
            speaking_rate_wpm REAL NOT NULL,
            vocal_energy REAL NOT NULL,
            soft_skills_score REAL NOT NULL,
            confidence_level TEXT NOT NULL,
            feedback_json TEXT NOT NULL,
            evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS actionable_roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            target_tier TEXT NOT NULL,
            weakness_areas_json TEXT NOT NULL,
            dsa_plan_json TEXT NOT NULL,
            project_recommendations_json TEXT NOT NULL,
            interview_prep_json TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS dsa_quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            quiz_score REAL NOT NULL,
            previous_dsa_score REAL,
            updated_dsa_score REAL NOT NULL,
            topic_breakdown_json TEXT,
            taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS student_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            doc_type TEXT NOT NULL,
            title TEXT NOT NULL,
            file_path TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_size_kb INTEGER DEFAULT 0,
            mime_type TEXT,
            extracted_data_json TEXT,
            is_verified INTEGER NOT NULL DEFAULT 0,
            verified_by TEXT,
            verified_at TIMESTAMP,
            verification_notes TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        """
        cur.executescript(schema)
        conn.commit()

        # ---- Lightweight migration for pre-existing SQLite DB files ----
        # (CREATE TABLE IF NOT EXISTS above does not add new columns to a
        # companies table that already existed before this feature was added.)
        for alter_stmt in (
            "ALTER TABLE companies ADD COLUMN min_cgpa_cutoff REAL NOT NULL DEFAULT 6.0",
            "ALTER TABLE companies ADD COLUMN min_dsa_cutoff REAL NOT NULL DEFAULT 50.0",
            "ALTER TABLE companies ADD COLUMN min_readiness_cutoff REAL NOT NULL DEFAULT 55.0",
            """CREATE TABLE IF NOT EXISTS student_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                doc_type TEXT NOT NULL,
                title TEXT NOT NULL,
                file_path TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size_kb INTEGER DEFAULT 0,
                mime_type TEXT,
                extracted_data_json TEXT,
                is_verified INTEGER NOT NULL DEFAULT 0,
                verified_by TEXT,
                verified_at TIMESTAMP,
                verification_notes TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )""",
        ):
            try:
                cur.execute(alter_stmt)
                conn.commit()
            except Exception:
                pass  # Column already exists

        conn.close()
        print("SQLite 3NF database initialized successfully.")
