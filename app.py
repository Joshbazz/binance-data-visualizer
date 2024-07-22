import pandas as pd
import streamlit as st
from data_fetcher import DataFetcher
from database_connection import DatabaseConnection
from pygwalker.api.streamlit import StreamlitRenderer
from database_utils import get_stored_data, get_data_slice
from sesion_state_manager_updated import SessionStateManager

#################################INITIALIZER#########################################
st.set_page_config(layout="wide")
sm = SessionStateManager()

# Initialize the coins variable
coins = ('BTCUSDT', 'ETHUSDT', 'SOLUSDT') # Add more coins as needed
#################################INITIALIZER#########################################


#################################INTRO INFORMATION###################################
st.title("Interactive Crypto Data Viewer")
st.text("This section allows you to select portions of your SQL Database, and use PygWalker to interactively vizualize your data.")
#################################INTRO INFORMATION###################################


#################################DATABASE CONNECTION#################################
db_name = st.text_input("Enter the database name: (Coin_prices is the preloaded database)", "Coin_prices")
db_url = f'sqlite:///{db_name}.db'
db_connection = DatabaseConnection(db_url)
data_fetcher = DataFetcher(db_connection)

new_table = db_connection.is_database_empty()
if st.button("Show Summary Statistics"):
    summary = data_fetcher.get_summary_statistics()
    st.write(summary)
#################################DATABASE CONNECTION#################################


#################################DATA VIZ INPUTS#####################################
selected_coin = st.selectbox("Select a coin to show data", coins)
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=pd.to_datetime('2024-06-01').date())
with col2:
    end_date = st.date_input("End Date", value=pd.to_datetime('2024-06-30').date())
#################################DATA VIZ INPUTS#####################################


#################################PYGWALKER SECTION#################################
# Button to fetch data
if st.button("Interact With Your Data!"):
    try:
        # Ensure that db_name is defined and not empty
        if 'db_name' in locals() and db_name:
            df = get_data_slice(f'{db_name}.db', selected_coin, start_date, end_date)
            pyg_app = StreamlitRenderer(df)
            pyg_app.explorer()
            # Display DataFrame in Streamlit
            st.write("DataFrame:")
            st.dataframe(df)
        else:
            st.error("Please connect to an existing database, or create a new one.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
#################################PYGWALKER SECTION#################################


#################################LOCATION SECTION##################################
# Ask the user for their location
st.subheader("Location Verification")
st.text("Please be aware, you will not be able to fetch data from the Binance API if you are located in the US.")
st.text("In future updates, this will be handled with a connection to a domestically appropriate API.")
st.text("For now, this app ships with a pre-loaded SQL database for your use.")
st.text("Please select 'Other' from the dropdown to gain access")
location = st.selectbox("Where are you located?", ["Select...", "United States", "Other"])

if location == "Select...":
    st.warning("Please select your location to continue.")
elif location == "United States":
    st.error("Sorry, data fetching is not allowed from the United States.")
else:
    # Define the coins and date range
    coins = ('BTCUSDT', 'ETHUSDT', 'SOLUSDT') # Add more coins as needed

    # Allow multiple coin selection
    selected_coins = st.multiselect("Select coins for fetching data", coins)
#################################LOCATION SECTION##################################


#################################FETCH START DATE COLUMNS#################################
    col4, col5 = st.columns(2)
    with col4:
        fetch_start_date = st.date_input("Fetch Start Date", value=st.session_state.fetch_start_date)
    with col5:
        fetch_end_date = st.date_input("Fetch End Date", value=st.session_state.fetch_end_date)
    
    daterange = pd.date_range(fetch_start_date, fetch_end_date, freq='MS')
#################################FETCH START DATE COLUMNS#################################


#################################BINANCE API CALLS########################################
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
#################################BINANCE API CALLS########################################