import streamlit as st
from datetime import datetime

class SessionStateManager:
    def __init__(self):
        self._initialize_state()

    def _initialize_state(self):
        # Check if session state has been initialized; if not, create default values
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            self._initialize_default_states()

    def _initialize_default_states(self):
        default_states = {
            'data_downloaded': False,
            'fetched_data': False,
            'summary_stats': None,
            'existing_database': False,
            'db_name': None,
            'fetch_start_date': datetime.today().date(),
            'fetch_end_date': datetime.today().date(),
            'view_start_date': datetime.today().date(),
            'view_end_date': datetime.today().date(),
        }
        for key, value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def set_state(self, key, value):
        if key in st.session_state:
            st.session_state[key] = value
        else:
            raise KeyError(f"Session state key '{key}' does not exist.")

    def get_state(self, key):
        if key in st.session_state:
            return st.session_state[key]
        else:
            raise KeyError(f"Session state key '{key}' does not exist.")
    
    def create_state(self, key, value):
        if key not in st.session_state:
            st.session_state[key] = value
        return st.session_state[key]

    def check_state(self, key):
        return key in st.session_state and st.session_state[key]