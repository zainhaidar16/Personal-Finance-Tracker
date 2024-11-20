import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pdfplumber

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

# Sidebar instructions
st.sidebar.header("Instructions")
st.sidebar.info("""
1. Upload your bank statement file (Excel, CSV, or PDF).\n
2. Select columns for analysis and visualizations.\n
3. Explore your financial data dynamically using visualizations and cards.\n
4. Download the processed data.
""")

# App title
st.title("💸 Personal Finance Tracker")
st.subheader("Track and visualize your expenses dynamically!")

# File uploader
uploaded_file = st.file_uploader(
    "Upload your bank statement file (CSV, Excel, or PDF)", type=["csv", "xlsx", "pdf"]
)

if uploaded_file:
    # Load data based on file type
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            data = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".pdf"):
            # Extract tabular data from PDF using pdfplumber
            with pdfplumber.open(uploaded_file) as pdf:
                tables = []
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        tables.extend(table)
                # Convert list of tables to DataFrame
                data = pd.DataFrame(tables[1:], columns=tables[0])
        else:
            st.error("Unsupported file type!")
    except Exception as e:
        st.error(f"Error loading file: {e}")
    else:
        st.write("### Uploaded Data Preview", data.head())

        # Column selection for analysis
        st.write("### Select Columns for Analysis and Visualizations")
        selected_date = st.selectbox("Select column for Date", data.columns)
        selected_amount = st.selectbox("Select column for Amount (Debit/Credit)", data.columns)
        selected_category = st.selectbox("Select column for Categories/Descriptions", data.columns)
        selected_type = st.selectbox("Select column for Type (Income/Expense)", data.columns)

        # Preprocess data
        data[selected_date] = pd.to_datetime(data[selected_date], errors="coerce")
        data[selected_amount] = pd.to_numeric(data[selected_amount], errors="coerce")
        data = data.dropna(subset=[selected_date, selected_amount])

        # Calculate key metrics
        total_income = data[data[selected_type].str.lower() == "income"][selected_amount].sum()
        total_expenses = data[data[selected_type].str.lower() == "expense"][selected_amount].sum()
        net_savings = total_income - total_expenses

        # Visual Cards
        st.write("### Key Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("💸 Total Expenses", f"${abs(total_expenses):,.2f}")
        col2.metric("💰 Total Income", f"${total_income:,.2f}")
        col3.metric("📈 Net Savings", f"${net_savings:,.2f}")

        # Create visualizations
        st.write("### Explore Data with Six Visualizations")
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        # 1. Expense by Category
        with col1:
            st.write("#### Expense by Category")
            category_summary = data.groupby(selected_category)[selected_amount].sum()
            fig, ax = plt.subplots()
            category_summary.plot(kind="bar", ax=ax, color="skyblue")
            ax.set_title("Expenses by Category")
            ax.set_ylabel("Amount")
            st.pyplot(fig)

        # 2. Monthly Trends
        with col2:
            st.write("#### Monthly Trends")
            data["Month"] = data[selected_date].dt.to_period("M")
            monthly_summary = data.groupby("Month")[selected_amount].sum()
            fig, ax = plt.subplots()
            monthly_summary.plot(ax=ax, color="cyan", marker="o")
            ax.set_title("Monthly Trends")
            ax.set_ylabel("Amount")
            st.pyplot(fig)

        # 3. Income vs Expenses
        with col3:
            st.write("#### Income vs Expenses")
            type_summary = data.groupby(selected_type)[selected_amount].sum()
            fig, ax = plt.subplots()
            type_summary.plot(kind="bar", ax=ax, color=["green", "red"])
            ax.set_title("Income vs Expenses")
            st.pyplot(fig)

        # 4. Daily Transactions
        with col4:
            st.write("#### Daily Transactions")
            data["Day"] = data[selected_date].dt.date
            daily_summary = data.groupby("Day")[selected_amount].sum()
            fig, ax = plt.subplots()
            daily_summary.plot(ax=ax, color="purple", marker="o")
            ax.set_title("Daily Transactions")
            ax.set_ylabel("Amount")
            st.pyplot(fig)

        # 5. Top 5 Expense Categories
        with col5:
            st.write("#### Top 5 Categories")
            top_categories = data.groupby(selected_category)[selected_amount].sum().nlargest(5)
            fig, ax = plt.subplots()
            sns.barplot(x=top_categories.values, y=top_categories.index, ax=ax, palette="Reds_r")
            ax.set_title("Top 5 Categories")
            ax.set_xlabel("Amount")
            st.pyplot(fig)

        # 6. Cumulative Savings
        with col6:
            st.write("#### Cumulative Savings")
            data["Cumulative"] = data[selected_amount].cumsum()
            fig, ax = plt.subplots()
            ax.plot(data[selected_date], data["Cumulative"], color="green", marker="o")
            ax.set_title("Cumulative Savings")
            ax.set_ylabel("Amount")
            st.pyplot(fig)

        # Download Processed Data
        def convert_df(df):
            return df.to_csv(index=False).encode("utf-8")

        csv = convert_df(data)
        st.download_button(
            label="Download Processed Data",
            data=csv,
            file_name="processed_transactions.csv",
            mime="text/csv",
        )
