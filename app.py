from anyio import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# PAGE CONFIG

st.set_page_config(
    page_title="Anime Source Intelligence Dashboard",
    page_icon="🎌",
    layout="wide"
)



# LOAD DATA

@st.cache_data
def load_data():
    from pathlib import Path

    DATA_FILE = Path("data/processed/anime_processed.csv")
    df = pd.read_csv(DATA_FILE)
    return df

df = load_data()


# CLEANING

numeric_cols = [
    "Score",
    "Members",
    "Favorites",
    "Episodes",
    "Popularity"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")


# SIDEBAR

st.sidebar.title("🎌 Filters")

sources = sorted(df["Source_Clean"].dropna().unique())

selected_sources = st.sidebar.multiselect(
    "Source Material",
    sources,
    default=sources
)

filtered_df = df[df["Source_Clean"].isin(selected_sources)]


# TITLE

st.title("🎌 Anime Source Material Intelligence Dashboard")

st.markdown(
"""
Explore how source material influences anime success,
ratings, popularity and audience engagement.
"""
)

st.info("""
### Executive Summary

This dashboard explores how anime source materials influence ratings,
popularity and audience engagement.

**Key Findings**

• Manga is the dominant source material.

• Manga and Novel adaptations tend to receive stronger ratings.

• Popular anime attract significantly more favorites.

• Audience engagement is closely linked with anime success.
""")


# KPI SECTION

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Anime",
        f"{len(filtered_df):,}"
    )

with col2:
    st.metric(
        "Average Score",
        round(filtered_df["Score"].mean(), 2)
    )

with col3:
    st.metric(
        "Average Members",
        f"{int(filtered_df['Members'].mean()):,}"
    )

with col4:
    st.metric(
        "Average Favorites",
        f"{int(filtered_df['Favorites'].mean()):,}"
    )

st.divider()


# CHART 1

c1, c2 = st.columns(2)

with c1:

    source_counts = (
        filtered_df["Source_Clean"]
        .value_counts()
        .reset_index()
    )

    source_counts.columns = ["Source", "Count"]

    fig = px.bar(
        source_counts,
        x="Source",
        y="Count",
        title="Anime Count by Source Material"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(
    " Shows how many anime originate from each source material. "
    "Manga adaptations dominate the industry."
)

with c2:

    avg_score = (
        filtered_df
        .groupby("Source_Clean")["Score"]
        .mean()
        .reset_index()
        .sort_values("Score", ascending=False)
    )

    fig = px.bar(
        avg_score,
        x="Source_Clean",
        y="Score",
        title="Average Score by Source"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(
    " Compares average ratings across source types. "
    "Higher bars indicate stronger audience reception."
)


# CHART 2


c3, c4 = st.columns(2)

with c3:

    fig = px.box(
        filtered_df,
        x="Source_Clean",
        y="Score",
        title="Score Distribution by Source"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(
    " Displays score consistency and spread. "
    "Tighter boxes indicate more consistent ratings."
)

with c4:

    fig = px.scatter(
        filtered_df,
        x="Members",
        y="Favorites",
        color="Source_Clean",
        title="Members vs Favorites",
        opacity=0.7
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption(
    " Examines audience size versus fan loyalty. "
    "More members generally lead to more favorites."
)


# POPULARITY ANALYSIS

st.subheader(" Popularity Analysis")

popularity = (
    filtered_df
    .groupby("Source_Clean")["Popularity"]
    .mean()
    .reset_index()
    .sort_values("Popularity")
)

fig = px.bar(
    popularity,
    x="Source_Clean",
    y="Popularity",
    title="Average Popularity Rank"
)

st.plotly_chart(fig, use_container_width=True)
st.caption(
    " Compares average popularity ranking by source material. "
    "Lower ranks represent greater popularity."
)


# GENRE ANALYSIS


st.subheader(" Genre Analysis")

genre_df = filtered_df.copy()

genre_df["Genres"] = (
    genre_df["Genres"]
    .astype(str)
    .str.split(", ")
)

genre_df = genre_df.explode("Genres")

top_genres = (
    genre_df["Genres"]
    .value_counts()
    .head(15)
    .reset_index()
)

top_genres.columns = ["Genre", "Count"]

fig = px.bar(
    top_genres,
    x="Genre",
    y="Count",
    title="Top Genres"
)

st.plotly_chart(fig, use_container_width=True)
st.caption(
    " Highlights the most common genres in the dataset. "
    "These genres drive a large share of anime production."
)


# ML INSIGHTS

st.subheader(" Machine Learning Findings")

st.info(
"""
Linear Regression Model

Features Used:
• Members
• Favorites
• Episodes
• Source Material

Actual scores were predicted using these features:
• MAE: 0.6382902284204977
• R2 Score: 0.2585901359414291
"""
)


# DATA TABLE


st.subheader(" Anime Explorer")

search = st.text_input("Search Anime")

if search:
    display_df = filtered_df[
        filtered_df["Name"]
        .str.contains(search, case=False, na=False)
    ]
else:
    display_df = filtered_df

st.dataframe(
    display_df,
    use_container_width=True
)


# DOWNLOAD


csv = display_df.to_csv(index=False)

st.download_button(
    "⬇ Download Filtered Data",
    csv,
    "anime_filtered.csv",
    "text/csv"
)