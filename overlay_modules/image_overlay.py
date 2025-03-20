import cv2
import numpy as np

def overlay_image(frame, homography, overlay):
    h, w, _ = overlay.shape
    corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
    transformed_corners = cv2.perspectiveTransform(corners, homography)
    matrix = cv2.getPerspectiveTransform(np.float32(corners), np.float32(transformed_corners))
    warped = cv2.warpPerspective(overlay, matrix, (frame.shape[1], frame.shape[0]))
    mask = np.zeros_like(frame, dtype=np.uint8)
    cv2.fillPoly(mask, [np.int32(transformed_corners)], (255, 255, 255))
    frame = cv2.bitwise_and(frame, cv2.bitwise_not(mask))
    frame = cv2.add(frame, warped)
    return frame