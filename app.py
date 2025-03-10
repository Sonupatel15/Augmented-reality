import streamlit as st
import cv2
import numpy as np
import os
import sys
import time
import io
from PIL import Image
from datetime import datetime

# Append the src directory to sys.path so we can import ar_main.py
sys.path.append(os.path.join(os.getcwd(), "src"))

from objloader_simple import OBJ
from ar_main import render, projection_matrix

# Page configuration and styling
st.set_page_config(
    page_title="AR Vision",
    page_icon="🔮",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4A56E2;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6C757D;
        margin-bottom: 2rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #4A56E2;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #3A46C2;
    }
    .gallery-image {
        border-radius: 5px;
        margin: 5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">AR Vision Explorer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Interactive Augmented Reality Experience</p>', unsafe_allow_html=True)

# Initialize session state variables
if 'captured_images' not in st.session_state:
    st.session_state.captured_images = []
if 'current_model' not in st.session_state:
    st.session_state.current_model = "rat.obj"
if 'current_reference' not in st.session_state:
    st.session_state.current_reference = "rich.jpg"
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'show_match_points' not in st.session_state:
    st.session_state.show_match_points = False
if 'min_matches' not in st.session_state:
    st.session_state.min_matches = 10

# Function to start the camera and run AR processing
def start_camera():
    MIN_MATCHES = st.session_state.min_matches
    
    # Camera settings and configuration
    camera_parameters = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]])
    orb = cv2.BRISK_create()
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    dir_name = os.getcwd()
    
    model_path = os.path.join(dir_name, "reference", st.session_state.current_reference)
    obj_path = os.path.join(dir_name, "models", st.session_state.current_model)
    
    if not os.path.exists(model_path) or not os.path.exists(obj_path):
        st.error(f"Model or reference image not found! Looking for:\n{model_path}\n{obj_path}")
        return
    
    model = cv2.imread(model_path, 0)
    kp_model, des_model = orb.detectAndCompute(model, None)
    obj = OBJ(obj_path, swapyz=True)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        st.error("Could not open webcam")
        return
    
    stframe = st.empty()  # Placeholder for displaying frames
    status_text = st.empty()  # Placeholder for status text
    
    while st.session_state.camera_active:
        ret, frame = cap.read()
        if not ret:
            st.error("Unable to capture video")
            break
        
        frame_display = frame.copy()
        kp_frame, des_frame = orb.detectAndCompute(frame, None)
        
        if des_frame is not None:
            matches = bf.match(des_model, des_frame)
            matches = sorted(matches, key=lambda x: x.distance)
            
            # Display match count status
            status_text.text(f"Detected matches: {len(matches)}/{MIN_MATCHES} required")
            
            if len(matches) > MIN_MATCHES:
                src_pts = np.float32([kp_model[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                homography, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                
                if homography is not None:
                    try:
                        projection = projection_matrix(camera_parameters, homography)
                        frame_display = render(frame_display, obj, projection, model)
                    except Exception as e:
                        status_text.error(f"Error in rendering: {e}")
                        
            # Optionally display match points
            if st.session_state.show_match_points and len(matches) > 0:
                match_display = cv2.drawMatches(
                    model, kp_model, 
                    frame, kp_frame, 
                    matches[:10], None,
                    flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
                )
                frame_display = match_display
        
        frame_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
        stframe.image(frame_rgb, channels="RGB", use_column_width=True)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    status_text.empty()
    stframe.empty()
    st.session_state.camera_active = False

# Function to capture an image
def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Could not open webcam")
        return
    
    # Countdown
    for i in range(3, 0, -1):
        st.text(f"Capturing in {i}...")
        time.sleep(1)
    
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"captured_{timestamp}.jpg"
        
        # Save image to session state
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame_rgb)
        st.session_state.captured_images.append((pil_img, timestamp))
        
        # Save to disk
        if not os.path.exists("captures"):
            os.makedirs("captures")
        pil_img.save(os.path.join("captures", image_path))
        
        st.success(f"Image captured and saved!")
    else:
        st.error("Failed to capture image")

# Main UI layout with sidebar
with st.sidebar:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Control Panel")
    
    # Model selection
    st.markdown("### 3D Model Selection")
    models = ["rat.obj", "fox.obj", "dragon.obj"]  # Add your available models here
    st.session_state.current_model = st.selectbox("Choose 3D Model", models, index=0)
    
    # Reference image selection
    st.markdown("### Reference Image")
    references = ["rich.jpg", "marker.jpg", "table.jpg"]  # Add your available references here
    st.session_state.current_reference = st.selectbox("Choose Reference Image", references, index=0)
    
    # AR Settings
    st.markdown("### AR Settings")
    st.session_state.min_matches = st.slider("Minimum Matches", 5, 50, 10)
    st.session_state.show_match_points = st.checkbox("Show Match Points", False)
    
    # Camera controls
    st.markdown("### Camera Controls")
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.camera_active:
            if st.button("Start Camera", key="start"):
                st.session_state.camera_active = True
        else:
            if st.button("Stop Camera", key="stop"):
                st.session_state.camera_active = False
    
    with col2:
        if st.button("Capture Image"):
            capture_image()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main content area
st.markdown('<div class="card">', unsafe_allow_html=True)

# Camera view and feature display
if st.session_state.camera_active:
    start_camera()
else:
    st.markdown("### Click 'Start Camera' to begin the AR experience")
    st.markdown("Use the control panel on the left to adjust settings and capture images.")

st.markdown('</div>', unsafe_allow_html=True)

# Gallery of captured images
if st.session_state.captured_images:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## 📸 Captured Images Gallery")
    
    # Display images in a grid
    cols = st.columns(3)
    for i, (img, timestamp) in enumerate(st.session_state.captured_images):
        with cols[i % 3]:
            st.image(img, caption=f"Captured: {timestamp}", use_column_width=True)
            
            # Option to delete image
            if st.button(f"Delete", key=f"del_{i}"):
                del st.session_state.captured_images[i]
                st.experimental_rerun()
                
            # Option to download image
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG")
            st.download_button(
                label="Download",
                data=img_bytes.getvalue(),
                file_name=f"ar_capture_{timestamp}.jpg",
                mime="image/jpeg",
                key=f"download_{i}"
            )
    
    # Clear all images button
    if st.button("Clear All Images"):
        st.session_state.captured_images = []
        st.experimental_rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# Information and help section
with st.expander("ℹ️ How to Use This AR Application"):
    st.markdown("""
    ### Getting Started with AR Vision Explorer
    
    1. **Select a 3D model and reference image** from the sidebar
    2. **Click 'Start Camera'** to begin the AR experience
    3. **Show the reference image** to your camera to see the 3D model appear
    4. **Adjust the settings** to improve detection if needed
    5. **Capture images** to save your AR moments
    
    ### Troubleshooting
    
    - Make sure your reference images are in the `reference` folder
    - Make sure your 3D models are in the `models` folder
    - If detection is poor, try adjusting the minimum matches slider
    - Ensure good lighting conditions for better marker detection
    """)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 30px; padding: 10px; color: #6C757D; font-size: 0.8rem;">
    AR Vision Explorer | Created with Streamlit and OpenCV
</div>
""", unsafe_allow_html=True)