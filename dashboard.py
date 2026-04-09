import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/data"

st.title("Political Sentiment Dashboard")

# 🔹 FILTER SECTION
st.sidebar.header("Filters")

sentiment_filter = st.sidebar.selectbox(
    "Select Sentiment",
    ["all", "positive", "neutral", "negative"]
)

limit = st.sidebar.slider("Number of Data", 5, 50, 10)

# 🔹 FETCH DATA
params = {"limit": limit}

if sentiment_filter != "all":
    params["sentiment"] = sentiment_filter

response = requests.get(API_URL, params=params)

if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)

    if not df.empty:

        # 🔹 Convert timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        st.subheader("Filtered Data")
        st.dataframe(df)

        # 🔹 Sentiment Distribution
        st.subheader("Sentiment Distribution")
        sentiment_counts = df["sentiment"].value_counts()
        st.bar_chart(sentiment_counts)

        # 🔹 TIME TREND
        st.subheader("Sentiment Trend Over Time")

        trend = df.groupby([
            pd.Grouper(key="timestamp", freq="H"),
            "sentiment"
        ]).size().unstack().fillna(0)

        st.line_chart(trend)

    else:
        st.warning("No data available")
else:
    st.error("Failed to fetch data")