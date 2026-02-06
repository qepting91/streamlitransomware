from unittest.mock import patch

from etl_engine import ingest_ransomlook, init_db

# Sample data for mocking
SAMPLE_RANSOMLOOK_RESPONSE = [
    {
        "post_title": "Victim A",
        "group_name": "LockBit",
        "discovered": "2023-10-27 10:00:00",
        "country": "US",
        "link": "https://example.com"
    }
]

def test_init_db(mock_db_connection):
    """Verifies that init_db creates the necessary tables."""
    init_db(mock_db_connection)
    
    tables = mock_db_connection.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]
    
    assert 'victims' in table_names
    assert 'darkweb_assets' in table_names
    assert 'dorks' in table_names

@patch("httpx.Client")
def test_ingest_ransomlook(mock_client_class, mock_db_connection):
    """Tests RansomLook ingestion with mocked API response."""
    # Setup Mock
    mock_instance = mock_client_class.return_value.__enter__.return_value
    mock_instance.get.return_value.status_code = 200
    mock_instance.get.return_value.json.return_value = SAMPLE_RANSOMLOOK_RESPONSE
    
    # Init DB first to have tables
    init_db(mock_db_connection)
    
    # Run Ingestion
    ingest_ransomlook(mock_db_connection)
    
    # Checks
    result = mock_db_connection.execute("SELECT * FROM victims").fetchall()
    assert len(result) == 1
    assert result[0][0] == "Victim A"
    assert result[0][1] == "LockBit"

