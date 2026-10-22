import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-placement-vit-sy-k-17-secret-key-2026')

# Database Settings
DB_TYPE = os.environ.get('DB_TYPE', 'auto')  # 'auto', 'mysql', or 'sqlite'
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DB', 'smart_placement_db')

SQLITE_PATH = os.environ.get('SQLITE_PATH', str(BASE_DIR / 'database' / 'smart_placement.db'))

# File Uploads
UPLOAD_FOLDER = str(BASE_DIR / 'static' / 'audio')
DOCUMENTS_FOLDER = str(BASE_DIR / 'uploads' / 'certificates')
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

# Automated Email & TPO Alerts
SMTP_HOST = os.environ.get('SMTP_HOST', 'localhost')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 1025))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
SMTP_FROM = os.environ.get('SMTP_FROM', 'placement-portal@vit.edu')
TPO_EMAIL = os.environ.get('TPO_EMAIL', 'sachin.jadhav@vit.edu')

# ML Model
MODEL_PATH = str(BASE_DIR / 'ml' / 'placement_model.joblib')

# Matplotlib cache fix
os.environ.setdefault('MPLCONFIGDIR', '/tmp/mpl_cache')
