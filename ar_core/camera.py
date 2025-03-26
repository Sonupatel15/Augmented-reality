# import cv2
# import streamlit as st

# def initialize_camera():
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         st.error("Could not open webcam")
#         return None
#     return cap

import cv2
import streamlit as st
import platform

def initialize_camera():
    """Initializes and returns the camera capture object."""
    try:
        # Streamlit Cloud does not support direct camera access
        if platform.system() == "Linux" and "google" in platform.release():
            st.error("⚠️ Camera access is not supported in this deployment environment.")
            return None
        
        # Use DirectShow backend for Windows (fixes some camera issues)
        if platform.system() == "Windows":
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            st.error("🚫 Could not access camera. Ensure the camera is connected and permissions are granted.")
            return None
        
        return cap

    except Exception as e:
        st.error(f"❌ Error initializing camera: {e}")
        return None

def release_camera(cap):
    """Releases the camera resource safely."""
    if cap is not None and cap.isOpened():
        cap.release()
        cv2.destroyAllWindows()