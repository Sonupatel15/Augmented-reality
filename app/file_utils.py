import os
import tempfile
from PIL import Image

def handle_file_upload(label, save_dir, allowed_types):
    uploaded_file = st.file_uploader(label, type=allowed_types)
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, dir=save_dir, suffix=f".{allowed_types[0]}") as tmp_file:
            tmp_file.write(uploaded_file.read())
            return tmp_file.name
    return None

def save_captured_image(image, timestamp):
    if not os.path.exists("captures"):
        os.makedirs("captures")
    image_path = os.path.join("captures", f"ar_capture_{timestamp}.jpg")
    image.save(image_path)

def cleanup_temp_files():
    for file_path in st.session_state.temp_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except:
            pass