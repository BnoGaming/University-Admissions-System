from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pyodbc
from datetime import datetime
import uuid
import random
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'default_key_for_dev')

# SQL Server Connection Configuration
# UPDATE THESE WITH YOUR SQL SERVER DETAILS
DB_CONFIG = {
    'server': 'localhost',  # or your server name
    'database': 'UniversityAdmissions',
    'username': 'your_username',
    'password': 'your_password',
    'driver': '{ODBC Driver 17 for SQL Server}'
}
# Alternative connection string for Windows Authentication:
CONNECTION_STRING = f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};Trusted_Connection=yes;"

# CONNECTION_STRING = f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};UID={DB_CONFIG['username']};PWD={DB_CONFIG['password']}"

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def get_user_from_db(email, password):
    """Authenticate user from database"""
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        query = """
            SELECT user_id, email, role_id 
            FROM users 
            WHERE email = ? AND password_hash = ?
        """
        cursor.execute(query, (email, password))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'user_id': row.user_id,
                'email': row.email,
                'role_id': row.role_id
            }
        return None
    except Exception as e:
        print(f"Error reading users: {e}")
        return None

def register_new_user(email, password):
    """Register a new user in the database"""
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Database connection failed"
        
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return False, "Email already exists"
        
        # Generate new user ID
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        new_id = f"U{count + 1001}"
        
        # Insert new user
        query = """
            INSERT INTO users (user_id, email, password_hash, role_id, created_at)
            VALUES (?, ?, ?, 2, ?)
        """
        cursor.execute(query, (new_id, email, password, datetime.now().date()))
        conn.commit()
        conn.close()
        
        return True, new_id
    except Exception as e:
        print(f"Registration error: {e}")
        return False, str(e)

def get_master_list():
    """Get comprehensive application list with all related data"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        cursor = conn.cursor()
        query = """
            SELECT 
                app.application_id,
                app.applicant_id,
                app.status,
                app.submission_date,
                app.days_to_submit,
                app.fees_paid,
                app.sop_text,
                app.admin_comments,
                a.user_id,
                a.first_name,
                a.last_name,
                a.dob,
                a.gender,
                a.country,
                a.city,
                a.is_first_generation,
                p.program_id,
                p.name AS program_name,
                p.dept,
                u.email
            FROM applications app
            INNER JOIN applicants a ON app.applicant_id = a.applicant_id
            LEFT JOIN programs p ON app.program_id = p.program_id
            LEFT JOIN users u ON a.user_id = u.user_id
            ORDER BY app.submission_date DESC
        """
        cursor.execute(query)
        
        columns = [column[0] for column in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            # Convert date to string for JSON serialization
            if row_dict.get('submission_date'):
                row_dict['submission_date'] = row_dict['submission_date'].strftime('%Y-%m-%d')
            if row_dict.get('dob'):
                row_dict['dob'] = row_dict['dob'].strftime('%Y-%m-%d')
            # Handle None values
            for key in row_dict:
                if row_dict[key] is None:
                    row_dict[key] = 'Unknown' if isinstance(key, str) else 0
            results.append(row_dict)
        
        conn.close()
        return results
    except Exception as e:
        print(f"Data Error: {e}")
        return []

def update_status_in_db(app_id, new_status):
    """Update application status in database"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        query = "UPDATE applications SET status = ? WHERE application_id = ?"
        cursor.execute(query, (new_status, app_id))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        
        return rows_affected > 0
    except Exception as e:
        print(f"Error updating: {e}")
        return False

