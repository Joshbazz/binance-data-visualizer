from sqlalchemy import create_engine, text
import streamlit as st

class DatabaseConnection:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)

    def get_engine(self):
        return self.engine

    def is_database_empty(self):
        # Check if the database contains any tables
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = result.fetchall()
            if not tables:
                st.warning("The Database is Missing or Empty.")
                return True
            
            # Check if any table has rows
            for (table_name,) in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name};"))
                count = result.scalar()
                if count > 0:
                    st.success("Database Loaded")
                    return False
        
        return True