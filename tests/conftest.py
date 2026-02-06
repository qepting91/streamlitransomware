
import duckdb
import pytest


@pytest.fixture
def mock_db_connection():
    """Returns an in-memory DuckDB connection."""
    con = duckdb.connect(':memory:')
    return con

@pytest.fixture
def mock_secrets():
    """Mocks streamlit secrets for testing."""
    import streamlit as st
    st.secrets = {"MOTHERDUCK_TOKEN": ""} # Empty to force local use in some paths, or mock values
    return st.secrets
