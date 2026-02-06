-- ============================================
-- CSV to SQL Server Migration Script
-- Run this AFTER creating tables with schema.sql
-- ============================================

USE UniversityAdmissions;
GO

PRINT 'Starting CSV data migration...';
PRINT '';

-- ============================================
-- IMPORTANT: Update file paths to your CSV location
-- Replace 'C:\path\to\your\csv\files\' with actual path
-- ============================================

DECLARE @CSVPath NVARCHAR(500) = 'C:\path\to\your\csv\files\';  -- UPDATE THIS!

-- ============================================
-- 1. IMPORT ROLES
-- ============================================
PRINT '1. Importing roles...';

BULK INSERT roles
FROM 'C:\path\to\your\csv\files\roles.csv'  -- UPDATE PATH!
WITH (
    FIRSTROW = 2,  -- Skip header row
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);

PRINT '   Imported ' + CAST(@@ROWCOUNT AS VARCHAR) + ' roles';
GO

-- ============================================
-- 2. IMPORT AGE_RANGES
-- ============================================
PRINT '2. Importing age ranges...';

BULK INSERT age_ranges
FROM 'C:\path\to\your\csv\files\age_ranges.csv'  -- UPDATE PATH!
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);

PRINT '   Imported ' + CAST(@@ROWCOUNT AS VARCHAR) + ' age ranges';
GO

-- ============================================
-- 3. IMPORT PROGRAMS
-- ============================================
PRINT '3. Importing programs...';

BULK INSERT programs
FROM 'C:\path\to\your\csv\files\programs.csv'  -- UPDATE PATH!
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);

PRINT '   Imported ' + CAST(@@ROWCOUNT AS VARCHAR) + ' programs';
GO

-- ============================================
-- 4. IMPORT USERS
-- ============================================
PRINT '4. Importing users...';

BULK INSERT users
FROM 'C:\path\to\your\csv\files\users.csv'  -- UPDATE PATH!
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);

PRINT '   Imported ' + CAST(@@ROWCOUNT AS VARCHAR) + ' users';
GO

-- ============================================
-- 5. IMPORT APPLICANTS
-- ============================================
PRINT '5. Importing applicants...';

BULK INSERT applicants
FROM 'C:\path\to\your\csv\files\applicants.csv'  -- UPDATE PATH!
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);

PRINT '   Imported ' + CAST(@@ROWCOUNT AS VARCHAR) + ' applicants';
GO

-- ============================================
-- 6. IMPORT APPLICATIONS
-- ============================================
PRINT '6. Importing applications...';

BULK INSERT applications
FROM 'C:\path\to\your\csv\files\applications.csv'  -- UPDATE PATH!
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);

PRINT '   Imported ' + CAST(@@ROWCOUNT AS VARCHAR) + ' applications';
GO

-- ============================================
-- 7. IMPORT ACADEMIC_PROFILE
-- ============================================
PRINT '7. Importing academic profiles...';

BULK INSERT academic_profile
FROM 'C:\path\to\your\csv\files\academic_profile.csv'  -- UPDATE PATH!
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);

PRINT '   Imported ' + CAST(@@ROWCOUNT AS VARCHAR) + ' academic profiles';
GO

-- ============================================
-- 8. IMPORT STUDENT_ACHIEVEMENTS
-- ============================================
PRINT '8. Importing student achievements...';

BULK INSERT student_achievements
FROM 'C:\path\to\your\csv\files\student_achievements.csv'  -- UPDATE PATH!
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
);

PRINT '   Imported ' + CAST(@@ROWCOUNT AS VARCHAR) + ' achievements';
GO

-- ============================================
-- 9. VERIFY IMPORT
-- ============================================
PRINT '';
PRINT '============================================';
PRINT 'Migration Complete! Summary:';
PRINT '============================================';

SELECT 'roles' AS TableName, COUNT(*) AS RecordCount FROM roles
UNION ALL
SELECT 'age_ranges', COUNT(*) FROM age_ranges
UNION ALL
SELECT 'programs', COUNT(*) FROM programs
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'applicants', COUNT(*) FROM applicants
UNION ALL
SELECT 'applications', COUNT(*) FROM applications
UNION ALL
SELECT 'academic_profile', COUNT(*) FROM academic_profile
UNION ALL
SELECT 'student_achievements', COUNT(*) FROM student_achievements;

PRINT '';
PRINT '============================================';
PRINT 'Verify foreign key relationships:';
PRINT '============================================';

-- Check for any orphaned records
SELECT 
    'Orphaned applications' AS Issue,
    COUNT(*) AS Count
FROM applications app
LEFT JOIN applicants a ON app.applicant_id = a.applicant_id
WHERE a.applicant_id IS NULL

UNION ALL

SELECT 
    'Orphaned applicants',
    COUNT(*)
FROM applicants a
LEFT JOIN users u ON a.user_id = u.user_id
WHERE u.user_id IS NULL;

PRINT '';
PRINT 'Migration script completed successfully!';
PRINT 'You can now run your Flask application.';
GO