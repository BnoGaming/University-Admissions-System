import pandas as pd
import random
from faker import Faker
from datetime import date, timedelta
from datetime import datetime as dt_module
import uuid

fake = Faker()
Faker.seed(42)

# --- 1. CONFIGURATION: INDIAN COLLEGE REALISTIC TRENDS ---
# Indian colleges typically see applications throughout the year with peaks during admission seasons
YEARLY_STATS = {
    2017: {"apps": 450,  "accept_rate": 0.68, "yield_rate": 0.82},
    2018: {"apps": 520,  "accept_rate": 0.65, "yield_rate": 0.80},
    2019: {"apps": 480,  "accept_rate": 0.70, "yield_rate": 0.78},
    2020: {"apps": 650,  "accept_rate": 0.62, "yield_rate": 0.75},  # COVID spike
    2021: {"apps": 850,  "accept_rate": 0.58, "yield_rate": 0.72},  # Post-COVID growth
    2022: {"apps": 1100, "accept_rate": 0.52, "yield_rate": 0.68},
    2023: {"apps": 1450, "accept_rate": 0.48, "yield_rate": 0.62},
    2024: {"apps": 1850, "accept_rate": 0.42, "yield_rate": 0.58},
    2025: {"apps": 2300, "accept_rate": 0.38, "yield_rate": 0.52},
    2026: {"apps": 100,  "accept_rate": 0.35, "yield_rate": 0.48}   # Partial year till yesterday
}

PROGRAMS = [
    # Fast to apply (High demand/First come first serve)
    {"program_id": "P101", "name": "Bachelor in Communication", "dept": "Arts", "median_days": 35},
    {"program_id": "P102", "name": "Bachelor in Design", "dept": "Design", "median_days": 28},
    
    # Average speed
    {"program_id": "P103", "name": "Preparatory Year", "dept": "General", "median_days": 45},
    {"program_id": "P109", "name": "Bachelor in Computer Science", "dept": "Engineering", "median_days": 50},
    {"program_id": "P108", "name": "Bachelor in Economics", "dept": "Economics", "median_days": 48},
    
    # Slow to apply (Requires more documents/Research)
    {"program_id": "P104", "name": "Master in Engineering", "dept": "Engineering", "median_days": 75},
    {"program_id": "P105", "name": "eMBA Strategy", "dept": "Business", "median_days": 90},
    {"program_id": "P106", "name": "Master in Marketing", "dept": "Business", "median_days": 85},
    {"program_id": "P107", "name": "Post Master in Physics", "dept": "Science", "median_days": 60}
]

AGE_RANGES = [
    {"range_id": 1, "min": 17, "max": 18, "label": "17-18"},
    {"range_id": 2, "min": 19, "max": 21, "label": "19-21"},
    {"range_id": 3, "min": 22, "max": 25, "label": "22-25"},
    {"range_id": 4, "min": 26, "max": 30, "label": "26-30"},
    {"range_id": 5, "min": 31, "max": 99, "label": "30+"}
]

ACHIEVEMENT_TYPES = [
    "State Level Debate Champion", "Math Olympiad Gold", "Hackathon Winner", 
    "Published Research Paper", "School Captain", "Volunteer of the Year", 
    "National Sports Player", "Music Grade 8", "Robotics Club President"
]

# --- 2. REALISTIC SOP GENERATOR ---
def generate_sop(program_name, achievement):
    """Stitches together a coherent, semi-unique SOP based on context."""
    
    openers = [
        f"I have always been deeply fascinated by the world of {program_name}.",
        f"From a young age, my curiosity has driven me towards {program_name}.",
        f"My journey in {program_name} began when I first encountered real-world challenges in this field.",
        "The intersection of innovation and practical application is where I thrive."
    ]
    
    middles = [
        f"My recent success as a {achievement} taught me the value of discipline and leadership.",
        "I have consistently sought opportunities to expand my knowledge beyond the classroom.",
        f"I believe that the curriculum at your university is the perfect environment to refine my skills in {program_name}.",
        "I am eager to learn from your distinguished faculty and contribute to the research initiatives on campus."
    ]
    
    closers = [
        "I am excited about the possibility of joining your diverse student community.",
        "I am confident that I can make a meaningful contribution to the university.",
        "Thank you for considering my application; I look forward to the opportunity to excel here.",
        "I hope to bring my unique perspective and dedication to your upcoming cohort."
    ]
    
    return f"{random.choice(openers)} {random.choice(middles)} {random.choice(closers)}"

# --- 3. HELPER FUNCTIONS ---
def get_age_range_id(dob, current_year):
    age = current_year - dob.year
    for r in AGE_RANGES:
        if r["min"] <= age <= r["max"]:
            return r["range_id"]
    return 5

def generate_seasonal_date(year):
    """
    Indian college admission pattern:
    - Jan-Feb: High (Board exam results + application season start)
    - Mar-Apr: Peak (Main admission season)
    - May-Jun: Very High (Summer admissions + late applications)
    - Jul-Aug: Medium (Monsoon semester intake)
    - Sep-Oct: Low (Academic year running)
    - Nov-Dec: Medium (Early applications for next cycle)
    """
    month_weights = [0.12, 0.12, 0.15, 0.16, 0.14, 0.13, 0.06, 0.05, 0.03, 0.02, 0.04, 0.08]
    month = random.choices(range(1, 13), weights=month_weights)[0]
    
    if month == 2: 
        day = random.randint(1, 28)
    elif month in [4, 6, 9, 11]: 
        day = random.randint(1, 30)
    else: 
        day = random.randint(1, 31)
    
    return date(year, month, day)

# --- 4. MAIN GENERATION LOOP ---
users_data = []
applicants_data = []
applications_data = []
academic_data = []
achievements_data = []

