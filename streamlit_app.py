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

# Styling for the dark theme
st.markdown("""
    <style>
        .main {
            background-color: #121212;
            color: white;
        }
        h1, h2, h3, h4, h5, h6, p, div {
            color: white;
        }
        .stMetric {
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #333333;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for instructions
st.sidebar.header("Instructions")
st.sidebar.info("""
1. Upload your transaction file (CSV or Excel).\n
2. The app will automatically detect columns and values.\n
3. Visualize and analyze your expenses.\n
4. Download your processed data or summary report.
""")
st.sidebar.write("Happy tracking! 🎉")

# App title and header
st.title("💸 Personal Finance Tracker")
st.subheader("Track and visualize your expenses effortlessly!")

# File uploader
uploaded_file = st.file_uploader("Upload your transaction file (CSV or Excel)", type=["csv", "xlsx"])

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
        st.write("### Uploaded Data Preview", data.head())

        # Automatic column type detection
        st.write("### Analyzing Data Columns")
        st.write("Detected columns and sample values:")
        detected_columns = {}
        for col in data.columns:
            sample_values = data[col].dropna().unique()[:5]
            detected_columns[col] = sample_values
            st.write(f"**{col}**: {sample_values}")

        # Assign column types
        date_col = next((col for col in data.columns if "date" in col.lower()), None)
        desc_col = next((col for col in data.columns if "desc" in col.lower() or "category" in col.lower()), None)
        amount_col = next((col for col in data.columns if "amount" in col.lower() or "debit" in col.lower() or "credit" in col.lower()), None)
        income_expense_col = next((col for col in data.columns if "income" in col.lower() or "expense" in col.lower()), None)

        if not date_col or not amount_col or not income_expense_col:
            st.error("The required columns (Date, Amount, and Income/Expense) were not detected!")
        else:
            st.write(f"**Date Column**: {date_col}")
            st.write(f"**Description Column**: {desc_col}")
            st.write(f"**Amount Column**: {amount_col}")
            st.write(f"**Income/Expense Column**: {income_expense_col}")

            # Preprocessing
            data = data.rename(columns={date_col: "Date", desc_col: "Description", amount_col: "Amount", income_expense_col: "Type"})
            data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
            data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
            data.dropna(subset=["Date", "Amount"], inplace=True)

            # Calculate totals
            total_expenses = data[data["Type"].str.lower() == "expense"]["Amount"].sum()
            total_income = data[data["Type"].str.lower() == "income"]["Amount"].sum()
            net_savings = total_income - total_expenses

            # Insights
            st.write("### Key Metrics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Expenses", f"${total_expenses:,.2f}")
            col2.metric("Total Income", f"${total_income:,.2f}")
            col3.metric("Net Savings", f"${net_savings:,.2f}")

            # Visualizations
            st.write("### Expense Breakdown by Category")
            if desc_col:
                category_summary = data[data["Type"].str.lower() == "expense"].groupby("Description")["Amount"].sum()
                fig, ax = plt.subplots(figsize=(10, 6))
                category_summary.plot(kind="bar", ax=ax, color="skyblue")
                ax.set_title("Expenses by Category")
                ax.set_ylabel("Amount ($)")
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
                summary = data.groupby("Description")["Amount"].sum()
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
