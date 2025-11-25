import sys
import os
import subprocess
import time
import socket
import runpy

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_backend():
    """Starts the backend server if it's not already running."""
    if not is_port_in_use(8000):
        print("Starting backend server...")
        
        # Prepare environment variables
        env = os.environ.copy()
        
        # Try to get API key from Streamlit secrets
        try:
            import streamlit as st
            if "GEMINI_API_KEY" in st.secrets:
                env["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
                print("Loaded GEMINI_API_KEY from secrets.")
        except Exception as e:
            print(f"Warning: Could not load secrets: {e}")

        # Start the backend as a subprocess
        # We use sys.executable to ensure the same Python environment is used
        subprocess.Popen(
            [sys.executable, "-m", "backend.main"],
            cwd=os.path.dirname(os.path.abspath(__file__)), # Run from root
            env=env
        )
        
        # Wait for the server to become available
        print("Waiting for backend to start...")
        for _ in range(30):
            if is_port_in_use(8000):
                print("Backend started successfully!")
                break
            time.sleep(1)
        else:
            print("Timeout waiting for backend to start.")
    else:
        print("Backend is already running.")

if __name__ == "__main__":
    # Start the backend service
    start_backend()
    
    # Run the Streamlit frontend
    # We use runpy to execute the script so it runs on every Streamlit rerun
    frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "streamlit_app.py")
    
    try:
        runpy.run_path(frontend_path, run_name="__main__")
    except Exception as e:
        import streamlit as st
        st.error(f"Failed to load the application: {e}")