# ID Counters
g_uid, g_aid, g_app_id, g_pid = 1000, 5000, 9000, 1

print("Generating Data with Realistic Indian College Trends...")

TODAY = dt_module.now().date()

for year, stats in YEARLY_STATS.items():
    print(f"  Processing {year}: {stats['apps']} applicants (Accept Rate: {stats['accept_rate']:.0%})")
    
    for _ in range(stats['apps']):
        g_uid += 1
        g_aid += 1
        g_app_id += 1
        g_pid += 1
        
        # Dimensions
        user_id = f"U{g_uid}"
        applicant_id = f"A{g_aid}"
        
        # Determine Status based on Year's specific rates
        is_accepted = random.random() < stats['accept_rate']
        
        if is_accepted:
            # If accepted, do they enroll? (Yield Rate)
            is_enrolled = random.random() < stats['yield_rate']
            status = 'Enrolled' if is_enrolled else 'Accepted'
            if year < 2025 and status == 'Accepted': 
                status = 'Lost'  # Old "Accepted" offers that didn't enroll are now "Lost"
        else:
            status = random.choices(['Rejected', 'Waitlisted'], weights=[0.8, 0.2])[0]
            if year < 2025 and status == 'Waitlisted':
                status = 'Rejected'  # Old waitlists are closed

        # Generate Context
        program = random.choice(PROGRAMS)
        
        # Generate submission date throughout the calendar year
        submission_date = generate_seasonal_date(year)
        
        # For 2026, ensure we don't exceed yesterday's date
        if year == 2026:
            # Generate dates only from Jan 1, 2026 to yesterday
            days_since_start = (TODAY - date(2026, 1, 1)).days
            if days_since_start <= 0:
                continue
            random_day = random.randint(0, days_since_start - 1)
            submission_date = date(2026, 1, 1) + timedelta(days=random_day)
        
        # Skip if submission date is in the future
        if submission_date > TODAY:
            continue
        
        # Calculate days to submit (just for tracking purposes, not tied to cycle open date)
        days_to_submit = int(random.gauss(program["median_days"], 20))
        days_to_submit = max(1, min(days_to_submit, 250))
        
        dob = fake.date_of_birth(minimum_age=17, maximum_age=28)
        achievement_name = random.choice(ACHIEVEMENT_TYPES)
        
        # --- POPULATE TABLES (SQL SCHEMA FORMAT) ---
        
        # Users table
        users_data.append({
            "user_id": user_id,
            "email": fake.unique.email(),
            "password_hash": "hash_placeholder",
            "role_id": 2,
            "created_at": submission_date
        })
        
        # Applicants table
        applicants_data.append({
            "applicant_id": applicant_id,
            "user_id": user_id,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "dob": dob,
            "age_range_id": get_age_range_id(dob, year),
            "gender": random.choices(['Male', 'Female', 'Other'], weights=[0.48, 0.48, 0.04])[0],
            "country": random.choice(['USA', 'India', 'China', 'France', 'UK', 'Nigeria', 'Canada']),
            "city": fake.city(),
            "is_first_generation": random.choice([True, False, False])
        })
        
        # Applications table (Fact)
        # Fees Logic: Enrolled MUST have paid. Accepted MIGHT have paid.
        fees_paid = True if status == 'Enrolled' else (random.choice([True, False]) if status == 'Accepted' else False)
        
        applications_data.append({
            "application_id": f"APP{g_app_id}",
            "applicant_id": applicant_id,
            "program_id": program["program_id"],
            "status": status,
            "submission_date": submission_date,
            "days_to_submit": days_to_submit,
            "fees_paid": fees_paid,
            "sop_text": generate_sop(program["name"], achievement_name),
            "admin_comments": ""
        })
        
        # Academic Profile
        # Correlate scores with status (Enrolled usually higher scores)
        if status in ['Enrolled', 'Accepted', 'Lost']:
            gpa = round(random.uniform(3.4, 4.0), 2)
            sat = random.randint(1300, 1600)
        else:
            gpa = round(random.uniform(2.3, 3.6), 2)
            sat = random.randint(900, 1400)
            
        academic_data.append({
            "profile_id": f"P{g_pid}",
            "applicant_id": applicant_id,
            "high_school_gpa": gpa,
            "sat_score": sat,
            "scholarship_requested": random.choice([True, False])
        })
        
        # Student Achievements
        achievements_data.append({
            "id": str(uuid.uuid4()),
            "applicant_id": applicant_id,
            "achievement_name": achievement_name,
            "date_awarded": fake.date_between(start_date='-3y', end_date='-1y')
        })

# --- SAVE FILES ---
print(f"\nSaving files...")
print(f"  Total records generated: {len(applications_data)}")

pd.DataFrame([{"role_id": 1, "name": "Admin"}, {"role_id": 2, "name": "Applicant"}]).to_csv("roles.csv", index=False)
pd.DataFrame(AGE_RANGES).to_csv("age_ranges.csv", index=False)
pd.DataFrame(PROGRAMS).to_csv("programs.csv", index=False)
pd.DataFrame(users_data).to_csv("users.csv", index=False)
pd.DataFrame(applicants_data).to_csv("applicants.csv", index=False)
pd.DataFrame(applications_data).to_csv("applications.csv", index=False)
pd.DataFrame(academic_data).to_csv("academic_profile.csv", index=False)
pd.DataFrame(achievements_data).to_csv("student_achievements.csv", index=False)

print("\n✅ Success! Data Generation Complete.")
print(f"\nBreakdown by year:")
apps_df = pd.DataFrame(applications_data)
apps_df['year'] = pd.to_datetime(apps_df['submission_date']).dt.year
print(apps_df.groupby('year').size())