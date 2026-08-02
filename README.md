# Data Analyst Job Market Analysis (India)

Analyzes live job postings across India to answer practical job-search questions:

1. Which skills do companies ask for the most?
2. Which cities have the most openings?
3. What share of postings are fresher-friendly vs experienced-only?
4. How do skill requirements differ by role?
5. Which skills appear together in the same postings?

## Why this project

Built while job-hunting for Data Analyst / fresher roles - instead of guessing
which skills to prioritize, this pulls real posting data and answers it directly.

## Tech Stack

- Python
- Adzuna Job Search API
- Pandas
- Matplotlib
- Plotly

## Setup

1. Get a free API key from [Adzuna Developer](https://developer.adzuna.com/) - sign up,
   create an app, and you'll get an `APP_ID` and `APP_KEY`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your API credentials:
   ```bash
   export ADZUNA_APP_ID=your_app_id
   export ADZUNA_APP_KEY=your_app_key
   ```
4. Fetch job postings:
   ```bash
   python fetch_jobs.py
   ```
   This saves `jobs_raw.csv` with postings across multiple data roles.
5. Generate static charts:
   ```bash
   python analyze.py
   ```
   This saves:
   - `top_skills.png`
   - `top_cities.png`
   - `experience_split.png`
   - `skills_by_role.png`
   - `skill_cooccurrence.png`
6. Generate the interactive dashboard:
   ```bash
   python visualize_plotly.py
   ```
   This saves `interactive_dashboard.html`.

## Sample Output

Add your generated charts here once you run the project, plus a short takeaway
like: "SQL and Excel appeared most often, while Power BI demand was strongest
for analyst roles."

## Project Structure

```text
fetch_jobs.py          # pulls job postings from the Adzuna API
analyze.py             # static skill/city/experience analysis charts
visualize_plotly.py    # interactive HTML dashboard
requirements.txt
README.md
```