def get_programs_list():
    """Get all programs from database"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        cursor = conn.cursor()
        cursor.execute("SELECT program_id, name, dept, median_days FROM programs ORDER BY name")
        
        programs = []
        for row in cursor.fetchall():
            programs.append({
                'program_id': row.program_id,
                'name': row.name,
                'dept': row.dept,
                'median_days': row.median_days,
                'active_students': random.randint(50, 300)  # Mock data
            })
        
        conn.close()
        return programs
    except Exception as e:
        print(f"Error fetching programs: {e}")
        return []

# --- ROUTES ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_action', methods=['POST'])
def login_action():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Admin login
    if email == "admin@mm.edu" and password == "admin123":
        session['user_id'] = "ADMIN_001"
        session['role'] = 1
        return redirect(url_for('admin_dashboard'))
    
    # User login
    user = get_user_from_db(email, password)
    if user:
        session['user_id'] = user['user_id']
        session['role'] = user['role_id']
        return redirect(url_for('my_application'))
    
    return render_template('login.html', error="Invalid credentials")

@app.route('/register_action', methods=['POST'])
def register_action():
    email = request.form.get('reg_email')
    password = request.form.get('reg_password')
    success, message = register_new_user(email, password)
    if success:
        return render_template('login.html', success="Registration successful! Please login.")
    else:
        return render_template('login.html', error=f"Registration failed: {message}")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 1: 
        return redirect(url_for('login'))
    
    applicants_list = get_master_list()
    pbi_url = os.getenv('PBI_EMBED_URL')
    return render_template('dashboard.html', applicants=applicants_list[:50], pbi_url=pbi_url)

@app.route('/students')
def students():
    if session.get('role') != 1:
        return redirect(url_for('login'))
    
    all_applicants = get_master_list()
    
    # Filter only 2026 applications
    current_year_applicants = [
        app for app in all_applicants 
        if app.get('submission_date') and str(app['submission_date']).startswith('2026')
    ]
    
    # Sort by submission date descending
    current_year_applicants.sort(
        key=lambda x: x.get('submission_date', ''), 
        reverse=True
    )
    
    return render_template('students.html', applicants=current_year_applicants)

@app.route('/update_application', methods=['POST'])
def update_application():
    if session.get('role') != 1:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    data = request.json
    status_map = {"accept": "Accepted", "reject": "Rejected"}
    new_status = status_map.get(data.get('action'))
    
    if update_status_in_db(data.get('app_id'), new_status):
        return jsonify({"success": True, "new_status": new_status})
    return jsonify({"success": False})

@app.route('/submit_application', methods=['POST'])
def submit_application():
    try:
        conn = get_db_connection()
        if not conn:
            return "<h1>Database Error</h1><p>Could not connect to database</p><a href='/apply'>Try Again</a>"
        
        cursor = conn.cursor()
        
        # 1. Gather Form Data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form.get('dob', '2000-01-01')
        city = request.form.get('city', 'Unknown')
        country = request.form.get('country', 'Unknown')
        gender = request.form.get('gender', 'Other')
        
        gpa = float(request.form.get('gpa', 0.0))
        sat = int(request.form.get('sat_score', 0))
        is_first_gen = 1 if 'is_first_gen' in request.form else 0
        scholarship = 1 if 'scholarship' in request.form else 0
        achievement_text = request.form.get('achievement', '').strip()
        
        program_id = request.form['program_id']
        sop = request.form.get('sop_text', '')
        
        # 2. Generate IDs
        # New Applicant ID
        cursor.execute("SELECT COUNT(*) FROM applicants")
        last_aid_num = cursor.fetchone()[0] + 5000
        new_aid = f"A{last_aid_num + 1}"
        
        # New Application ID
        cursor.execute("SELECT COUNT(*) FROM applications")
        last_app_num = cursor.fetchone()[0] + 9000
        new_app_id = f"APP{last_app_num + 1}"
        
        # 3. Insert into APPLICANTS table
        applicant_query = """
            INSERT INTO applicants (applicant_id, user_id, first_name, last_name, dob, 
                                   age_range_id, gender, country, city, is_first_generation)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
        """
        cursor.execute(applicant_query, (
            new_aid, session.get('user_id', 'Unknown'), first_name, last_name, 
            dob, gender, country, city, is_first_gen
        ))
        
        # 4. Insert into APPLICATIONS table
        application_query = """
            INSERT INTO applications (application_id, applicant_id, program_id, status,
                                     submission_date, days_to_submit, fees_paid, sop_text, admin_comments)
            VALUES (?, ?, ?, 'Waitlisted', ?, 0, 0, ?, '')
        """
        cursor.execute(application_query, (
            new_app_id, new_aid, program_id, datetime.now().date(), sop
        ))
        
        # 5. Insert into ACADEMIC_PROFILE table
        cursor.execute("SELECT COUNT(*) FROM academic_profile")
        profile_count = cursor.fetchone()[0] + 1000
        new_profile_id = f"P{profile_count + 1}"
        
        academic_query = """
            INSERT INTO academic_profile (profile_id, applicant_id, high_school_gpa, 
                                         sat_score, scholarship_requested)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(academic_query, (new_profile_id, new_aid, gpa, sat, scholarship))
        
        # 6. Insert into STUDENT_ACHIEVEMENTS table (if achievement provided)
        if achievement_text:
            achievement_id = str(uuid.uuid4())
            achievement_query = """
                INSERT INTO student_achievements (id, applicant_id, achievement_name, date_awarded)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(achievement_query, (achievement_id, new_aid, achievement_text, datetime.now().date()))
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        return f"""
        <div style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: green;">Application Submitted Successfully!</h1>
            <p>Your Application ID is <strong>{new_app_id}</strong></p>
            <p>Applicant ID: <strong>{new_aid}</strong></p>
            <p>We have recorded your GPA ({gpa}) and SAT Score ({sat}).</p>
            <br>
            <a href='/my_application' style="padding: 10px 20px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px;">View My Applications</a>
            <br><br>
            <a href='/apply' style="padding: 10px 20px; background: #10b981; color: white; text-decoration: none; border-radius: 5px;">Submit Another Application</a>
        </div>
        """
    
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return f"<h1>Error</h1><p>{str(e)}</p><a href='/apply'>Try Again</a>"

@app.route('/apply')
def apply():
    programs = get_programs_list()
    return render_template('apply.html', programs=programs)

@app.route('/my_application')
def my_application():
    if session.get('role') != 2:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    try:
        conn = get_db_connection()
        if not conn:
            return render_template('my_application.html', applications=[])
        
        cursor = conn.cursor()
        query = """
            SELECT 
                app.application_id,
                app.status,
                app.submission_date,
                app.fees_paid,
                app.sop_text,
                a.first_name,
                a.last_name,
                p.name AS program_name,
                p.dept
            FROM applications app
            INNER JOIN applicants a ON app.applicant_id = a.applicant_id
            LEFT JOIN programs p ON app.program_id = p.program_id
            WHERE a.user_id = ?
            ORDER BY app.submission_date DESC
        """
        cursor.execute(query, (user_id,))
        
        applications = []
        for row in cursor.fetchall():
            applications.append({
                'application_id': row.application_id,
                'status': row.status,
                'submission_date': row.submission_date.strftime('%Y-%m-%d') if row.submission_date else 'N/A',
                'fees_paid': row.fees_paid,
                'sop_text': row.sop_text,
                'first_name': row.first_name,
                'last_name': row.last_name,
                'program_name': row.program_name if row.program_name else 'N/A'
            })
        
        conn.close()
        return render_template('my_application.html', applications=applications)
        
    except Exception as e:
        print(f"Error loading applications: {e}")
        return render_template('my_application.html', applications=[])

@app.route('/programs')
def programs():
    if session.get('role') != 1:
        return redirect(url_for('login'))
    
    programs_list = get_programs_list()
    return render_template('programs.html', programs=programs_list)

if __name__ == '__main__':
    app.run(debug=True, port=5000)