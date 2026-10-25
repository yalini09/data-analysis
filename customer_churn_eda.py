"""
Customer Churn Dataset: Profiling, Cleaning, Validation and EDA
Requirements: pandas, numpy, matplotlib, openpyxl
Run: python customer_churn_eda.py
Place customer_churn_sample.csv in the same folder as this script.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("customer_churn_sample.csv")

# 1. PROFILE
print("Shape:", df.shape)
print("\nData types:\n", df.dtypes)
print("\nMissing values:\n", df.isna().sum())
print("\nExact duplicate rows:", df.duplicated().sum())
print("\nUnique CustomerIDs:", df["CustomerID"].nunique())

# 2. CLEAN
clean = df.copy()
clean["CustomerID"] = clean["CustomerID"].astype("string")
for col in ["Gender", "SubscriptionType", "ContractType", "PaymentMethod", "Churn"]:
    clean[col] = clean[col].astype("category")

# Assumptions:
# - CustomerID should be unique.
# - No missing-value imputation is needed if there are no missing values.
# - Do not automatically delete IQR outliers; investigate them first.
# - TotalCharges is expected to approximately equal MonthlyCharges * TenureMonths
#   for this sample, but business rules may differ in real datasets.

# 3. OUTLIER SCREENING (IQR)
numeric_cols = df.select_dtypes(include=np.number).columns
for col in numeric_cols:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    flagged = df.loc[(df[col] < lower) | (df[col] > upper), col]
    print(f"\n{col}: IQR bounds=({lower:.2f}, {upper:.2f}); outliers={flagged.tolist()}")

# 4. SUMMARY STATISTICS
print("\nSummary statistics:\n", clean.describe(include="all"))

# 5. VALIDATION
assert clean["CustomerID"].is_unique, "CustomerID values are not unique."
assert clean.duplicated().sum() == 0, "Exact duplicate rows remain."
assert (df[["Age", "TenureMonths", "MonthlyCharges", "TotalCharges", "SupportTickets"]] >= 0).all().all(), "Negative value found."

expected = df["MonthlyCharges"] * df["TenureMonths"]
within_tolerance = (df["TotalCharges"] - expected).abs() <= 0.02
print(f"\nTotalCharges arithmetic check: {within_tolerance.sum()}/{len(df)} rows within 0.02")

# 6. SAVE CLEANED DATA
clean.to_csv("customer_churn_cleaned.csv", index=False)

# 7. DISTRIBUTIONS
for col in ["Age", "TenureMonths", "MonthlyCharges", "SupportTickets"]:
    df[col].plot(kind="hist", bins=min(8, df[col].nunique()), edgecolor="black", title=f"{col} Distribution")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(f"{col.lower()}_distribution.png", dpi=150)
    plt.show()

df["Churn"].value_counts().plot(kind="bar", title="Customer Churn Distribution")
plt.xlabel("Churn")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.savefig("churn_distribution.png", dpi=150)
plt.show()
