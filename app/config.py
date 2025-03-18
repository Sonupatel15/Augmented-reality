import os

# Paths
ASSETS_PATH = os.path.join("assets")
REFERENCE_IMAGES_PATH = os.path.join(ASSETS_PATH, "reference_images")

# Camera parameters
CAMERA_PARAMS = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]])