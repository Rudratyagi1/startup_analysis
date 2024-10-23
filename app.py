import seaborn as sns
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('startup_cleaned.csv')

# Clean the investor column by stripping any extra spaces
df['investors'] = df['investors'].str.strip()

# Check if the 'date' column exists and convert it to datetime format
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Convert to datetime, coerce errors to NaT
else:
    st.error("The 'date' column is missing from the dataset.")

# Drop rows with NaT in the 'date' column if any exist
df = df.dropna(subset=['date'])

# Add year column for analysis
df['year'] = df['date'].dt.year

# Sidebar for analysis selection
st.sidebar.title('STARTUP ANALYSIS')
option = st.sidebar.selectbox('SELECT ONE', ['OVERALL ANALYSIS', 'STARTUP', 'INVESTOR'])

if option == 'OVERALL ANALYSIS':
    st.title('OVERALL ANALYSIS')
    btn0 = st.sidebar.button('OVERALL ANALYSIS')
    if btn0:
        # Total number of startups and total amount invested
        total_startups = df['startup'].nunique()
        total_invested = df['amount'].sum()
        max_investment = df['amount'].max()
        avg_investment = df['amount'].mean()

        st.subheader('Total Startups and Investments')
        st.write(f"Total Startups: {total_startups}")
        st.write(f"Total Amount Invested: ${total_invested:,.2f}")
        st.write(f"Maximum Amount Invested: ${max_investment:,.2f}")
        st.write(f"Average Amount Invested: ${avg_investment:,.2f}")

        # Vertical Analysis: Top Vertical by Count and Total Investment
        vertical_analysis = df.groupby('vertical')['amount'].agg(['count', 'sum']).reset_index()
        top_vertical = vertical_analysis.loc[vertical_analysis['sum'].idxmax()]

        st.subheader('Vertical Analysis')
        st.write("Top Vertical by Count and Total Investment:")
        st.write(
            f"Vertical: {top_vertical['vertical']}, Count: {top_vertical['count']}, Total Investment: ${top_vertical['sum']:,.2f}")

        # Bar Chart for Vertical Analysis with Vertical Labels
        plt.figure(figsize=(10, 5))
        sns.barplot(x='count', y='vertical', data=vertical_analysis.sort_values('count', ascending=False),
                    palette='viridis')
        plt.title('Vertical Analysis: Count of Startups by Vertical')
        plt.xlabel('Count of Startups')
        plt.ylabel('Vertical')
        plt.xticks(rotation=90)  # Rotate x-axis labels vertically
        st.pyplot(plt)  # Display the plot in Streamlit
        plt.clf()  # Clear the current figure after displaying

        # Types of Rounds (formerly Types of Funding)
        round_types = df['round'].value_counts()
        st.subheader('Types of Rounds')
        st.bar_chart(round_types)

        # City-wise Funding Analysis
        city_funding = df.groupby('city')['amount'].sum().reset_index()
        st.subheader('City-wise Funding')
        st.bar_chart(city_funding.set_index('city'))

        # Top Startups Year-wise and Overall
        df['year'] = df['date'].dt.year
        top_startups_overall = df.groupby('startup')['amount'].sum().reset_index().nlargest(5, 'amount')
        st.subheader('Top Startups Overall')
        st.write(top_startups_overall)

        top_startups_yearwise = df.groupby(['year', 'startup'])['amount'].sum().reset_index()
        top_startups_yearwise = top_startups_yearwise.loc[top_startups_yearwise.groupby('year')['amount'].idxmax()]
        st.subheader('Top Startups Year-wise')
        st.write(top_startups_yearwise)

        # Top Investors
        top_investors = df.groupby('investors')['amount'].sum().reset_index().nlargest(5, 'amount')
        st.subheader('Top Investors')
        st.write(top_investors)

        # Funding Heatmap
        funding_heatmap_data = df.pivot_table(index='year', columns='vertical', values='amount', aggfunc='sum').fillna(
            0)
        st.subheader('Funding Heatmap')
        plt.figure(figsize=(10, 5))
        sns.heatmap(funding_heatmap_data, annot=True, fmt=".0f", cmap='Blues')
        plt.title('Funding Heatmap by Year and Vertical')
        st.pyplot(plt)


