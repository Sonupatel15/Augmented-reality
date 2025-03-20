import streamlit as st
import cv2
import numpy as np
import os
import tempfile
from PIL import Image
from datetime import datetime

# Import AR backend functionality
from ar_core.ar_main import process_frame
from ar_core.camera import initialize_camera
from overlay_modules.object_loader import OBJ
from utils.projection import projection_matrix

# Page configuration and styling (Classic UI)
st.set_page_config(
    page_title="AR Wedding Card Experience (Classic)",
    page_icon="💍",
    layout="wide"
)

st.title("AR Wedding Card Experience (Classic)")
st.write("Create magical wedding memories with augmented reality")

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

# Sidebar with controls (Classic UI)
st.sidebar.header("Control Panel")

# Overlay selection
st.sidebar.subheader("Overlay Type")
overlay_type = st.sidebar.selectbox("What would you like to display?",
                                    ["3D", "IMAGE", "VIDEO"],
                                    key="overlay_selector")
st.session_state.overlay_type = overlay_type

# Reference image selection
st.sidebar.subheader("Reference Image")
reference_options = ["Upload your own"]

if os.path.exists("assets/reference"):
    reference_files = [f for f in os.listdir("assets/reference")
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    reference_options.extend(reference_files)

reference_selection = st.sidebar.selectbox("Select wedding card reference",
                                           reference_options,
                                           index=0 if len(reference_options) > 0 else 0)

if reference_selection == "Upload your own":
    uploaded_reference = st.sidebar.file_uploader("Upload wedding card",
                                                  type=["jpg", "jpeg", "png"],
                                                  key="reference_uploader")
    if uploaded_reference is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_ref:
            tmp_ref.write(uploaded_reference.read())
            reference_path = tmp_ref.name
            st.session_state.temp_files.append(reference_path)
            st.session_state.reference_path = reference_path
            st.sidebar.image(reference_path, caption="Your reference image", width=150)
else:
    st.session_state.reference_path = os.path.join("assets/reference", reference_selection)
    try:
        st.sidebar.image(st.session_state.reference_path, caption="Reference Image", width=150)
    except:
        st.sidebar.error(f"Could not display reference image: {st.session_state.reference_path}")

if overlay_type == "3D":
    st.sidebar.subheader("3D Model Selection")
    model_options = ["Default (Fox)"]
    if os.path.exists("assets/models"):
        model_files = [f for f in os.listdir("assets/models") if f.lower().endswith('.obj')]
        model_options.extend(model_files)
    model_selection = st.sidebar.selectbox("Select 3D model", model_options)
    if model_selection == "Default (Fox)":
        st.session_state.model_path = "assets/models/fox.obj"
    else:
        st.session_state.model_path = os.path.join("assets/models", model_selection)

elif overlay_type == "IMAGE":
    st.sidebar.subheader("Image Overlay")
    uploaded_image = st.sidebar.file_uploader("Upload image overlay", type=["jpg", "jpeg", "png"])
    if uploaded_image is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_img:
            tmp_img.write(uploaded_image.read())
            image_path = tmp_img.name
            st.session_state.temp_files.append(image_path)
            st.session_state.image_path = image_path
            st.sidebar.image(image_path, caption="Your image overlay", width=150)

elif overlay_type == "VIDEO":
    st.sidebar.subheader("Video Overlay")
    uploaded_video = st.sidebar.file_uploader("Upload video overlay", type=["mp4", "mov", "avi"])
    if uploaded_video is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_vid:
            tmp_vid.write(uploaded_video.read())
            video_path = tmp_vid.name
            st.session_state.temp_files.append(video_path)
            st.session_state.video_path = video_path
            st.sidebar.video(video_path, start_time=0)

st.sidebar.subheader("Settings")
st.session_state.min_matches = st.sidebar.slider("Feature point matches", 5, 50, 10,
                                                 help="Minimum matches required for detection")

st.sidebar.subheader("Camera Control")
camera_button_label = "Stop Camera" if st.session_state.camera_active else "Start Camera"
if st.sidebar.button(camera_button_label, key="camera_toggle"):
    st.session_state.camera_active = not st.session_state.camera_active
    if not st.session_state.camera_active:
        st.rerun()

if st.session_state.camera_active:
    if st.sidebar.button("📸 Capture Moment", key="capture_btn"):
        st.session_state.capture_requested = True

# Main content area with camera feed and gallery (Classic UI)
def run_ar_camera():
    if not hasattr(st.session_state, 'reference_path'):
        st.error("Please select or upload a reference image")
        st.session_state.camera_active = False
        return

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

    camera_params = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]])

    obj = None
    if st.session_state.overlay_type == "3D":
        try:
            obj = OBJ(st.session_state.model_path, swapyz=True)
        except Exception as e:
            st.error(f"Error loading 3D model: {e}")
            st.session_state.camera_active = False
            return

    image_overlay = None
    if st.session_state.overlay_type == "IMAGE":
        try:
            image_overlay = cv2.imread(st.session_state.image_path)
        except:
            st.error("Failed to load image overlay")
            st.session_state.camera_active = False
            return

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

    cap = initialize_camera()
    if cap is None:
        return

    camera_placeholder = st.empty()
    status_text = st.empty()

    if 'capture_requested' not in st.session_state:
        st.session_state.capture_requested = False

    while st.session_state.camera_active:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to capture frame from camera")
            break

        try:
            frame = process_frame(frame, reference_image, camera_params, obj, image_overlay, video_cap, st.session_state.overlay_type, st.session_state.min_matches)
            if frame is None:
                status_text.text("Not enough matches")
                continue
        except Exception as e:
            status_text.text(f"Error in processing frame: {str(e)}")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if st.session_state.capture_requested:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pil_img = Image.fromarray(frame_rgb)
            st.session_state.captured_images.append((pil_img, timestamp))
            st.session_state.capture_requested = False

            if not os.path.exists("captures"):
                os.makedirs("captures")
            image_path = os.path.join("captures", f"ar_capture_{timestamp}.jpg")
            pil_img.save(image_path)

            status_text.success(f"Image captured successfully!")

        camera_placeholder.image(frame_rgb, channels="RGB", caption="AR Camera Feed", use_column_width=True)

    cap.release()
    if video_cap is not None:
        video_cap.release()
    cv2.destroyAllWindows()
    camera_placeholder.empty()
    status_text.empty()

