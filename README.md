# Customer Churn Dashboard (Beginner Project)

This project creates an interactive dashboard with:
- Churn rate
- Retention rate
- Monthly revenue at risk
- Average tenure
- Filters for contract type, tenure, and payment method
- Charts for contract churn, customer status, tenure groups, and monthly charges
- Downloadable filtered customer data

## Important
`customer_churn_demo.csv` is synthetic demo data created only to demonstrate the dashboard. Replace it with your cleaned dataset before presenting it as real analysis.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```
4. Streamlit opens the dashboard in your browser.

## Publish a public proof link (Streamlit Community Cloud)
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `customer_churn_demo.csv`.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Choose the repository, branch, and `app.py` as the main file.
4. Deploy, wait for the app to build, and copy the public app URL.
5. Test the URL in a private/incognito browser window.

## Expected CSV columns
- `CustomerID`: unique customer ID
- `Contract`: contract category
- `TenureMonths`: tenure in months (numeric)
- `PaymentMethod`: payment category
- `MonthlyCharges`: monthly amount (numeric)
- `Churn`: `Yes` or `No`

## Metric definitions
- Churn rate = churned customers / total customers × 100
- Retention rate = retained customers / total customers × 100
- Monthly revenue at risk = sum of monthly charges for churned customers
- Average tenure = mean tenure in months

## Interpretation caveat
The demo data is randomly generated and is not evidence of real business performance. The revenue-at-risk KPI is a simple monthly-charge exposure estimate and should not be described as a confirmed forecast.
