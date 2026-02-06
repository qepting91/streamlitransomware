import io

import duckdb
import speech_recognition as sr
import streamlit as st

import etl_engine


# --- Database Connection ---
@st.cache_resource
def get_db_connection():
    """Connects to MotherDuck or Local DuckDB."""
    try:
        # Check for token at top level or nested in [database]
        token = st.secrets.get("MOTHERDUCK_TOKEN") or st.secrets.get("database", {}).get("motherduck_token")
        
        if token:
            return duckdb.connect(f'md:?motherduck_token={token}')
        else:
            # Fallback to local (read-only)
            return duckdb.connect('ransomstat.duckdb', read_only=True)
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None


def render_analyst_tools(con):
    """Renders the standard Analyst Tools sidebar across the app."""
    with st.sidebar:
        st.header("Analyst Tools")

        # --- Section 1: Data Sync (Collapsible) ---
        with st.expander("🔄 Data Sync Settings", expanded=False):
            days_to_fetch = st.slider("Lookback Days", min_value=1, max_value=30, value=7, help="How many days of attacks to fetch from the API.")
            
            if st.button("Fetch Latest Intel", use_container_width=True):
                with st.spinner(f"Ingesting last {days_to_fetch} days..."):
                    try:
                        etl_engine.ingest_ransomlook(con, days=days_to_fetch)
                        st.success("Intel Updated")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Sync Failed: {e}")

        # --- DEBUG: State Monitor (Temporary) ---
        with st.expander("🐞 State Monitor", expanded=False):
            st.json(st.session_state)

        # --- Section 2: Voice Intelligence (Persisted) ---
        with st.expander("🎙️ Voice Intelligence", expanded=True):
            
            # 1. Initialize Persistent State
            if "voice_log" not in st.session_state:
                st.session_state["voice_log"] = {"bytes": None, "transcript": None}

            # 2. Define Callback
            def process_audio_callback():
                # Get widget state directly
                widget_audio = st.session_state.get("voice_widget_key")
                
                if widget_audio:
                    try:
                        # Attempt to read. This fails if Streamlit has marked it as 'DeletedFile' during nav
                        new_bytes = widget_audio.read()
                        
                        if len(new_bytes) > 100:
                            try:
                                r = sr.Recognizer()
                                with sr.AudioFile(io.BytesIO(new_bytes)) as source:
                                    audio_data = r.record(source)
                                    text = r.recognize_google(audio_data)
                            except Exception as e:
                                text = f"[Transcription Error: {e}]"
                            
                            # SAVE to persistent state
                            st.session_state["voice_log"] = {
                                "bytes": new_bytes,
                                "transcript": text
                            }
                    except AttributeError:
                        # Swallows 'DeletedFile' object has no attribute 'read'
                        # This happens on page navigation; we just ignore it to keep existing state.
                        pass
                    except Exception:
                        pass

            # 3. Input Widget (With Callback)
            st.audio_input(
                "Record Note", 
                label_visibility="collapsed", 
                key="voice_widget_key", 
                on_change=process_audio_callback
            )

            # 4. Render Persistent Log (Decoupled from Widget)
            saved_log = st.session_state["voice_log"]
            
            if saved_log["bytes"]:
                st.audio(saved_log["bytes"], format='audio/wav')
                
                if saved_log["transcript"]:
                    st.text_area("Transcript", saved_log["transcript"], height=100)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button("💾 Wav", saved_log["bytes"], "note.wav", "audio/wav", use_container_width=True)
                with col2:
                    if saved_log["transcript"]:
                        st.download_button("📄 MD", saved_log["transcript"], "transcript.md", "text/markdown", use_container_width=True)
                        
                if st.button("Clear Log", use_container_width=True):
                    st.session_state["voice_log"] = {"bytes": None, "transcript": None}
                    # We intentionally don't clear the widget key to avoid complex sync issues, 
                    # but the users next recording will overwrite.
                    st.rerun()

        # --- Section 3: Mission Notes (Persisted) ---
        with st.expander("📝 Mission Notes", expanded=True):
            if "notepad_content" not in st.session_state:
                st.session_state["notepad_content"] = ""
                
            # Use on_change callback to ensure sync? 
            # Actually, standard key binding is robust enough for simple text area.
            current_notes = st.text_area(
                "Scratchpad", 
                value=st.session_state["notepad_content"], 
                height=150, 
                label_visibility="collapsed",
                placeholder="Type mission notes here...",
                key="mission_notepad" 
            )
            # Sync Key to State manually if needed, but key="mission_notepad" stores in session_state.mission_notepad
            # We'll just read from the widget key next time or sync it here for safety.
            st.session_state["notepad_content"] = current_notes

            if current_notes:
                st.download_button("💾 Save Notes", f"# Mission Notes\n\n{current_notes}", "notes.md", "text/markdown", use_container_width=True)

        # --- Footer ---
        st.markdown("---")
        if st.secrets.get("MOTHERDUCK_TOKEN") or st.secrets.get("database", {}).get("motherduck_token"):
            st.caption("🟢 Connected: MotherDuck")
        else:
            st.caption("📂 Connected: Local DB")
