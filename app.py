import streamlit as st
import pandas as pd

st.set_page_config(page_title="IL Dispensary Price Aggregator", layout="wide")
st.title("🌿 Live IL Dispensary Price Comparison")

@st.cache_data(ttl=300)
def load_data():
    return pd.read_csv("daily_menu.csv")

try:
    df = load_data()
    
    st.sidebar.header("Filter Options")
    
    # Category Filter
    categories = ["All"] + sorted([str(c) for c in df["Category"].dropna().unique()])
    selected_cat = st.sidebar.selectbox("Category", categories)
    
    # Dispensary Filter
    dispensaries = ["All"] + sorted([str(d) for d in df["Dispensary"].dropna().unique()])
    selected_disp = st.sidebar.selectbox("Dispensary", dispensaries)
    
    # Search Query
    search = st.sidebar.text_input("Search Brand or Product (e.g. 'Rosin', 'Motorbreath')")
    
    # Filter Sales Only
    sales_only = st.sidebar.checkbox("Show Sales Only")

    # Apply Filters
    filtered = df.copy()
    if selected_cat != "All":
        filtered = filtered[filtered["Category"] == selected_cat]
    if selected_disp != "All":
        filtered = filtered[filtered["Dispensary"] == selected_disp]
    if search:
        filtered = filtered[
            filtered["Product"].str.contains(search, case=False, na=False) | 
            filtered["Brand"].str.contains(search, case=False, na=False)
        ]
    if sales_only:
        filtered = filtered[filtered["On Sale"] == "Yes"]

    # Sorting
    st.subheader(f"Showing {len(filtered)} results")
    sort_order = st.radio("Sort by Price:", ["Low to High", "High to Low"], horizontal=True)
    ascending = True if sort_order == "Low to High" else False
    
    filtered = filtered.sort_values(by="Price ($)", ascending=ascending)

    # Display Table
    st.dataframe(
        filtered,
        use_container_width=True,
        column_config={
            "Price ($)": st.column_config.NumberColumn(format="$%.2f"),
            "Reg Price ($)": st.column_config.NumberColumn(format="$%.2f"),
        },
        hide_index=True
    )

except Exception as e:
    st.warning("No daily menu data available yet. Trigger the workflow in GitHub Actions to generate the first daily_menu.csv file!")
