import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------
# Page Configuration
# -----------------------------------

st.set_page_config(
    page_title="Netflix Interactive Dashboard",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Netflix Interactive Dashboard")

st.markdown(
    "Explore Netflix Movies and TV Shows using interactive visualizations."
)

# -----------------------------------
# Load Dataset
# -----------------------------------

df = pd.read_csv("data/netflix_titles.csv")

# Data Cleaning
df["director"] = df["director"].fillna("Unknown")
df["cast"] = df["cast"].fillna("Unknown")
df["country"] = df["country"].fillna("Unknown")

df = df.dropna(subset=["rating", "duration"])

df["date_added"] = pd.to_datetime(
    df["date_added"].str.strip(),
    errors="coerce"
)

df = df.dropna(subset=["date_added"])

# -----------------------------------
# KPI Cards
# -----------------------------------

movies = len(df[df["type"] == "Movie"])

tvshows = len(df[df["type"] == "TV Show"])

countries = df["country"].nunique()

avg_year = int(df["release_year"].mean())

col1, col2, col3, col4 = st.columns(4)

col1.metric("🎥 Movies", movies)

col2.metric("📺 TV Shows", tvshows)

col3.metric("🌍 Countries", countries)

col4.metric("📅 Avg Release Year", avg_year)

# -----------------------------------
# Sidebar Filters
# -----------------------------------

st.sidebar.header("🔍 Filter Dashboard")

# Type Filter
selected_type = st.sidebar.multiselect(
    "Select Type",
    options=df["type"].unique(),
    default=df["type"].unique()
)

# Rating Filter
selected_rating = st.sidebar.multiselect(
    "Select Rating",
    options=sorted(df["rating"].unique()),
    default=sorted(df["rating"].unique())
)

# Release Year Filter
min_year = int(df["release_year"].min())
max_year = int(df["release_year"].max())

selected_year = st.sidebar.slider(
    "Release Year",
    min_year,
    max_year,
    (min_year, max_year)
)

# Country Filter
countries = sorted(df["country"].unique())

selected_country = st.sidebar.selectbox(
    "Select Country",
    ["All"] + countries
)

# Apply Filters
filtered_df = df[
    (df["type"].isin(selected_type)) &
    (df["rating"].isin(selected_rating)) &
    (df["release_year"].between(selected_year[0], selected_year[1]))
]

if selected_country != "All":
    filtered_df = filtered_df[
        filtered_df["country"] == selected_country
    ]

st.subheader("🎬 Movies vs TV Shows")

type_count = filtered_df["type"].value_counts().reset_index()
type_count.columns = ["Type", "Count"]

fig = px.pie(
    type_count,
    values="Count",
    names="Type",
    hole=0.5,
    title="Movies vs TV Shows"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("⭐ Content Rating Distribution")

rating_count = (
    filtered_df["rating"]
    .value_counts()
    .reset_index()
)

rating_count.columns = ["Rating", "Count"]

fig = px.bar(
    rating_count,
    x="Rating",
    y="Count",
    title="Content Rating Distribution"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("📅 Content Released Over the Years")

year_count = (
    filtered_df["release_year"]
    .value_counts()
    .sort_index()
    .reset_index()
)

year_count.columns = ["Year", "Count"]

fig = px.line(
    year_count,
    x="Year",
    y="Count",
    markers=True,
    title="Netflix Content by Release Year"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# Top 10 Countries
# -----------------------------------

st.subheader("🌍 Top 10 Countries by Content")

country_df = (
    filtered_df[filtered_df["country"] != "Unknown"]
    .groupby("country")
    .size()
    .reset_index(name="Count")
    .sort_values("Count", ascending=False)
    .head(10)
)

fig = px.bar(
    country_df,
    x="country",
    y="Count",
    color="Count",
    title="Top 10 Countries"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# Top Genres
# -----------------------------------

st.subheader("🎭 Top Genres")

genre_df = (
    filtered_df["listed_in"]
    .str.split(", ")
    .explode()
    .value_counts()
    .head(10)
    .reset_index()
)

genre_df.columns = ["Genre", "Count"]

fig = px.bar(
    genre_df,
    x="Genre",
    y="Count",
    color="Count",
    title="Top 10 Genres"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# World Map
# -----------------------------------

st.subheader("🗺️ Content Distribution Across Countries")

map_df = (
    filtered_df[filtered_df["country"] != "Unknown"]
    .groupby("country")
    .size()
    .reset_index(name="Count")
)

fig = px.choropleth(
    map_df,
    locations="country",
    locationmode="country names",
    color="Count",
    hover_name="country",
    color_continuous_scale="Reds",
    title="Netflix Content Across the World"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------
# Dataset Preview
# -----------------------------------

st.subheader("📄 Filtered Dataset")

st.dataframe(filtered_df)