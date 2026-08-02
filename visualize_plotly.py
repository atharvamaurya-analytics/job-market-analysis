"""
visualize_plotly.py (v4 — legend + spacing fixes)
Creates one interactive HTML dashboard from jobs_raw.csv covering:
  1. Top skills overall
  2. Top hiring cities
  3. Fresher vs experienced split
  4. Top skills by role (comparison)
  5. Skill co-occurrence heatmap

Setup:
    pip install plotly pandas

Run:
    python visualize_plotly.py

Output: dashboard.html
"""

import re

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

INPUT_FILE = "jobs_raw.csv"
OUTPUT_FILE = "dashboard.html"

SKILLS = [
    "python", "sql", "excel", "power bi", "tableau", "r programming",
    "machine learning", "statistics", "pandas", "numpy", "spark",
    "aws", "azure", "google cloud", "looker", "sap", "scikit-learn",
    "etl", "big data", "hadoop", "git",
]

FRESHER_HINTS = ["fresher", "0-1 year", "0-2 year", "entry level", "entry-level", "graduate trainee"]
EXPERIENCED_HINTS = ["5+ years", "senior", "lead", "manager", "8+ years", "10+ years"]


def clean_city(city):
    if pd.isna(city) or not str(city).strip():
        return None
    city = str(city).split(",")[0].strip()
    return None if city.lower() == "india" else city


def classify_experience(text):
    if any(h in text for h in FRESHER_HINTS):
        return "Fresher-friendly"
    if any(h in text for h in EXPERIENCED_HINTS):
        return "Experienced"
    return "Unclear"


def main():
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} postings from {INPUT_FILE}")
    if "role" not in df.columns:
        df["role"] = "data analyst"

    df["text"] = (df["title"].fillna("") + " " + df["description"].fillna("")).str.lower()
    df["city_clean"] = df["city"].apply(clean_city)
    df["experience"] = df["text"].apply(classify_experience)
    # Word-boundary matching — avoids false positives like "git" inside
    # "digital" or "sap" inside "disappointed".
    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        df[skill] = df["text"].str.contains(pattern, regex=True)

    top_skills = df[SKILLS].sum().sort_values(ascending=False).head(10)
    top_cities = df["city_clean"].value_counts().head(10)
    exp_counts = df["experience"].value_counts()

    role_skills = df[SKILLS].sum().sort_values(ascending=False).head(6).index.tolist()
    by_role = df.groupby("role")[role_skills].mean() * 100

    cooc_skills = df[SKILLS].sum().sort_values(ascending=False).head(8).index.tolist()
    cooc_matrix = df[cooc_skills].astype(int)
    cooccurrence = cooc_matrix.T.dot(cooc_matrix)

    fig = make_subplots(
        rows=3, cols=2,
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "domain"}, {"type": "bar"}],
            [{"type": "heatmap", "colspan": 2}, None],
        ],
        subplot_titles=(
            "Most In-Demand Skills<br><span style='font-size:11px;color:gray'>Skills mentioned most often across all postings</span>",
            "Top Hiring Cities<br><span style='font-size:11px;color:gray'>Cities with the most job postings</span>",
            "Fresher vs Experienced<br><span style='font-size:11px;color:gray'>Split of postings by experience level required</span>",
            "Top Skills by Role<br><span style='font-size:11px;color:gray'>How skill demand differs across the 3 roles (click legend to isolate one)</span>",
            "Skill Co-occurrence<br><span style='font-size:11px;color:gray'>How often two skills are asked for in the same posting</span>",
        ),
        vertical_spacing=0.14,
        row_heights=[0.28, 0.28, 0.44],
    )

    fig.add_trace(
        go.Bar(x=top_skills.values[::-1], y=top_skills.index[::-1], orientation="h",
               marker_color="#2563eb", showlegend=False),
        row=1, col=1,
    )

    fig.add_trace(
        go.Bar(x=top_cities.values[::-1], y=top_cities.index[::-1], orientation="h",
               marker_color="#16a34a", showlegend=False),
        row=1, col=2,
    )

    fig.add_trace(
        go.Pie(
            labels=exp_counts.index, values=exp_counts.values,
            marker_colors=["#94a3b8", "#ef4444", "#22c55e"][:len(exp_counts)],
            showlegend=False, textinfo="label+percent",
        ),
        row=2, col=1,
    )

    # NOTE: no shared legendgroup here anymore — each role's bar is its own
    # group, so clicking one in the legend only hides that one, not all three.
    for role in by_role.index:
        fig.add_trace(
            go.Bar(x=role_skills, y=by_role.loc[role].values, name=role),
            row=2, col=2,
        )

    fig.add_trace(
        go.Heatmap(
            z=cooccurrence.values, x=cooc_skills, y=cooc_skills,
            colorscale="Blues", showscale=True,
            text=cooccurrence.values, texttemplate="%{text}",
            colorbar=dict(title="postings", len=0.32, y=0.13, x=1.02),
        ),
        row=3, col=1,
    )

    fig.update_layout(
        title=dict(
            text=f"Job Market Dashboard — India ({len(df)} postings, {df['role'].nunique()} roles)",
            font=dict(size=24),
            y=0.99,
        ),
        height=1550,
        template="plotly_white",
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=0.42, xanchor="right", x=1.0),
        margin=dict(t=140, b=40),
    )

    fig.write_html(OUTPUT_FILE)
    print(f"Saved interactive dashboard to {OUTPUT_FILE}")
    print("Double-click it to open in your browser.")


if __name__ == "__main__":
    main()
