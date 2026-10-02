import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Electricity Reliability Analytics",
    page_icon="⚡",
    layout="wide"
)

# =========================================================
# LOAD ARFF DATASET
# =========================================================

with open("eb.arff", "r", encoding="utf-8") as file:
    lines = file.readlines()

data_start = 0
columns = []

for i, line in enumerate(lines):
    low = line.strip().lower()

    if low.startswith("@attribute"):
        parts = line.strip().split(None, 2)
        columns.append(parts[1].strip("'\""))

    elif low == "@data":
        data_start = i + 1
        break

rows = []

for line in lines[data_start:]:
    line = line.strip()

    if line and not line.startswith("%"):
        rows.append([
            v.strip().strip("'\"")
            for v in line.split(",")
        ])

df = pd.DataFrame(rows, columns=columns)

# =========================================================
# DATA CLEANING
# =========================================================

df = df.replace("?", pd.NA)

for col in ["ForkVA", "ForkW", "ServiceID"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["Usage_Level"] = pd.cut(
    df["ForkW"],
    bins=[
        -float("inf"),
        0.25,
        0.50,
        0.75,
        float("inf")
    ],
    labels=[
        "Low",
        "Medium",
        "High",
        "Very High"
    ]
)

# =========================================================
# HEADER
# =========================================================

st.title("⚡ Electricity Reliability Analytics")

st.subheader(
    "Electricity Consumption & Service Usage Dashboard"
)

st.write(
    "An interactive analytics dashboard for exploring electricity "
    "consumption patterns across consumer types and service IDs."
)

st.caption(
    "Developed by Kavya | Python • Pandas • Matplotlib • Streamlit"
)

st.divider()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title("🎛️ Dashboard Filters")

# Consumer type filter

consumer_options = sorted(df["Type"].dropna().unique())

selected_consumers = st.sidebar.multiselect(
    "Consumer Type",
    consumer_options,
    default=consumer_options
)

# Usage level filter

usage_options = [
    "Low",
    "Medium",
    "High",
    "Very High"
]

selected_usage = st.sidebar.multiselect(
    "Usage Level",
    usage_options,
    default=usage_options
)

# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df[
    (df["Type"].isin(selected_consumers)) &
    (df["Usage_Level"].isin(selected_usage))
].copy()

# =========================================================
# KPI CALCULATIONS
# =========================================================

total_records = len(filtered_df)

consumer_types = filtered_df["Type"].nunique()

service_ids = filtered_df["ServiceID"].nunique()

average_forkw = filtered_df["ForkW"].mean()

# =========================================================
# KPI CARDS
# =========================================================

st.header("📌 Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Records",
    f"{total_records:,}"
)

col2.metric(
    "Consumer Types",
    consumer_types
)

col3.metric(
    "Service IDs",
    f"{service_ids:,}"
)

col4.metric(
    "Average ForkW",
    f"{average_forkw:.3f}"
)

# =========================================================
# CONSUMER TYPE ANALYSIS
# =========================================================

st.header("📊 Consumer Type Analysis")

average_usage = (
    filtered_df
    .groupby("Type")["ForkW"]
    .mean()
    .sort_values(ascending=False)
)

fig1, ax1 = plt.subplots(figsize=(12, 5))

ax1.bar(
    average_usage.index,
    average_usage.values
)

ax1.set_xlabel("Consumer Type")
ax1.set_ylabel("Average ForkW")
ax1.set_title(
    "Average Electricity Usage by Consumer Type"
)

plt.xticks(rotation=90)
plt.tight_layout()

st.pyplot(fig1)

# =========================================================
# USAGE LEVEL DISTRIBUTION
# =========================================================

st.header("📈 Usage Level Distribution")

usage_counts = (
    filtered_df["Usage_Level"]
    .value_counts()
    .reindex(
        [
            "Low",
            "Medium",
            "High",
            "Very High"
        ]
    )
    .fillna(0)
)

fig2, ax2 = plt.subplots(figsize=(8, 5))

ax2.bar(
    usage_counts.index.astype(str),
    usage_counts.values
)

ax2.set_xlabel("Usage Level")
ax2.set_ylabel("Number of Records")
ax2.set_title(
    "Electricity Usage Level Distribution"
)

plt.tight_layout()

st.pyplot(fig2)

# =========================================================
# FORKVA VS FORKW
# =========================================================

st.header("🔍 Electricity Measurement Relationship")

correlation = filtered_df["ForkVA"].corr(
    filtered_df["ForkW"]
)

st.metric(
    "ForkVA ↔ ForkW Correlation",
    f"{correlation:.3f}"
)

fig3, ax3 = plt.subplots(figsize=(9, 5))

ax3.scatter(
    filtered_df["ForkVA"],
    filtered_df["ForkW"],
    alpha=0.5
)

ax3.set_xlabel("ForkVA")
ax3.set_ylabel("ForkW")

ax3.set_title(
    "Relationship Between ForkVA and ForkW"
)

plt.tight_layout()

st.pyplot(fig3)

# =========================================================
# CONSUMER SUMMARY TABLE
# =========================================================

st.header("🏢 Consumer Usage Summary")

summary = (
    filtered_df
    .groupby("Type")[["ForkVA", "ForkW"]]
    .mean()
    .sort_values(
        "ForkW",
        ascending=False
    )
)

st.dataframe(
    summary,
    width="stretch"
)

# =========================================================
# AUTOMATIC INSIGHTS
# =========================================================

st.header("💡 Key Insights")

if not average_usage.empty:

    highest_type = average_usage.idxmax()
    highest_value = average_usage.max()

    lowest_type = average_usage.idxmin()
    lowest_value = average_usage.min()

    st.write(
        f"🔴 **Highest average electricity usage:** "
        f"{highest_type} "
        f"({highest_value:.3f} ForkW)"
    )

    st.write(
        f"🟢 **Lowest average electricity usage:** "
        f"{lowest_type} "
        f"({lowest_value:.3f} ForkW)"
    )

    st.write(
        f"📌 **Records analyzed:** "
        f"{total_records:,}"
    )

    st.write(
        f"📌 **Consumer types analyzed:** "
        f"{consumer_types}"
    )

    st.write(
        f"📌 **Service IDs analyzed:** "
        f"{service_ids:,}"
    )

# =========================================================
# DOWNLOAD DATA
# =========================================================

st.header("⬇️ Download Filtered Data")

csv_data = filtered_df.to_csv(
    index=False
)

st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="electricity_filtered_data.csv",
    mime="text/csv"
)

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Electricity Reliability Analytics | "
    "Data Analytics Project"
)