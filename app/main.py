import streamlit as st
from app.ui import render_ui
from app.file_utils import cleanup_temp_files
import atexit

# Main entry point
def main():
    # Set up the UI
    render_ui()

    # Register cleanup function for temp files
    atexit.register(cleanup_temp_files)

if __name__ == "__main__":
    main()