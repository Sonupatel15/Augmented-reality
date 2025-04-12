# AR Experience

AR Overlay Model is a real-time augmented reality system that dynamically projects 3D objects, images, or videos onto reference images captured by a camera. Using ORB feature detection and homography estimation, it accurately tracks the reference image in live video feeds and renders overlays with precise perspective alignment. The model supports OBJ files for 3D objects, image files (JPG/PNG), and video files (MP4/AVI), which are transformed using perspective warping to match the reference image's orientation and scale in real-time. This markerless solution performs all processing client-side with OpenCV and Streamlit, enabling instant AR visualization without requiring physical markers or specialized hardware.

## Contributors

* [@Sonupatel](https://github.com/Sonupatel15)
* [@Harsha](https://github.com/harsha188-codes)

## Setup

1.  Install dependencies: `pip install -r requirements.txt`
2.  Run the Streamlit app: `streamlit run streamlit_app.py`

## Usage

Follow the instructions in the Streamlit app to upload reference images, 3D models, overlay images, and videos.

## Directory Structure

- `ar_core`: Core AR functionality.
- `overlay_modules`: Modules for overlaying content (3D, images, videos).
- `utils`: Utility functions.
- `assets`: Assets like reference images, models, etc.
- `streamlit_app.py`: Streamlit frontend.

## Launch the Application
`streamlit run streamlit_app.py`
