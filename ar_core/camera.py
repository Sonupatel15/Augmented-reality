import cv2
import streamlit as st

def initialize_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Could not open webcam")
        return None
    return cap