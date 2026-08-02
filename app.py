"""
app.py — Interactive Job Market Explorer (Streamlit)

Setup:
    pip install streamlit plotly pandas

Run locally:
    streamlit run app.py
"""

import re

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="India Job Market Explorer", layout="wide")

# Slightly bigger toolbar icons on the data table (download/search/expand/sort).
# Best-effort tweak using Streamlit's public data-testid hooks — if a future
# Streamlit version changes these internally, this block just has no effect.
st.markdown(
    """
    <style>
    [data-testid="stElementToolbar"] button {
        width: 34px !important;
        height: 34px !important;
    }
    [data-testid="stElementToolbar"] button svg {
        width: 22px !important;
        height: 22px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SKILLS = [
    "python", "sql", "excel", "power bi", "tableau", "r programming",
    "machine learning", "statistics", "pandas", "numpy", "spark",
    "aws", "azure", "google cloud", "looker", "sap", "scikit-learn",
    "etl", "big data", "hadoop", "git",
]


def clean_city(city):
    if pd.isna(city) or not str(city).strip():
        return None
    city = str(city).split(",")[0].strip()
    return None if city.lower() == "india" else city


@st.cache_data
def load_data():
    df = pd.read_csv("jobs_raw.csv")
    df["text"] = (df["title"].fillna("") + " " + df["description"].fillna("")).str.lower()
    df["city_clean"] = df["city"].apply(clean_city)
    return df


df = load_data()

st.title("📊 India Job Market Explorer")
st.caption(f"{len(df)} postings across {df['role'].nunique()} roles — data refreshed weekly")

# ---- Sidebar filters ----
st.sidebar.header("Filters")
roles = st.sidebar.multiselect(
    "Role", options=sorted(df["role"].unique()), default=sorted(df["role"].unique())
)
cities = sorted(df["city_clean"].dropna().unique())
selected_cities = st.sidebar.multiselect("City (leave empty = all)", options=cities)

# ---- Friendly alert instead of crashing on empty selections ----
if not roles:
    st.warning("⚠️ Please select at least one **Role** from the sidebar to see the data.")
    st.stop()

filtered = df[df["role"].isin(roles)]
if selected_cities:
    filtered = filtered[filtered["city_clean"].isin(selected_cities)]

st.sidebar.metric("Postings matching filters", len(filtered))

if filtered.empty:
    st.warning("⚠️ No postings match the current filters. Try selecting a different Role or City.")
    st.stop()

# ---- Charts ----
col1, col2 = st.columns(2)

with col1:
    # Word-boundary matching — avoids false positives like "git" inside
    # "digital" or "sap" inside "disappointed".
    skill_counts = {
        s: int(filtered["text"].str.contains(r"\b" + re.escape(s) + r"\b", regex=True).sum())
        for s in SKILLS
    }
    skill_df = pd.DataFrame(
        sorted(skill_counts.items(), key=lambda x: -x[1])[:10], columns=["skill", "count"]
    )
    fig = px.bar(skill_df, x="count", y="skill", orientation="h", title="Top Skills")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    city_counts = filtered["city_clean"].value_counts().head(10)
    if city_counts.empty:
        st.info("No city data available for the current filters.")
    else:
        city_df = pd.DataFrame({"city": city_counts.index, "count": city_counts.values})
        fig2 = px.bar(city_df, x="count", y="city", orientation="h", title="Top Cities")
        fig2.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

# ---- Table ----
st.subheader("Browse postings")
st.dataframe(
    filtered[["role", "title", "company", "city", "created", "redirect_url"]],
    use_container_width=True,
    hide_index=True,
)
