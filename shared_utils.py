import streamlit as st
import etl_engine

def render_analyst_tools(con):
    """Renders the standard Analyst Tools sidebar across the app."""
    with st.sidebar:
        st.header("Analyst Tools")
        st.markdown("---")

        # Data Sync Control
        st.subheader("🔄 Data Sync")
        days_to_fetch = st.slider("Lookback Days", min_value=1, max_value=30, value=7, help="How many days of attacks to fetch from the API.")
        
        if st.button("Fetch Latest Intel"):
            with st.spinner(f"Ingesting last {days_to_fetch} days of attacks..."):
                try:
                    etl_engine.ingest_ransomlook(con, days=days_to_fetch)
                    st.success("Cyber Threat Intel Updated.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Sync Failed: {e}")

        st.markdown("---")
        
        # Audio Notes
        st.subheader("🎙️ Voice Logs")
        
        # Privacy Disclaimer
        st.caption("⚠️ **Privacy Note**: Voice logs are processed in-session only and are automatically cleared when the session ends. No audio is permanently stored.")
        
        audio_value = st.audio_input("Record Intelligence Note")
        if audio_value:
            st.success("Note recorded and saved to session context.")
            st.audio(audio_value)
        
        st.markdown("---")
        st.info("System Status: ONLINE")
        if st.secrets.get("MOTHERDUCK_TOKEN"):
            st.success("Connected to MotherDuck 🦆")
        else:
            st.warning("Connected to Local DB 📂")
