import streamlit as st
import pandas as pd
from pygwalker.api.streamlit import StreamlitRenderer
import sqlite3
from sqlalchemy import create_engine
from data_fetcher import DataFetcher
from database_connection import DatabaseConnection
from sesion_state_manager_updated import SessionStateManager

st.set_page_config(layout="wide")
sm = SessionStateManager()
# data_fetcher = DataFetcher()

st.title("Interactive Crypto Data Viewer")
st.text("Welcome! This App will allow you to download data from Binance and store it to a SQL Database,")
st.text("and interact with your data with PygWalker!")
st.divider()
# Ask the user for their location
st.subheader("Location Verification")
st.text("Please be aware, you will not be able to fetch data from the Binance API if you are located in the US.")
st.text("In future updates, this will be handled with a connection to a domestically appropriate API.")
st.text("For now, this app ships with a pre-loaded SQL database for your use.")
st.text("Please select 'Other' from the dropdown to gain access")
location = st.selectbox("Where are you located?", ["Select...", "United States", "Other"])

# Initialize the coins variable
coins = ()

if 'data_downloaded' not in st.session_state:
    st.session_state.data_downloaded = False

if 'fetched_data' not in st.session_state:
    st.session_state.fetched_data = False


if location == "Select...":
    st.warning("Please select your location to continue.")
elif location == "United States":
    st.error("Sorry, data fetching is not allowed from the United States.")
else:
    # Ask the user for the database name
    db_name = st.text_input("Enter the database name:", "Coin_prices")
    db_url = f'sqlite:///{db_name}.db'
    db_connection = DatabaseConnection(db_url)
    data_fetcher = DataFetcher(db_connection)

    if st.button("Show Summary Statistics"):
        summary = data_fetcher.get_summary_statistics()
        st.write(summary)

    # Define the coins and date range
    coins = ('BTCUSDT', 'ETHUSDT', 'SOLUSDT') # Add more coins as needed

    # Allow multiple coin selection
    selected_coins = st.multiselect("Select coins for fetching data", coins)

    # def fetch_date_range_selector(self):
    #     # Date inputs with session state values
    fetch_start_date = st.date_input("Fetch Start Date", value=st.session_state.fetch_start_date)
    fetch_end_date = st.date_input("Fetch End Date")

    daterange = pd.date_range(fetch_start_date, fetch_end_date, freq='MS')
    # daterange = pd.date_range('2024-06-01', '2024-06-10', freq='MS')

    st.text("Click the button below to get data from Binance for the Coins")
    st.text("and dates selected above.")
    if st.button("Fetch Data"):
        if selected_coins:
            with st.spinner("Fetching data..."):
                data_fetcher.fetch_and_store_data(selected_coins, daterange)
            st.success("Data fetching complete!")
            st.session_state.data_downloaded = True
            st.session_state.fetched_data = True
        else:
            st.error("Please select at least one coin.")

st.divider()
# Streamlit UI components
st.title("SQLite Database Data Slice to DataFrame")
st.text("This section allows you to select portions of your SQL Database,")
st.text("and use PygWalker to interactively vizualize your data.")

def get_stored_data(symbol, engine):
    query = f"SELECT * FROM {symbol}"
    df = pd.read_sql(query, engine)
    return df

if st.session_state.data_downloaded:
    # Display data for a selected coin
    st.text("Please select a coin before moving to the interactive charts below")
    selected_coin = st.selectbox("Select a coin to show data", coins)

    st.text("The button below will show you all available data,")
    st.text("whether downloaded from binance, or from the pre-loaded database.")
    if st.button("Show Data"):
        if st.session_state.fetched_data:
            df = get_stored_data(selected_coin, data_fetcher.engine)
            st.write(df)
        else:
            st.warning("Please fetch data before trying to show it.")

# Function to connect to the SQLite database and retrieve a slice of data
def get_data_slice(database, symbol, start_date, end_date):
    # NOTE: we need to inject query dates here
    conn = sqlite3.connect(database)
    query = f"""
    SELECT * FROM {symbol}
    WHERE Time >= '{start_date} 00:00:00.000000'
    AND Time < datetime('{end_date}', '+1 day', 'start of day');
    """

    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Inputs for date range
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

# Button to fetch data
if st.button("Retrieve Data"):
    try:
        # Ensure that db_name is defined and not empty
        if 'db_name' in locals() and db_name:
            df = get_data_slice(f'{db_name}.db', selected_coin, start_date, end_date)
            
            # Display DataFrame in Streamlit
            st.write("DataFrame:")
            st.dataframe(df)
            
            pyg_app = StreamlitRenderer(df)
            pyg_app.explorer()
        else:
            st.error("Please connect to an existing database, or create a new one.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

