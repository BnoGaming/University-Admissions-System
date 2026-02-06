from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os
import uuid
from datetime import datetime
import random
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'default_key_for_dev')


BASE_DIR = os.getcwd()
USERS_CSV = os.path.join(BASE_DIR, 'users.csv')
APPS_CSV = os.path.join(BASE_DIR, 'applications.csv')
APPLICANTS_CSV = os.path.join(BASE_DIR, 'applicants.csv')
PROGRAMS_CSV = os.path.join(BASE_DIR, 'programs.csv')
ACADEMIC_CSV = os.path.join(BASE_DIR, 'academic_profile.csv')
ACHIEVEMENTS_CSV = os.path.join(BASE_DIR, 'student_achievements.csv')

def get_user_from_csv(email, password):
    try:
        df = pd.read_csv(USERS_CSV)
        user = df[(df['email'] == email) & (df['password_hash'] == password)]
        if not user.empty:
            return user.iloc[0].to_dict()
        return None
    except Exception as e:
        print(f"Error reading users: {e}")
        return None

def register_new_user(email, password):
    try:
        df = pd.read_csv(USERS_CSV)
        if email in df['email'].values:
            return False, "Email already exists"
        new_id = f"U{len(df) + 1001}"
        new_user = {
            "user_id": new_id,
            "email": email,
            "password_hash": password,
            "role_id": 2,
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }
        pd.DataFrame([new_user]).to_csv(USERS_CSV, mode='a', header=False, index=False)
        return True, new_id
    except Exception as e:
        return False, str(e)

def get_master_list():
    try:
        if not os.path.exists(APPS_CSV) or not os.path.exists(APPLICANTS_CSV):
            return []

        # 1. LOAD DATA (With Crash Protection)
        # on_bad_lines='skip' will ignore the broken row you created earlier
        df_apps = pd.read_csv(APPS_CSV)
        df_applicants = pd.read_csv(APPLICANTS_CSV, on_bad_lines='skip') 
        df_programs = pd.read_csv(PROGRAMS_CSV)
        df_users = pd.read_csv(USERS_CSV) # Load users to get Email correctly

        # 2. MERGE DATA
        # Merge Apps + Applicants
        merged = pd.merge(df_apps, df_applicants, on='applicant_id', how='inner')
        # Merge Programs
        merged = pd.merge(merged, df_programs, on='program_id', how='left')
        # Merge Users (To get Email properly)
        merged = pd.merge(merged, df_users[['user_id', 'email']], on='user_id', how='left')

        # 3. CLEAN UP
        final_df = merged.rename(columns={'name': 'program_name'})
        final_df['submission_date'] = pd.to_datetime(final_df['submission_date'], errors='coerce')
        final_df = final_df.sort_values(by='submission_date', ascending=False)
        final_df = final_df.fillna("Unknown")

        if 'days_to_submit' not in final_df.columns:
            final_df['days_to_submit'] = 0

        return final_df.to_dict(orient='records')

    except Exception as e:
        print(f"Data Error: {e}")
        return []

def update_status_in_csv(app_id, new_status):
    try:
        df = pd.read_csv(APPS_CSV)
        if app_id in df['application_id'].values:
            df.loc[df['application_id'] == app_id, 'status'] = new_status
            df.to_csv(APPS_CSV, index=False)
            return True
        return False
    except Exception as e:
        print(f"Error updating: {e}")
        return False

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
    
    if email == "admin@mm.edu" and password == "admin123":
        session['user_id'] = "ADMIN_001"
        session['role'] = 1
        return redirect(url_for('admin_dashboard'))
    
    user = get_user_from_csv(email, password)
    if user:
        session['user_id'] = user['user_id']
        session['role'] = 2
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
    # Power BI Link
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
    
    # Sort by submission date descending (newest first)
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
    
    if update_status_in_csv(data.get('app_id'), new_status):
        return jsonify({"success": True, "new_status": new_status})
    return jsonify({"success": False})

