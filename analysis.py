import pandas as pd
import matplotlib.pyplot as plt

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
    if line and not line.startswith("%"):          # skip all comment lines
        rows.append([v.strip().strip("'\"") for v in line.split(",")])

df = pd.DataFrame(rows, columns=columns)
df = df.replace("?", pd.NA)                         # ARFF missing marker

# Convert numeric columns (bad values become NaN instead of crashing)
for col in ["ForkVA", "ForkW", "ServiceID"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

print("Columns:", df.columns.tolist())
print("Shape:", df.shape)
print("\nFirst 5 rows:\n", df.head())
print("\nData types:\n", df.dtypes)
print("\nMissing values:\n", df.isnull().sum())

print("\nConsumer Types:\n", df["Type"].value_counts())
print("\nSectors:\n", df["Sector"].value_counts())

print("\nElectricity Statistics:\n", df[["ForkVA", "ForkW"]].describe())
print("\nAverage by Consumer Type:\n",
      df.groupby("Type")[["ForkVA", "ForkW"]].mean().sort_values("ForkW", ascending=False))
print("\nTotal ForkW by Consumer Type:\n",
      df.groupby("Type")["ForkW"].sum().sort_values(ascending=False))

print("\nUnique Service IDs:", df["ServiceID"].nunique())
print("\nRecords per Service ID:\n", df["ServiceID"].value_counts().head(10))

service_usage = df.groupby(["ServiceID", "Type"])[["ForkVA", "ForkW"]].mean()
print("\nService Level Usage (top 20):\n",
      service_usage.sort_values("ForkW", ascending=False).head(20))

print("\nStd Dev by Consumer Type:\n", df.groupby("Type")[["ForkVA", "ForkW"]].std())

print("\nHighest Usage:\n", df.loc[df["ForkW"].idxmax()])
print("\nLowest Usage:\n", df.loc[df["ForkW"].idxmin()])

# Usage categories: check range first, then bin safely
print("\nForkW min/max:", df["ForkW"].min(), df["ForkW"].max())

df["Usage_Level"] = pd.cut(
    df["ForkW"],
    bins=[-float("inf"), 0.25, 0.50, 0.75, float("inf")],   # no value falls outside
    labels=["Low", "Medium", "High", "Very High"]
)
# Alternative if data is skewed: pd.qcut(df["ForkW"], 4, labels=[...], duplicates="drop")

usage_counts = df["Usage_Level"].value_counts().reindex(["Low", "Medium", "High", "Very High"])
print("\nUsage Categories:\n", usage_counts)

# Chart 1
average_usage = df.groupby("Type")["ForkW"].mean().sort_values(ascending=False)

plt.figure(figsize=(12, 6))
plt.bar(average_usage.index, average_usage.values)

plt.xticks(rotation=90)
plt.xlabel("Consumer Type")
plt.ylabel("Average ForkW")
plt.title("Average Electricity Usage by Consumer Type")

plt.tight_layout()


# Chart 2
plt.figure(figsize=(8, 5))
plt.bar(usage_counts.index.astype(str), usage_counts.values)

plt.xlabel("Usage Level")
plt.ylabel("Number of Records")
plt.title("Electricity Usage Level Distribution")

plt.tight_layout()

plt.show()
# ==========================================
# Chart 3: ForkVA vs ForkW
# ==========================================

plt.figure(figsize=(10, 6))

plt.scatter(df["ForkVA"], df["ForkW"], alpha=0.5)

plt.xlabel("ForkVA")
plt.ylabel("ForkW")
plt.title("Relationship Between ForkVA and ForkW")

plt.tight_layout()
plt.show()
# ==========================================
# Correlation Analysis
# ==========================================

correlation = df["ForkVA"].corr(df["ForkW"])

print("\nCorrelation between ForkVA and ForkW:")
print(correlation)
# ==========================================
# AUTOMATIC INSIGHTS
# ==========================================

print("\n" + "=" * 50)
print("AUTOMATIC ELECTRICITY USAGE INSIGHTS")
print("=" * 50)

print("\n1. Total Records:", len(df))

print("2. Number of Consumer Types:", df["Type"].nunique())

print("3. Number of Sectors:", df["Sector"].nunique())

print("4. Unique Service IDs:", df["ServiceID"].nunique())

print("5. Highest Average Consumer Type:", highest_type)

print("6. Highest Average ForkW:", round(highest_average, 4))

print("7. Lowest Average Consumer Type:", lowest_type)

print("8. Lowest Average ForkW:", round(lowest_average, 4))

print("9. ForkVA-ForkW Correlation:", round(correlation, 4))

print("\nUsage Level Distribution:")
print(usage_counts)