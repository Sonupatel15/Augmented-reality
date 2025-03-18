import streamlit as st
from app.ar_logic import run_ar_camera
from app.file_utils import handle_file_upload, save_captured_image
from app.config import ASSETS_PATH, REFERENCE_IMAGES_PATH

# Custom CSS for styling
def inject_custom_css():
    st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; color: #FF4B8B; margin-bottom: 0.5rem; text-align: center; }
        .sub-header { font-size: 1.2rem; color: #6C757D; margin-bottom: 2rem; text-align: center; }
        .card { background-color: #f8f9fa; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        .stButton>button { background-color: #FF4B8B; color: white; font-weight: bold; padding: 0.5rem 1rem; border-radius: 5px; width: 100%; }
        .stButton>button:hover { background-color: #E3407C; }
        .capture-btn { background-color: #20C997; }
        .view-container { border: 2px solid #ddd; border-radius: 10px; padding: 10px; background-color: #f0f0f0; }
        .gallery-image { border-radius: 5px; margin: 5px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# Render the main UI
def render_ui():
    # Inject custom CSS
    inject_custom_css()

    # App header
    st.markdown('<h1 class="main-header">AR Wedding Card Experience</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Create magical wedding memories with augmented reality</p>', unsafe_allow_html=True)

    # Initialize session state
    if 'camera_active' not in st.session_state:
        st.session_state.camera_active = False
    if 'captured_images' not in st.session_state:
        st.session_state.captured_images = []

    # Create layout with two columns (sidebar and main content)
    col1, col2 = st.columns([1, 3])

    # Sidebar with controls
    with col1:
        render_sidebar()

    # Main content area with camera feed and gallery
    with col2:
        render_main_content()

# Render sidebar controls
def render_sidebar():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📱 Control Panel")

    # Overlay selection
    overlay_type = st.selectbox("What would you like to display?", ["3D", "IMAGE", "VIDEO"], key="overlay_selector")
    st.session_state.overlay_type = overlay_type

    # Reference image selection
    st.markdown("### Reference Image")
    reference_path = handle_file_upload("Upload wedding card", REFERENCE_IMAGES_PATH, ["jpg", "jpeg", "png"])
    if reference_path:
        st.session_state.reference_path = reference_path

    # Conditional options based on overlay type
    if overlay_type == "3D":
        st.markdown("### 3D Model Selection")
        model_path = handle_file_upload("Upload 3D model", "models", ["obj"])
        if model_path:
            st.session_state.model_path = model_path

    elif overlay_type == "IMAGE":
        st.markdown("### Image Overlay")
        image_path = handle_file_upload("Upload image overlay", ASSETS_PATH, ["jpg", "jpeg", "png"])
        if image_path:
            st.session_state.image_path = image_path

    elif overlay_type == "VIDEO":
        st.markdown("### Video Overlay")
        video_path = handle_file_upload("Upload video overlay", ASSETS_PATH, ["mp4", "mov", "avi"])
        if video_path:
            st.session_state.video_path = video_path

    # Camera control
    st.markdown("### Camera Control")
    camera_button_label = "Stop Camera" if st.session_state.camera_active else "Start Camera"
    if st.button(camera_button_label, key="camera_toggle"):
        st.session_state.camera_active = not st.session_state.camera_active

    st.markdown('</div>', unsafe_allow_html=True)

# Render main content
def render_main_content():
    st.markdown('<div class="card view-container">', unsafe_allow_html=True)

    if st.session_state.camera_active:
        st.subheader("📷 AR View")
        run_ar_camera()
    else:
        st.subheader("AR Camera Feed")
        st.info("Press 'Start Camera' in the control panel to begin the AR experience.")

    st.markdown('</div>', unsafe_allow_html=True)

    # Gallery of captured images
    if st.session_state.captured_images:
        render_gallery()

# Render gallery of captured images
def render_gallery():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📸 Captured Moments")

    # Create columns for gallery
    gallery_cols = st.columns(3)
    for i, (img, timestamp) in enumerate(st.session_state.captured_images):
        with gallery_cols[i % 3]:
            st.image(img, caption=f"Captured: {timestamp}", use_column_width=True)

            # Download and delete buttons
            col1, col2 = st.columns(2)
            with col1:
                save_captured_image(img, timestamp)
            with col2:
                if st.button("Delete", key=f"delete_{i}"):
                    st.session_state.captured_images.pop(i)
                    st.experimental_rerun()

    # Clear all button
    if st.button("Clear All Images", key="clear_gallery"):
        st.session_state.captured_images = []
        st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)