import cv2
import numpy as np

def overlay_video_on_frame(img_webcam, img_warp, homography, target_shape):
    h, w, _ = target_shape
    corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
    corners_transformed = cv2.perspectiveTransform(corners, homography).astype(np.int32)

    mask = np.zeros(img_webcam.shape[:2], dtype=np.uint8)
    cv2.fillConvexPoly(mask, corners_transformed, 255)

    masked_img_warp = cv2.bitwise_and(img_warp, img_warp, mask=mask)
    masked_img_webcam = cv2.bitwise_and(img_webcam, img_webcam, mask=cv2.bitwise_not(mask))

    result = cv2.add(masked_img_webcam, masked_img_warp)
    return result