@app.route('/submit_application', methods=['POST'])
def submit_application():
    try:
        # 1. Gather Personal Data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form.get('dob', '2000-01-01')
        city = request.form.get('city', 'Unknown')
        country = request.form.get('country', 'Unknown')
        gender = request.form.get('gender', 'Other')
        
        # 2. Gather Academic Data (Required Fields)
        gpa = float(request.form.get('gpa', 0.0))
        sat = int(request.form.get('sat_score', 0))
        is_first_gen = 'is_first_gen' in request.form
        scholarship = 'scholarship' in request.form
        achievement_text = request.form.get('achievement', '').strip()
        
        program_id = request.form['program_id']
        sop = request.form.get('sop_text', '')

        # 3. Generate IDs
        # (We use try/except on reading to handle empty files safely)
        try:
            df_apps = pd.read_csv(APPS_CSV)
            last_app_num = int(df_apps['application_id'].iloc[-1].replace('APP', '')) 
        except:
            last_app_num = 9000
        new_app_id = f"APP{last_app_num + 1}"

        try:
            df_applicants = pd.read_csv(APPLICANTS_CSV, on_bad_lines='skip')
            last_aid_num = int(df_applicants['applicant_id'].iloc[-1].replace('A', ''))
        except:
            last_aid_num = 5000
        new_aid = f"A{last_aid_num + 1}"

        # 4. Save to APPLICANTS.CSV (Strict 10 Columns)
        # Note: We do NOT save 'email' here to avoid breaking the schema. 
        # Email is linked via user_id in users.csv.
        new_applicant = {
            "applicant_id": new_aid,
            "user_id": session.get('user_id', 'Unknown'),
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob,
            "age_range_id": 1, 
            "gender": gender, 
            "country": country,
            "city": city,
            "is_first_generation": is_first_gen
        }
        pd.DataFrame([new_applicant]).to_csv(APPLICANTS_CSV, mode='a', header=False, index=False)

        # 5. Save to APPLICATIONS.CSV
        new_application = {
            "application_id": new_app_id,
            "applicant_id": new_aid,
            "program_id": program_id,
            "status": "Waitlisted",
            "submission_date": datetime.now().strftime("%Y-%m-%d"),
            "days_to_submit": 0,
            "fees_paid": False,
            "sop_text": sop,
            "admin_comments": ""
        }
        pd.DataFrame([new_application]).to_csv(APPS_CSV, mode='a', header=False, index=False)

        # 6. Save to ACADEMIC_PROFILE.CSV (The proper place for GPA/SAT)
        try:
            df_acad = pd.read_csv(ACADEMIC_CSV)
            last_pid = int(df_acad['profile_id'].iloc[-1].replace('P', ''))
        except:
            last_pid = 1000
            
        new_academic = {
            "profile_id": f"P{last_pid + 1}",
            "applicant_id": new_aid,
            "high_school_gpa": gpa,
            "sat_score": sat,
            "scholarship_requested": scholarship
        }
        # Check if file exists to determine if we need a header
        header_mode = not os.path.exists(ACADEMIC_CSV)
        pd.DataFrame([new_academic]).to_csv(ACADEMIC_CSV, mode='a', header=header_mode, index=False)

        # 7. Save to STUDENT_ACHIEVEMENTS.CSV (The proper place for Awards)
        if achievement_text:
            try:
                df_achieve = pd.read_csv(ACHIEVEMENTS_CSV)
            except:
                pass
            
            new_achievement = {
                "id": str(uuid.uuid4()),
                "applicant_id": new_aid,
                "achievement_name": achievement_text,
                "date_awarded": datetime.now().strftime("%Y-%m-%d")
            }
            header_mode_ach = not os.path.exists(ACHIEVEMENTS_CSV)
            pd.DataFrame([new_achievement]).to_csv(ACHIEVEMENTS_CSV, mode='a', header=header_mode_ach, index=False)

        return f"""
        <div style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: green;">Application Submitted!</h1>
            <p>Your Application ID is <strong>{new_app_id}</strong></p>
            <p>We have recorded your GPA ({gpa}) and Scholarship Request.</p>
            <br>
            <a href='/students' style="padding: 10px 20px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px;">View Status</a>
        </div>
        """
    
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p><a href='/apply'>Try Again</a>"

@app.route('/apply')
def apply():
    try:
        df = pd.read_csv(PROGRAMS_CSV)
        programs = df.to_dict(orient='records')
    except:
        programs = []
    return render_template('apply.html', programs=programs)

@app.route('/my_application')
def my_application():
    if session.get('role') != 2:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    try:
        # Get user's applications
        df_apps = pd.read_csv(APPS_CSV)
        df_applicants = pd.read_csv(APPLICANTS_CSV, on_bad_lines='skip')
        df_programs = pd.read_csv(PROGRAMS_CSV)
        
        # Filter by user
        user_applicants = df_applicants[df_applicants['user_id'] == user_id]
        
        if user_applicants.empty:
            return render_template('my_application.html', applications=[])
        
        # Merge to get full details
        merged = pd.merge(df_apps, user_applicants, on='applicant_id', how='inner')
        merged = pd.merge(merged, df_programs, on='program_id', how='left')
        merged = merged.rename(columns={'name': 'program_name'})
        merged = merged.sort_values(by='submission_date', ascending=False)
        
        applications = merged.to_dict(orient='records')
        
        return render_template('my_application.html', applications=applications)
        
    except Exception as e:
        print(f"Error loading applications: {e}")
        return render_template('my_application.html', applications=[])

@app.route('/programs')
def programs():
    if session.get('role') != 1:
        return redirect(url_for('login'))
    
    try:
        df = pd.read_csv(PROGRAMS_CSV)
        if 'active_students' not in df.columns:
            df['active_students'] = df['program_id'].apply(lambda x: random.randint(50, 300))
        programs_list = df.to_dict(orient='records')
    except:
        programs_list = []
        
    return render_template('programs.html', programs=programs_list)

if __name__ == '__main__':
    app.run(debug=True, port=5000)