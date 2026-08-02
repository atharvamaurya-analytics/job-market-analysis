"""
analyze.py (v2 — pandas)
Loads jobs_raw.csv (across 3 roles) and produces:
  1. Top skills overall              -> top_skills.png
  2. Top hiring cities                -> top_cities.png
  3. Fresher vs experienced split     -> experience_split.png
  4. Top skills BY ROLE (comparison)  -> skills_by_role.png   [NEW]
  5. Skill co-occurrence heatmap      -> skill_cooccurrence.png  [NEW]

Setup:
    pip install pandas matplotlib

Run:
    python analyze.py
"""

import re

import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "jobs_raw.csv"

SKILLS = [
    "python", "sql", "excel", "power bi", "tableau", "r programming",
    "machine learning", "statistics", "pandas", "numpy", "spark",
    "aws", "azure", "google cloud", "looker", "sap", "scikit-learn",
    "etl", "big data", "hadoop", "git",
]

FRESHER_HINTS = ["fresher", "0-1 year", "0-2 year", "entry level", "entry-level", "graduate trainee"]
EXPERIENCED_HINTS = ["5+ years", "senior", "lead", "manager", "8+ years", "10+ years"]


def load_data():
    df = pd.read_csv(INPUT_FILE)
    df["text"] = (df["title"].fillna("") + " " + df["description"].fillna("")).str.lower()
    return df


def add_skill_flags(df):
    # Word-boundary matching — avoids false positives like "git" inside
    # "digital" or "sap" inside "disappointed".
    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        df[skill] = df["text"].str.contains(pattern, regex=True)
    return df


def clean_city(city):
    if pd.isna(city) or not str(city).strip():
        return None
    city = str(city).split(",")[0].strip()
    if city.lower() == "india":
        return None
    return city


def classify_experience(text):
    if any(h in text for h in FRESHER_HINTS):
        return "Fresher-friendly"
    if any(h in text for h in EXPERIENCED_HINTS):
        return "Experienced"
    return "Unclear"


def plot_top_skills(df):
    counts = df[SKILLS].sum().sort_values(ascending=False).head(10)
    print("\nTop skills requested (all roles combined):")
    print(counts.to_string())

    plt.figure(figsize=(8, 6))
    plt.barh(counts.index[::-1], counts.values[::-1], color="#2563eb")
    plt.xlabel("Number of postings")
    plt.title(f"Most In-Demand Skills — All Roles ({len(df)} postings)")
    plt.tight_layout()
    plt.savefig("top_skills.png")
    plt.close()
    print("Saved top_skills.png")


def plot_top_cities(df):
    cities = df["city"].apply(clean_city).dropna()
    counts = cities.value_counts().head(10)
    print("\nTop hiring cities:")
    print(counts.to_string())

    plt.figure(figsize=(8, 6))
    plt.barh(counts.index[::-1], counts.values[::-1], color="#16a34a")
    plt.xlabel("Number of postings")
    plt.title("Top Hiring Cities")
    plt.tight_layout()
    plt.savefig("top_cities.png")
    plt.close()
    print("Saved top_cities.png")


def plot_experience_split(df):
    labels = df["text"].apply(classify_experience)
    counts = labels.value_counts()
    print("\nExperience level split:")
    print(counts.to_string())

    plt.figure(figsize=(7, 6))
    plt.pie(counts.values, labels=counts.index, autopct="%1.0f%%")
    plt.title("Fresher vs Experienced — All Roles")
    plt.tight_layout()
    plt.savefig("experience_split.png")
    plt.close()
    print("Saved experience_split.png")


def plot_skills_by_role(df):
    top_skills = df[SKILLS].sum().sort_values(ascending=False).head(6).index.tolist()
    grouped = df.groupby("role")[top_skills].mean() * 100  # % of postings per role

    print("\nTop skills by role (% of postings mentioning it):")
    print(grouped.round(1).to_string())

    ax = grouped.T.plot(kind="bar", figsize=(9, 6))
    ax.set_ylabel("% of postings mentioning skill")
    ax.set_title("Top Skills by Role — Comparison")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig("skills_by_role.png")
    plt.close()
    print("Saved skills_by_role.png")


def plot_skill_cooccurrence(df):
    top_skills = df[SKILLS].sum().sort_values(ascending=False).head(8).index.tolist()
    matrix = df[top_skills].astype(int)
    cooccurrence = matrix.T.dot(matrix)

    print("\nSkill co-occurrence (top 8 skills, how often they appear together):")
    print(cooccurrence.to_string())

    plt.figure(figsize=(8, 7))
    plt.imshow(cooccurrence.values, cmap="Blues")
    plt.xticks(range(len(top_skills)), top_skills, rotation=45, ha="right")
    plt.yticks(range(len(top_skills)), top_skills)
    max_val = cooccurrence.values.max()
    for i in range(len(top_skills)):
        for j in range(len(top_skills)):
            val = cooccurrence.values[i, j]
            plt.text(j, i, val, ha="center", va="center",
                      color="white" if val > max_val / 2 else "black")
    plt.title("Which Skills Appear Together in the Same Posting")
    plt.colorbar(label="Number of postings")
    plt.tight_layout()
    plt.savefig("skill_cooccurrence.png")
    plt.close()
    print("Saved skill_cooccurrence.png")


def main():
    df = load_data()
    print(f"Loaded {len(df)} postings from {INPUT_FILE}")
    if "role" not in df.columns:
        print("Note: no 'role' column found — make sure jobs_raw.csv is the multi-role version.")
        df["role"] = "data analyst"

    df = add_skill_flags(df)

    plot_top_skills(df)
    plot_top_cities(df)
    plot_experience_split(df)
    plot_skills_by_role(df)
    plot_skill_cooccurrence(df)

    print("\nAll 5 charts saved. Open them from your project folder.")


if __name__ == "__main__":
    main()
