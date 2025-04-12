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


## Output Screenshots

### For 3D Model:

**When reference image is found:**

![3D Model Found](https://github.com/user-attachments/assets/f00bff1e-ee5a-47c4-9c59-903f297dbafa)

**When reference image is not found:**

![3D Model Not Found](https://github.com/user-attachments/assets/b4766c2c-1628-4368-bd83-96159992e2ee)

### For Image Mode:

**When reference image is found:**

![Image Overlay Found](https://github.com/user-attachments/assets/470be2ae-ce6a-4a87-8d41-395efe642e29)

**When reference image is not found:**

![Image Overlay Not Found](https://github.com/user-attachments/assets/735e632f-07cc-4809-9272-4896b7fe9b4e)

### For Video Mode:

**When reference image is found:**

![Video Overlay Found](https://github.com/user-attachments/assets/3701faf6-e6dc-4577-9dd6-39f58af34561)

**When reference image is not found:**

![Video Overlay Not Found](https://github.com/user-attachments/assets/f2a06bf7-34de-4439-b9b1-4a0c7ca78480)












