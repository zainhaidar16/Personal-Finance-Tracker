import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar instructions
st.sidebar.header("Instructions")
st.sidebar.info("""
1. Upload your transaction file (CSV or Excel).\n
2. Select columns for each visualization.\n
3. Analyze your data dynamically using visualizations and cards.\n
4. Download your processed data.
""")

# App title
st.title("💸 Personal Finance Tracker")
st.subheader("Track and visualize your expenses dynamically!")

# File uploader
uploaded_file = st.file_uploader("Upload your transaction file (CSV or Excel)", type=["csv", "xlsx"])

# If file is uploaded, show the columns selection
if uploaded_file:
    try:
        # Load the file
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
    else:
        # Show uploaded data preview
        st.write("### Uploaded Data Preview", data.head())

        # Column selection for analysis
        st.write("### Select Columns for Analysis and Visualizations")
        selected_date = st.selectbox("Select column for Date", data.columns)
        selected_amount = st.selectbox("Select column for Amount (Debit/Credit)", data.columns)
        selected_category = st.selectbox("Select column for Categories/Descriptions", data.columns)
        selected_type = st.selectbox("Select column for Type (Income/Expense)", data.columns)

        # Show visualization options once columns are selected
        if selected_date and selected_amount and selected_category and selected_type:
            # Preprocess data after column selection
            data[selected_date] = pd.to_datetime(data[selected_date], errors="coerce")
            
            # Convert Amount column to numeric, coercing errors to NaN
            data[selected_amount] = pd.to_numeric(data[selected_amount], errors="coerce")

            # Drop rows with NaN values in essential columns
            data = data.dropna(subset=[selected_date, selected_amount, selected_category, selected_type])

            # Convert selected_type column to string before applying .str methods
            data[selected_type] = data[selected_type].astype(str)

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

                # Ensure the summary is numeric before plotting
                if category_summary.empty or category_summary.isnull().all():
                    st.warning("No valid numeric data available for this visualization.")
                else:
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

                # Ensure the summary is numeric before plotting
                if monthly_summary.empty or monthly_summary.isnull().all():
                    st.warning("No valid numeric data available for this visualization.")
                else:
                    fig, ax = plt.subplots()
                    monthly_summary.plot(ax=ax, color="cyan", marker="o")
                    ax.set_title("Monthly Trends")
                    ax.set_ylabel("Amount")
                    st.pyplot(fig)

            # 3. Income vs Expenses
            with col3:
                st.write("#### Income vs Expenses")
                type_summary = data.groupby(selected_type)[selected_amount].sum()

                # Ensure the summary is numeric before plotting
                if type_summary.empty or type_summary.isnull().all():
                    st.warning("No valid numeric data available for this visualization.")
                else:
                    fig, ax = plt.subplots()
                    type_summary.plot(kind="bar", ax=ax, color=["green", "red"])
                    ax.set_title("Income vs Expenses")
                    st.pyplot(fig)

            # 4. Daily Transactions
            with col4:
                st.write("#### Daily Transactions")
                data["Day"] = data[selected_date].dt.date
                daily_summary = data.groupby("Day")[selected_amount].sum()

                # Ensure the summary is numeric before plotting
                if daily_summary.empty or daily_summary.isnull().all():
                    st.warning("No valid numeric data available for this visualization.")
                else:
                    fig, ax = plt.subplots()
                    daily_summary.plot(ax=ax, color="purple", marker="o")
                    ax.set_title("Daily Transactions")
                    ax.set_ylabel("Amount")
                    st.pyplot(fig)

            # 5. Top 5 Expense Categories
            with col5:
                st.write("#### Top 5 Categories")
                top_categories = data.groupby(selected_category)[selected_amount].sum().nlargest(5)

                # Ensure the summary is numeric before plotting
                if top_categories.empty or top_categories.isnull().all():
                    st.warning("No valid numeric data available for this visualization.")
                else:
                    fig, ax = plt.subplots()
                    sns.barplot(x=top_categories.values, y=top_categories.index, ax=ax, palette="Reds_r")
                    ax.set_title("Top 5 Categories")
                    ax.set_xlabel("Amount")
                    st.pyplot(fig)

            # 6. Cumulative Savings
            with col6:
                st.write("#### Cumulative Savings")
                data["Cumulative"] = data[selected_amount].cumsum()

                # Ensure the summary is numeric before plotting
                if data["Cumulative"].empty or data["Cumulative"].isnull().all():
                    st.warning("No valid numeric data available for this visualization.")
                else:
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