if st.session_state.camera_active:
    st.subheader("📷 AR View")
    run_ar_camera()
else:
    st.subheader("AR Camera Feed")
    st.info("Press 'Start Camera' in the control panel to begin the AR experience.")
    example_image_path = os.path.join("assets/reference", "example.jpg")
    if os.path.exists(example_image_path):
        st.image(example_image_path, caption="Example: Show your wedding card to the camera", use_column_width=True)
    else:
        st.write("1. Select a reference image. 2. Choose what to display. 3. Start Camera. 4. Show card. 5. Capture.")

if st.session_state.captured_images:
    st.subheader("📸 Captured Moments")
    gallery_cols = st.columns(3)
    for i, (img, timestamp) in enumerate(st.session_state.captured_images):
        with gallery_cols[i % 3]:
            st.image(img, caption=f"Captured: {timestamp}", use_column_width=True)
            col1, col2 = st.columns(2)
            with col1:
                buf = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                img.save(buf, format="JPEG")
                buf.close()
                with open(buf.name, "rb") as file:
                    st.download_button("Download", file, f"ar_wedding_{timestamp}.jpg", "image/jpeg", key=f"download_{i}")
            with col2:
                if st.button("Delete", key=f"delete_{i}"):
                    st.session_state.captured_images.pop(i)
                    st.rerun()
    if st.button("Clear All Images", key="clear_gallery"):
        st.session_state.captured_images = []
        st.rerun()

st.markdown("""
<div style="text-align: center; margin-top: 30px; padding: 10px; color: #6C757D; font-size: 0.8rem;">
    AR Wedding Card Experience | Create unforgettable memories
</div>
""", unsafe_allow_html=True)

def cleanup_temp_files():
    for file_path in st.session_state.temp_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except:
            pass

import atexit
atexit.register(cleanup_temp_files)

def main():
    pass

if __name__ == "__main__":
    main()