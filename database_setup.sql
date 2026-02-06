-- Lookup Tables
CREATE TABLE roles (
    role_id INT PRIMARY KEY,
    name NVARCHAR(50) NOT NULL
);

CREATE TABLE age_ranges (
    range_id INT PRIMARY KEY,
    label NVARCHAR(20) NOT NULL,
    min INT NOT NULL,
    max INT NOT NULL
);

CREATE TABLE programs (
    program_id NVARCHAR(10) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    dept NVARCHAR(50) NOT NULL,
    median_days INT
);

-- User Tables
CREATE TABLE users (
    user_id NVARCHAR(20) PRIMARY KEY,
    email NVARCHAR(100) NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    created_at DATE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE applicants (
    applicant_id NVARCHAR(20) PRIMARY KEY,
    user_id NVARCHAR(20) NOT NULL,
    first_name NVARCHAR(50) NOT NULL,
    last_name NVARCHAR(50) NOT NULL,
    dob DATE,
    age_range_id INT,
    gender NVARCHAR(10),
    country NVARCHAR(50),
    city NVARCHAR(50),
    is_first_generation BIT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (age_range_id) REFERENCES age_ranges(range_id)
);

-- Fact Table
CREATE TABLE applications (
    application_id NVARCHAR(20) PRIMARY KEY,
    applicant_id NVARCHAR(20) NOT NULL,
    program_id NVARCHAR(10) NOT NULL,
    status NVARCHAR(20) NOT NULL,
    submission_date DATE,
    days_to_submit INT,
    fees_paid BIT,
    sop_text NVARCHAR(MAX),
    admin_comments NVARCHAR(MAX),
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id),
    FOREIGN KEY (program_id) REFERENCES programs(program_id)
);

-- Related Tables
CREATE TABLE academic_profile (
    profile_id NVARCHAR(20) PRIMARY KEY,
    applicant_id NVARCHAR(20) NOT NULL,
    high_school_gpa DECIMAL(3,2),
    sat_score INT,
    scholarship_requested BIT,
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
);

CREATE TABLE student_achievements (
    id NVARCHAR(50) PRIMARY KEY,
    applicant_id NVARCHAR(20) NOT NULL,
    achievement_name NVARCHAR(200),
    date_awarded DATE,
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
);