# 📖 Usage Guide & Advanced Workflows

This guide covers advanced operations for the University Admissions System, including generating synthetic data, migrating it to SQL Server, and configuring the Power BI dashboard.

---

## 🛠️ Workflow 1: Generate Synthetic Data (CSV)
The application includes a sophisticated data generator that creates realistic admissions data based on Indian college trends (2017–2026).

**1. Locate the Generator**
Navigate to the root directory where `generate_data.py` is located.

**2. Run the Script**
Execute the following command in your terminal:
```bash
python generate_data.py
```

**3. Output**
The script will generate the following CSV files in your directory:
* `users.csv`: User credentials (applicants).
* `applicants.csv`: Demographic details.
* `applications.csv`: Application status, dates, and SOPs.
* `academic_profile.csv`: GPA and SAT scores.
* `student_achievements.csv`: Extracurricular awards.
* `programs.csv`, `roles.csv`, `age_ranges.csv`: Lookup tables.

> **Note:** The script automatically handles logic like "Accepted students have higher GPAs" and "Admission spikes occur in March-April".

---

## 🔄 Workflow 2: Migrate CSV Data to SQL Server
Once you have generated the CSV data, you can bulk import it into your SQL Server database using the provided migration script.

**Prerequisite:** Ensure your database tables are created. If not, run `schema.sql` first.

**1. Prepare the Migration Script**
Open the `migrate.sql` file in a text editor or SQL Server Management Studio (SSMS).

**2. Update File Paths**
The `BULK INSERT` commands require absolute paths to your CSV files. Find and replace the placeholder path in the script:

* **Find:** `C:\path\to\your\csv\files\`
* **Replace with:** The actual absolute path to your project folder (e.g., `C:\Users\YourName\Projects\UniversityAdmissions\`).

*Example:*
```sql
BULK INSERT roles
FROM 'C:\Users\Admin\UniversityAdmissions\roles.csv' -- Updated Path
WITH ( ... )
```

**3. Execute the Migration**
* **Option A (SSMS):** Open `migrate.sql` in SSMS, connect to your database instance, and click **Execute**.
* **Option B (Command Line):**
    ```bash
    sqlcmd -S localhost -d UniversityAdmissions -i migrate.sql
    ```

**4. Verify Data**
The script prints a summary table at the end showing the count of records imported into each table.

---

## 📊 Workflow 3: Running the Power BI Dashboard
The Admin Dashboard embeds a live Power BI report to visualize admissions data.

### Step 1: Configure the Environment
The application looks for the Power BI URL in your environment variables.
1.  Create a file named `.env` in the root directory (if it doesn't exist).
2.  Add your Power BI Embed URL:
    ```env
    PBI_EMBED_URL=[https://app.powerbi.com/view?r=eyJrIjoi](https://app.powerbi.com/view?r=eyJrIjoi)...
    ```
    *(Note: If you are setting up your own report, use the "Publish to Web (Public)" link from the Power BI Service).*

### Step 2: Access the Dashboard
1.  Start the Flask application (`python app.py`).
2.  Log in as an **Admin**:
    * **Email:** `admin@mm.edu`
    * **Password:** `admin123`
3.  You will be redirected to `/admin_dashboard`.
4.  The Power BI report will load inside the dashboard iframe, displaying metrics derived from your current database state.

### Step 3: Refreshing Data
Since the Power BI report is connected to your dataset:
* **Direct Query:** If configured with Direct Query, changes in the SQL database (new applications) reflect immediately.
* **Import Mode:** If using Import Mode, you must refresh the dataset in the Power BI Service for new SQL data to appear in the embedded report.