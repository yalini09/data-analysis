import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Customer Churn Dashboard", page_icon="📊", layout="wide")

st.title("📊 Customer Churn & Retention Dashboard")
st.caption("Demo dashboard — replace the sample CSV with your cleaned customer dataset before submitting.")

@st.cache_data
def load_data(file):
    data = pd.read_csv(file)
    required = {"CustomerID", "Contract", "TenureMonths", "PaymentMethod", "MonthlyCharges", "Churn"}
    missing = required - set(data.columns)
    if missing:
        st.error("Missing required columns: " + ", ".join(sorted(missing)))
        st.stop()
    data["TenureMonths"] = pd.to_numeric(data["TenureMonths"], errors="coerce")
    data["MonthlyCharges"] = pd.to_numeric(data["MonthlyCharges"], errors="coerce")
    data["Churn"] = data["Churn"].astype(str).str.strip().str.title()
    data = data.dropna(subset=["CustomerID", "Contract", "TenureMonths", "PaymentMethod", "MonthlyCharges", "Churn"])
    data = data[data["Churn"].isin(["Yes", "No"])]
    return data

uploaded = st.sidebar.file_uploader("Upload cleaned customer CSV (optional)", type=["csv"])
default_file = "customer_churn_demo.csv"
try:
    df = load_data(uploaded if uploaded is not None else default_file)
except FileNotFoundError:
    st.error("Place customer_churn_demo.csv in the same folder as app.py, or upload a CSV.")
    st.stop()

st.sidebar.header("Filters")
contracts = st.sidebar.multiselect("Contract", sorted(df["Contract"].unique()), default=sorted(df["Contract"].unique()))
min_tenure, max_tenure = int(df["TenureMonths"].min()), int(df["TenureMonths"].max())
tenure_range = st.sidebar.slider("Tenure (months)", min_tenure, max_tenure, (min_tenure, max_tenure))
payments = st.sidebar.multiselect("Payment method", sorted(df["PaymentMethod"].unique()), default=sorted(df["PaymentMethod"].unique()))

filtered = df[
    df["Contract"].isin(contracts)
    & df["TenureMonths"].between(tenure_range[0], tenure_range[1])
    & df["PaymentMethod"].isin(payments)
].copy()

if filtered.empty:
    st.warning("No customers match these filters. Adjust the filters.")
    st.stop()

total = len(filtered)
churned = int((filtered["Churn"] == "Yes").sum())
retained = int((filtered["Churn"] == "No").sum())
churn_rate = churned / total * 100 if total else 0
retention_rate = retained / total * 100 if total else 0
revenue_at_risk = filtered.loc[filtered["Churn"] == "Yes", "MonthlyCharges"].sum()
avg_tenure = filtered["TenureMonths"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Churn rate", f"{churn_rate:.1f}%", help="Churned customers ÷ all filtered customers.")
k2.metric("Retention rate", f"{retention_rate:.1f}%", help="Retained customers ÷ all filtered customers.")
k3.metric("Monthly revenue at risk", f"₹{revenue_at_risk:,.0f}", help="Sum of monthly charges for customers marked as churned; a proxy, not a forecast.")
k4.metric("Average tenure", f"{avg_tenure:.1f} months")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Churn by contract")
    contract_summary = filtered.groupby("Contract", as_index=False).agg(
        Customers=("CustomerID", "count"),
        Churned=("Churn", lambda s: (s == "Yes").sum())
    )
    contract_summary["Churn rate (%)"] = contract_summary["Churned"] / contract_summary["Customers"] * 100
    fig = px.bar(contract_summary, x="Contract", y="Churn rate (%)", color="Contract",
                 text=contract_summary["Churn rate (%)"].map(lambda x: f"{x:.1f}%"),
                 title="Churn rate by contract type",
                 color_discrete_sequence=["#4472C4", "#70AD47", "#ED7D31"])
    fig.update_layout(showlegend=False, yaxis_title="Churn rate (%)", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Customer status")
    status = filtered["Churn"].value_counts().rename_axis("Status").reset_index(name="Customers")
    fig2 = px.pie(status, names="Status", values="Customers", hole=0.55,
                  color="Status", color_discrete_map={"Yes":"#D55E00", "No":"#0072B2"},
                  title="Churned vs retained customers")
    st.plotly_chart(fig2, use_container_width=True)

left2, right2 = st.columns(2)
with left2:
    st.subheader("Churn by tenure")
    tenure_summary = filtered.assign(TenureBand=pd.cut(
        filtered["TenureMonths"], bins=[-1, 6, 12, 24, 48, 72],
        labels=["0–6", "7–12", "13–24", "25–48", "49–72"], include_lowest=True
    )).groupby("TenureBand", observed=False).agg(
        Customers=("CustomerID", "count"),
        Churned=("Churn", lambda s: (s == "Yes").sum())
    ).reset_index()
    tenure_summary["Churn rate (%)"] = (tenure_summary["Churned"] / tenure_summary["Customers"].replace(0, pd.NA) * 100).fillna(0)
    fig3 = px.line(tenure_summary, x="TenureBand", y="Churn rate (%)", markers=True,
                   title="Churn rate across tenure groups", color_discrete_sequence=["#6A3D9A"])
    fig3.update_layout(xaxis_title="Tenure (months)", yaxis_title="Churn rate (%)")
    st.plotly_chart(fig3, use_container_width=True)

with right2:
    st.subheader("Monthly charges by status")
    fig4 = px.box(filtered, x="Churn", y="MonthlyCharges", color="Churn",
                   color_discrete_map={"Yes":"#D55E00", "No":"#0072B2"},
                   title="Monthly charges: churned vs retained")
    fig4.update_layout(xaxis_title="Customer status", yaxis_title="Monthly charges (₹)")
    st.plotly_chart(fig4, use_container_width=True)

st.subheader("Filtered customer data")
st.dataframe(filtered, use_container_width=True, hide_index=True)
st.download_button("Download filtered data as CSV", filtered.to_csv(index=False).encode("utf-8"),
                   file_name="filtered_customer_churn.csv", mime="text/csv")

st.markdown("""
**Metric definitions**
- **Churn rate:** customers with `Churn = Yes` ÷ all customers in the filtered view × 100.
- **Retention rate:** customers with `Churn = No` ÷ all customers in the filtered view × 100.
- **Monthly revenue at risk:** sum of `MonthlyCharges` for customers marked as churned. This is a simple exposure proxy, not guaranteed future lost revenue.
- **Average tenure:** mean number of months customers have been with the company.
""")
