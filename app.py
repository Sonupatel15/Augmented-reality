import streamlit as st
import cv2
import numpy as np
import os
import sys
import time
import tempfile
from PIL import Image
from datetime import datetime

# Import AR backend functionality
from objloader_simple import OBJ
from ar_main import render, projection_matrix, overlay_image, MIN_MATCHES

# Page configuration and styling
st.set_page_config(
    page_title="AR Wedding Card Experience",
    page_icon="💍",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF4B8B;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6C757D;
        margin-bottom: 2rem;
        text-align: center;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #FF4B8B;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #E3407C;
    }
    .capture-btn {
        background-color: #20C997;
    }
    .stSelectbox label, .stSlider label {
        font-weight: bold;
        color: #444;
    }
    .view-container {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 10px;
        background-color: #f0f0f0;
    }
    .gallery-image {
        border-radius: 5px;
        margin: 5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<h1 class="main-header">AR Wedding Card Experience</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Create magical wedding memories with augmented reality</p>', unsafe_allow_html=True)

# Initialize session state variables
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'min_matches' not in st.session_state:
    st.session_state.min_matches = 10
if 'captured_images' not in st.session_state:
    st.session_state.captured_images = []
if 'overlay_type' not in st.session_state:
    st.session_state.overlay_type = "3D"
if 'temp_files' not in st.session_state:
    st.session_state.temp_files = []

# Create layout with two columns (sidebar and main content)
col1, col2 = st.columns([1, 3])

# Sidebar with controls
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📱 Control Panel")
    
    # Overlay selection
    st.markdown("### Overlay Type")
    overlay_type = st.selectbox("What would you like to display?", 
                                ["3D", "IMAGE", "VIDEO"], 
                                key="overlay_selector")
    st.session_state.overlay_type = overlay_type
    
    # Reference image selection
    st.markdown("### Reference Image")
    reference_options = ["Upload your own"]
    
    # Check if reference_images directory exists and add files
    if os.path.exists("reference_images"):
        reference_files = [f for f in os.listdir("reference_images") 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        reference_options.extend(reference_files)
    
    reference_selection = st.selectbox("Select wedding card reference", 
                                       reference_options,
                                       index=0 if len(reference_options) > 0 else 0)
    
    # Handle reference image upload
    if reference_selection == "Upload your own":
        uploaded_reference = st.file_uploader("Upload wedding card", 
                                              type=["jpg", "jpeg", "png"],
                                              key="reference_uploader")
        if uploaded_reference is not None:
            # Save uploaded reference to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_ref:
                tmp_ref.write(uploaded_reference.read())
                reference_path = tmp_ref.name
                st.session_state.temp_files.append(reference_path)
                st.session_state.reference_path = reference_path
                st.image(reference_path, caption="Your reference image", width=200)
    else:
        st.session_state.reference_path = os.path.join("reference_images", reference_selection)
        try:
            st.image(st.session_state.reference_path, caption="Reference Image", width=200)
        except:
            st.error(f"Could not display reference image: {st.session_state.reference_path}")
    
    # Conditional options based on overlay type
    if overlay_type == "3D":
        st.markdown("### 3D Model Selection")
        model_options = ["Default (Fox)"]
        
        # Check if models directory exists and add files
        if os.path.exists("models"):
            model_files = [f for f in os.listdir("models") if f.lower().endswith('.obj')]
            model_options.extend(model_files)
        
        model_selection = st.selectbox("Select 3D model", model_options)
        
        if model_selection == "Default (Fox)":
            st.session_state.model_path = "models/fox.obj"
        else:
            st.session_state.model_path = os.path.join("models", model_selection)
    
    elif overlay_type == "IMAGE":
        st.markdown("### Image Overlay")
        uploaded_image = st.file_uploader("Upload image overlay", type=["jpg", "jpeg", "png"])
        
        if uploaded_image is not None:
            # Save uploaded image to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_img:
                tmp_img.write(uploaded_image.read())
                image_path = tmp_img.name
                st.session_state.temp_files.append(image_path)
                st.session_state.image_path = image_path
                st.image(image_path, caption="Your image overlay", width=200)
    
    elif overlay_type == "VIDEO":
        st.markdown("### Video Overlay")
        uploaded_video = st.file_uploader("Upload video overlay", type=["mp4", "mov", "avi"])
        
        if uploaded_video is not None:
            # Save uploaded video to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_vid:
                tmp_vid.write(uploaded_video.read())
                video_path = tmp_vid.name
                st.session_state.temp_files.append(video_path)
                st.session_state.video_path = video_path
                st.video(video_path, start_time=0)
    
    # AR Settings
    st.markdown("### Settings")
    st.session_state.min_matches = st.slider("Feature point matches", 5, 50, 10, 
                                             help="Minimum matches required for detection")
    
    # Camera control
    st.markdown("### Camera Control")
    camera_button_label = "Stop Camera" if st.session_state.camera_active else "Start Camera"
    if st.button(camera_button_label, key="camera_toggle"):
        st.session_state.camera_active = not st.session_state.camera_active
        if not st.session_state.camera_active:
            st.experimental_rerun()
    
    # Capture image button
    if st.session_state.camera_active:
        if st.button("📸 Capture Moment", key="capture_btn"):
            st.session_state.capture_requested = True
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main content area with camera feed and gallery
with col2:
    # Function to start the camera and run AR processing
    def run_ar_camera():
        # Check if reference path is set
        if not hasattr(st.session_state, 'reference_path'):
            st.error("Please select or upload a reference image")
            st.session_state.camera_active = False
            return
        
        # Load reference image
        try:
            reference_image = cv2.imread(st.session_state.reference_path, 0)
            if reference_image is None:
                st.error(f"Failed to load reference image: {st.session_state.reference_path}")
                st.session_state.camera_active = False
                return
        except Exception as e:
            st.error(f"Error loading reference image: {e}")
            st.session_state.camera_active = False
            return
        
        # Initialize AR components
        camera_params = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]])
        orb = cv2.ORB_create(nfeatures=5000)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        # Get keypoints and descriptors for reference image
        kp_model, des_model = orb.detectAndCompute(reference_image, None)
        
        # Load 3D model if required
        obj = None
        if st.session_state.overlay_type == "3D":
            try:
                obj = OBJ(st.session_state.model_path, swapyz=True)
            except Exception as e:
                st.error(f"Error loading 3D model: {e}")
                st.session_state.camera_active = False
                return
        
        # Load image overlay if required
        image_overlay = None
        if st.session_state.overlay_type == "IMAGE":
            try:
                image_overlay = cv2.imread(st.session_state.image_path)
            except:
                st.error("Failed to load image overlay")
                st.session_state.camera_active = False
                return
        
        # Load video if required
        video_cap = None  
        if st.session_state.overlay_type == "VIDEO":
            try:
                video_cap = cv2.VideoCapture(st.session_state.video_path)
                if not video_cap.isOpened():
                    st.error("Failed to open video file")
                    st.session_state.camera_active = False
                    return
            except:
                st.error("Failed to load video overlay")
                st.session_state.camera_active = False
                return
        
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open webcam")
            st.session_state.camera_active = False
            return
        
        # Create placeholder for camera feed
        camera_placeholder = st.empty()
        status_text = st.empty()
        
        # Initialize capture requested flag
        if 'capture_requested' not in st.session_state:
            st.session_state.capture_requested = False
        
        # Main processing loop
        while st.session_state.camera_active:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to capture frame from camera")
                break
            
            # Process frame
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            kp_frame, des_frame = orb.detectAndCompute(gray_frame, None)
            
            # Match features
            if des_frame is not None and len(des_frame) > 0:
                matches = bf.match(des_model, des_frame)
                matches = sorted(matches, key=lambda x: x.distance)
                
                # Display match count status
                status_text.text(f"Detected matches: {len(matches)}/{st.session_state.min_matches} required")
                
                if len(matches) > st.session_state.min_matches:
                    # Extract matched keypoints
                    src_pts = np.float32([kp_model[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                    dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                    
                    # Find homography matrix
                    homography, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                    
                    if homography is not None:
                        try:
                            # Based on overlay type, render appropriate content
                            if st.session_state.overlay_type == "3D":
                                # For 3D model
                                projection = projection_matrix(camera_params, homography)
                                frame = render(frame, obj, projection, reference_image)
                            
                            elif st.session_state.overlay_type == "IMAGE" and image_overlay is not None:
                                # For image overlay
                                frame = overlay_image(frame, homography, image_overlay)
                            
                            elif st.session_state.overlay_type == "VIDEO" and video_cap is not None:
                                # For video overlay
                                ret_vid, video_frame = video_cap.read()
                                # If video ends, loop back to beginning
                                if not ret_vid:
                                    video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                                    ret_vid, video_frame = video_cap.read()
                                
                                if ret_vid:
                                    frame = overlay_image(frame, homography, video_frame)
                            
                            # Draw reference image border
                            h, w = reference_image.shape
                            corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
                            corners_transformed = cv2.perspectiveTransform(corners, homography)
                            frame = cv2.polylines(frame, [np.int32(corners_transformed)], True, (0, 255, 0), 2)
                        
                        except Exception as e:
                            status_text.text(f"Error in rendering: {str(e)}")
            
            # Convert frame to RGB for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Handle capture request
            if st.session_state.capture_requested:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pil_img = Image.fromarray(frame_rgb)
                st.session_state.captured_images.append((pil_img, timestamp))
                st.session_state.capture_requested = False
                
                # Save captured image
                if not os.path.exists("captures"):
                    os.makedirs("captures")
                image_path = os.path.join("captures", f"ar_capture_{timestamp}.jpg")
                pil_img.save(image_path)
                
                # Show capture confirmation
                status_text.success(f"Image captured successfully!")
            
            # Display the frame
            camera_placeholder.image(frame_rgb, channels="RGB", caption="AR Camera Feed", use_column_width=True)
        
        # Clean up resources
        cap.release()
        if video_cap is not None:
            video_cap.release()
        cv2.destroyAllWindows()
        camera_placeholder.empty()
        status_text.empty()
    
    # Display camera feed if active
    st.markdown('<div class="card view-container">', unsafe_allow_html=True)
    
    if st.session_state.camera_active:
        st.subheader("📷 AR View")
        run_ar_camera()
    else:
        st.subheader("AR Camera Feed")
        st.info("Press 'Start Camera' in the control panel to begin the AR experience.")
        
        # Display example image of how to use
        example_image_path = os.path.join("reference_images", "example.jpg") 
        if os.path.exists(example_image_path):
            st.image(example_image_path, caption="Example: Show your wedding card to the camera", use_column_width=True)
        else:
            st.markdown("""
            1. Select a reference image (your wedding card design)
            2. Choose what to display (3D model, image, or video)
            3. Click 'Start Camera' to begin
            4. Show your wedding card to the camera
            5. Capture magical AR moments with the 'Capture' button
            """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gallery of captured images
    if st.session_state.captured_images:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📸 Captured Moments")
        
        # Create columns for gallery
        gallery_cols = st.columns(3)
        for i, (img, timestamp) in enumerate(st.session_state.captured_images):
            with gallery_cols[i % 3]:
                st.image(img, caption=f"Captured: {timestamp}", use_column_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    # Download button
                    buf = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    img.save(buf, format="JPEG")
                    buf.close()
                    with open(buf.name, "rb") as file:
                        btn = st.download_button(
                            label="Download",
                            data=file,
                            file_name=f"ar_wedding_{timestamp}.jpg",
                            mime="image/jpeg",
                            key=f"download_{i}"
                        )
                
                with col2:
                    # Delete button
                    if st.button("Delete", key=f"delete_{i}"):
                        st.session_state.captured_images.pop(i)
                        st.experimental_rerun()
        
        # Clear all button
        if st.button("Clear All Images", key="clear_gallery"):
            st.session_state.captured_images = []
            st.experimental_rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 30px; padding: 10px; color: #6C757D; font-size: 0.8rem;">
    AR Wedding Card Experience | Create unforgettable memories
</div>
""", unsafe_allow_html=True)

# Clean up temp files when app is closed
def cleanup_temp_files():
    for file_path in st.session_state.temp_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except:
            pass

# Register cleanup function
import atexit
atexit.register(cleanup_temp_files)