elif option == 'STARTUP':
    selected_startup = st.sidebar.selectbox('SELECT ONE', sorted(df['startup'].unique().tolist()))
    btn1 = st.sidebar.button('FIND STARTUP DETAILS')

    if btn1:
        st.title(f'STARTUP ANALYSIS: {selected_startup}')

        # Dropdown for selecting a startup
        selected_startup = st.selectbox('Select a Startup', df['startup'].unique())

        # Get the selected startup's data
        startup_data = df[df['startup'] == selected_startup].iloc[0]

        # Display Company POV details
        st.subheader('Company POV')
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Name**: {startup_data['startup']}")
            st.write(f"**Investors**: {startup_data['investors']}")
            st.write(f"**Vertical**: {startup_data['vertical']}")
            st.write(f"**Sub Vertical**: {startup_data['subvertical']}")
            st.write(f"**Location**: {startup_data['city']}")
            st.write(f"**Funding Rounds**: {startup_data['round']}")
            st.write(f"**amount**: {startup_data['amount']}")

        with col2:
            st.write(f"**Date**: {startup_data['date']}")
            st.write(f"**Similar Companies**: {startup_data['startup']}")

        # Visualize funding rounds if applicable
        funding_rounds_data = df[df['startup'] == selected_startup]['round'].value_counts()
        if not funding_rounds_data.empty:
            st.subheader('Funding Rounds Visualization')
            plt.figure(figsize=(8, 4))
            sns.barplot(x=funding_rounds_data.index, y=funding_rounds_data.values, palette='viridis')
            plt.title(f'Funding Rounds for {selected_startup}')
            plt.xlabel('Funding Rounds')
            plt.ylabel('Count')
            st.pyplot(plt)

        # Optionally, you could display a line chart for total funding over time if date information is available
        # Ensure 'date' is parsed as a datetime in your DataFrame
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            total_funding_over_time = df.groupby('date')['amount'].sum().reset_index()

            st.subheader('Total Funding Over Time')
            plt.figure(figsize=(10, 5))
            sns.lineplot(data=total_funding_over_time, x='date', y='amount', marker='o', color='blue')
            plt.title('Total Funding Over Time')
            plt.xlabel('Date')
            plt.ylabel('Total Funding Amount')
            st.pyplot(plt)

else:
    # Investor selection and analysis
    investor = st.sidebar.selectbox('SELECT ONE', sorted(set(df['investors'].str.split(',').sum())))
    btn2 = st.sidebar.button('FIND INVESTOR DETAILS')

    if btn2:
        st.title(f"Investor Analysis for {investor}")

        # Filter investments by the selected investor
        investor_data = df[df['investors'].str.contains(investor)]

        # Show recent investments
        st.subheader('Recent Investments')
        st.dataframe(
            investor_data[['date', 'startup', 'vertical','city','round', 'amount']].sort_values(by='date', ascending=False).head(5))

        # Show biggest investment
        st.subheader('Top 5 Biggest Investments')

        # Get the 5 largest investments
        top_investments = investor_data.nlargest(5, 'amount')

        # Display details of the top 5 investments
        for index, investment in top_investments.iterrows():
            st.write(
                f"Investment: {investment['startup']} with an amount of {investment['amount']}")

        # Create a bar chart for the top 5 investments
        st.bar_chart(top_investments.set_index('startup')['amount'])


        # Show general investment sector
        st.subheader('Preferred Investment Sectors')
        sector_investment = investor_data['vertical'].value_counts()
        st.bar_chart(sector_investment)

        # City-wise pie chart
        st.subheader('City-Wise Investments')
        city_investment = investor_data['city'].value_counts()
        fig, ax = plt.subplots()
        ax.pie(city_investment, labels=city_investment.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)

        # Year-on-year investment graph
        st.subheader('Year-on-Year Investments')
        investor_data['year'] = pd.to_datetime(investor_data['date']).dt.year
        yoy_investment = investor_data.groupby('year')['amount'].sum()
        st.line_chart(yoy_investment)

        # Similar investments
        st.subheader('Similar Investments')
        similar_investments = df[df['vertical'].isin(investor_data['vertical'].unique())]
        st.table(similar_investments[['startup', 'vertical', 'city', 'amount']].drop_duplicates().head())