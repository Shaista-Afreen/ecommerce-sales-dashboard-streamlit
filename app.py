import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

# Title
st.title("🛍️ E-Commerce Sales Dashboard")

# Load Data
df = pd.read_csv("data/ecommerce_sales_data.csv")
# Convert 'Date' column to datetime if not already
df["Date"] = pd.to_datetime(df["Date"])

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Data")

# 1. Date Range Filter
min_date = df["Date"].min()
max_date = df["Date"].max()
date_range = st.sidebar.date_input("📅 Select Date Range", [min_date, max_date])

# 2. Category Filter
categories = df["Category"].unique()
selected_categories = st.sidebar.multiselect("🛍️ Select Categories", categories, default=list(categories))

# 3. Region Filter
regions = df["Region"].unique()
selected_regions = st.sidebar.multiselect("🌍 Select Regions", regions, default=list(regions))

st.sidebar.markdown("---")
st.sidebar.info("Use the filters above to explore your sales data interactively.")

# --- Apply Filters to DataFrame ---
filtered_df = df[
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1])) &
    (df["Category"].isin(selected_categories)) &
    (df["Region"].isin(selected_regions))
]


# --- PHASE 2: Summary Metrics ---
st.markdown("## 📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = filtered_df["Total Sale"].sum()
    st.metric("💰 Total Revenue", f"₹ {total_revenue:,.2f}")

with col2:
    total_orders = len(filtered_df)
    st.metric("📦 Total Orders", total_orders)

with col3:
    top_category = filtered_df["Category"].value_counts().idxmax() if not filtered_df.empty else "N/A"
    st.metric("🏆 Top Category", top_category)

with col4:
    num_regions = filtered_df["Region"].nunique()
    st.metric("🌍 Regions", num_regions)

# --- Show Data Table (optional below KPIs) ---
st.markdown("### 📦 Raw Sales Data")
# st.dataframe(filtered_df)


st.markdown("### 🧾 Smart Interactive Table")

if not filtered_df.empty:
    gb = GridOptionsBuilder.from_dataframe(filtered_df)
    gb.configure_pagination()
    gb.configure_side_bar()  # Optional: Shows filters and columns on right
    gb.configure_default_column(editable=False, groupable=True)
    grid_options = gb.build()

    AgGrid(
        filtered_df,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=True,
        theme="alpine"  # Other themes: "streamlit", "balham", "material"
    )
else:
    st.warning("⚠️ No data to display. Please adjust filters.")

# --- Download Button ---
st.markdown("### 📥 Download Filtered Data")

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

if not filtered_df.empty:
    csv_data = convert_df_to_csv(filtered_df)
    st.download_button(
        label="📤 Export as CSV",
        data=csv_data,
        file_name="filtered_sales_data.csv",
        mime="text/csv"
    )
else:
    st.info("No data available to download. Please adjust your filters.")


# --- Bar Chart: Total Sales by Category ---
st.markdown("### 📊 Total Sales by Category")
sales_by_category = filtered_df.groupby("Category")["Total Sale"].sum().reset_index()
fig_bar = px.bar(sales_by_category, x="Category", y="Total Sale", color="Category",
                 labels={"Total Sale": "Total Revenue"}, title="Total Revenue per Category")
st.plotly_chart(fig_bar, use_container_width=True)

# --- Line Chart: Sales Over Time ---
st.markdown("### 📈 Sales Trend Over Time")

sales_over_time = filtered_df.groupby("Date")["Total Sale"].sum().reset_index()
fig_line = px.line(sales_over_time, x="Date", y="Total Sale",
                   labels={"Total Sale": "Total Revenue"}, title="Revenue Over Time")
st.plotly_chart(fig_line, use_container_width=True)
