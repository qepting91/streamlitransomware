from streamlit.testing.v1 import AppTest


def test_app_load():
    """Verify the app loads without error."""
    # Note: 'app.py' is the new name
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    
    assert not at.exception
    # Check for title
    assert "RansomStat CTI" in at.title[0].value
