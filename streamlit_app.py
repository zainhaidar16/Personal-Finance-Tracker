import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling
st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
        }
        .stMetric {
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #ffffff;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for instructions
st.sidebar.header("Instructions")
st.sidebar.info("""
1. Upload your transaction file (CSV or Excel).\n
2. Ensure columns for Date, Amount, and Description exist.\n
3. Visualize and analyze your expenses.\n
4. Download your processed data or summary report.
""")
st.sidebar.write("Happy tracking! 🎉")

# App title and header
st.title("💸 Personal Finance Tracker")
st.subheader("Track and visualize your expenses effortlessly!")

# File uploader
uploaded_file = st.file_uploader("Upload your transaction file (CSV or Excel)", type=["csv", "xlsx"])

# Default categories
default_categories = {
    "groceries": "Food",
    "electricity": "Utilities",
    "movie": "Entertainment",
    "dining": "Food",
    "gas": "Transportation",
    "salary": "Income",
    "rent": "Housing",
    "insurance": "Insurance",
    "other": "Other"
}

if uploaded_file:
    # Load the data
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
    else:
        # Preview data
        st.write("### Uploaded Data", data.head())

        # Preprocessing
        data.columns = [col.strip().lower() for col in data.columns]  # Normalize column names
        if "date" in data.columns:
            data["date"] = pd.to_datetime(data["date"])
        else:
            st.error("Date column not found!")

        if "amount" not in data.columns:
            st.error("Amount column not found!")

        if "description" not in data.columns:
            st.error("Description column not found!")

        # Categorize transactions
        data["category"] = data["description"].map(
            lambda x: default_categories.get(x.lower(), "Other")
        )

        # Insights
        st.write("### Key Metrics")
        col1, col2, col3 = st.columns(3)
        total_expenses = data[data["amount"] < 0]["amount"].sum()
        total_income = data[data["amount"] > 0]["amount"].sum()
        net_savings = total_income + total_expenses

        col1.metric("Total Expenses", f"${-total_expenses:,.2f}")
        col2.metric("Total Income", f"${total_income:,.2f}")
        col3.metric("Net Savings", f"${net_savings:,.2f}")

        # Visualizations
        st.write("### Expense Breakdown by Category")
        category_summary = data[data["amount"] < 0].groupby("category")["amount"].sum().abs()
        fig, ax = plt.subplots(figsize=(10, 6))
        category_summary.plot(kind="pie", autopct="%1.1f%%", startangle=140, ax=ax, legend=True)
        ax.set_ylabel("")
        st.pyplot(fig)

        st.write("### Monthly Expense Trends")
        data["month"] = data["date"].dt.to_period("M")
        monthly_expenses = data[data["amount"] < 0].groupby("month")["amount"].sum().abs()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=monthly_expenses, marker="o", ax=ax)
        ax.set_title("Monthly Expenses")
        ax.set_ylabel("Amount ($)")
        ax.set_xlabel("Month")
        st.pyplot(fig)

        # Export processed data
        def convert_df(df):
            return df.to_csv(index=False).encode("utf-8")

        csv = convert_df(data)
        st.download_button(
            label="Download Processed Data",
            data=csv,
            file_name="processed_transactions.csv",
            mime="text/csv",
        )

        # Generate report
        def generate_report(data):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine="xlsxwriter")
            data.to_excel(writer, index=False, sheet_name="Transactions")
            summary = data.groupby("category")["amount"].sum()
            summary.to_excel(writer, sheet_name="Summary")
            writer.save()
            return output.getvalue()

        report = generate_report(data)
        st.download_button(
            label="Download Summary Report",
            data=report,
            file_name="summary_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

