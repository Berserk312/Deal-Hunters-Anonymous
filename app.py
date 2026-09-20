import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Chicagoland Dispensary Tracker", layout="wide")

st.title("🌿 Live IL Dispensary Price Comparison")

@st.cache_data(ttl=60)  # Refresh cache every 60 seconds
def load_data():
    if os.path.exists("daily_menu.csv"):
        df = pd.read_csv("daily_menu.csv")
        return df
    return None

df = load_data()

if df is None or df.empty:
    st.error("No daily menu data available yet. Trigger the workflow in GitHub Actions to generate daily_menu.csv!")
else:
    # Sidebar Filters
    st.sidebar.header("Filter Results")
    
    # Dispensary filter
    stores = ["All"] + list(df["Dispensary"].dropna().unique())
    selected_store = st.sidebar.selectbox("Select Dispensary", stores)
    
    # Category filter
    categories = ["All"] + list(df["Category"].dropna().unique())
    selected_cat = st.sidebar.selectbox("Select Category", categories)
    
    # Search filter
    search_query = st.sidebar.text_input("Search Product or Brand", "")
    
    # Filter logic
    filtered_df = df.copy()
    if selected_store != "All":
        filtered_df = filtered_df[filtered_df["Dispensary"] == selected_store]
    if selected_cat != "All":
        filtered_df = filtered_df[filtered_df["Category"] == selected_cat]
    if search_query:
        filtered_df = filtered_df[
            filtered_df["Product"].str.contains(search_query, case=False, na=False) |
            filtered_df["Brand"].str.contains(search_query, case=False, na=False)
        ]

    st.write(f"Showing **{len(filtered_df)}** products:")
    
    # Interactive Table
    st.dataframe(
        filtered_df,
        column_config={
            "Price ($)": st.column_config.NumberColumn(format="$%.2f"),
            "Reg Price ($)": st.column_config.NumberColumn(format="$%.2f"),
        },
        use_container_width=True,
        hide_index=True
    )