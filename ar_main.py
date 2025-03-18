# import cv2
# import numpy as np
# import math
# import os
# from objloader_simple import OBJ

# # Constants
# MIN_MATCHES = 10
# REFERENCE_IMAGE_PATH = 'reference/rich.jpg'  # Path to your reference image
# MODEL_PATH = 'models/rat.obj'  # Default 3D model path
# IMAGE_PATH = 'media/rich.jpg'  # Default image path
# VIDEO_PATH = 'media/sample_video.mp4'  # Default video path

# def render(frame, obj, projection, model, texture=None):
#     """Renders a 3D object onto the frame using homography projection."""
#     vertices = obj.vertices
#     scale_matrix = np.eye(3) * 3
#     h, w = model.shape

#     for face in obj.faces:
#         face_vertices = face[0]
#         points = np.array([vertices[vertex - 1] for vertex in face_vertices])
#         points = np.dot(points, scale_matrix)
#         points = np.array([[p[0] + w / 2, p[1] + h / 2, p[2]] for p in points])
        
#         dst = cv2.perspectiveTransform(points.reshape(-1, 1, 3), projection)
#         imgpts = np.int32(dst)

#         cv2.fillConvexPoly(frame, imgpts, (137, 27, 211))

#     return frame

# def projection_matrix(camera_matrix, homography):
#     """Computes the 3D projection matrix from the homography."""
#     homography *= -1
#     rt_matrix = np.dot(np.linalg.inv(camera_matrix), homography)

#     col_1, col_2, col_3 = rt_matrix[:, 0], rt_matrix[:, 1], rt_matrix[:, 2]
#     scale_factor = math.sqrt(np.linalg.norm(col_1, 2) * np.linalg.norm(col_2, 2))

#     rot_1, rot_2 = col_1 / scale_factor, col_2 / scale_factor
#     translation = col_3 / scale_factor

#     c, p = rot_1 + rot_2, np.cross(rot_1, rot_2)
#     d = np.cross(c, p)

#     rot_1 = (c / np.linalg.norm(c, 2) + d / np.linalg.norm(d, 2)) / math.sqrt(2)
#     rot_2 = (c / np.linalg.norm(c, 2) - d / np.linalg.norm(d, 2)) / math.sqrt(2)
#     rot_3 = np.cross(rot_1, rot_2)

#     projection = np.stack((rot_1, rot_2, rot_3, translation)).T
#     return np.dot(camera_matrix, projection)

# def overlay_image(frame, homography, overlay):
#     """Overlays an image onto the frame using homography."""
#     h, w, _ = overlay.shape
#     corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
#     transformed_corners = cv2.perspectiveTransform(corners, homography)

#     matrix = cv2.getPerspectiveTransform(np.float32(corners), np.float32(transformed_corners))
#     warped = cv2.warpPerspective(overlay, matrix, (frame.shape[1], frame.shape[0]))

#     mask = np.zeros_like(frame, dtype=np.uint8)
#     cv2.fillPoly(mask, [np.int32(transformed_corners)], (255, 255, 255))
#     frame = cv2.bitwise_and(frame, cv2.bitwise_not(mask))
#     frame = cv2.add(frame, warped)
#     return frame

# def main(selected_type="3D"):  # selected_type can be "3D", "IMAGE", or "VIDEO"
#     cap = cv2.VideoCapture(0)
#     reference_image = cv2.imread(REFERENCE_IMAGE_PATH, 0)
    
#     if selected_type == "3D":
#         obj = OBJ(MODEL_PATH, swapyz=True)
#     elif selected_type == "IMAGE":
#         overlay = cv2.imread(IMAGE_PATH)
#     elif selected_type == "VIDEO":
#         video_cap = cv2.VideoCapture(VIDEO_PATH)

#     orb = cv2.ORB_create(nfeatures=5000)
#     bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
#     kp_model, des_model = orb.detectAndCompute(reference_image, None)
#     camera_params = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]])

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Failed to grab frame")
#             break

#         gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         kp_frame, des_frame = orb.detectAndCompute(gray_frame, None)

#         if des_frame is not None and len(des_frame) > 0:
#             matches = bf.match(des_model, des_frame)
#             matches = sorted(matches, key=lambda x: x.distance)

#             if len(matches) > MIN_MATCHES:
#                 src_pts = np.float32([kp_model[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
#                 dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                
#                 homography, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

#                 if homography is not None:
#                     projection = projection_matrix(camera_params, homography)

#                     if selected_type == "3D":
#                         frame = render(frame, obj, projection, reference_image)
#                     elif selected_type == "IMAGE":
#                         frame = overlay_image(frame, homography, overlay)
#                     elif selected_type == "VIDEO":
#                         ret_video, video_frame = video_cap.read()
#                         if ret_video:
#                             frame = overlay_image(frame, homography, video_frame)

#                     h, w = reference_image.shape
#                     corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
#                     corners_transformed = cv2.perspectiveTransform(corners, homography)
#                     frame = cv2.polylines(frame, [np.int32(corners_transformed)], True, (0, 255, 0), 2)

#         cv2.imshow('AR Wedding Card', frame)
#         if cv2.waitKey(1) == 27:
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     if selected_type == "VIDEO":
#         video_cap.release()

# if __name__ == "__main__":
#     main("3D")  # Change to "IMAGE" or "VIDEO" based on frontend selection

import cv2
import numpy as np
import math
import os
from objloader_simple import OBJ
from utils import overlay_image  # Import overlay function from utils.py

# Constants
MIN_MATCHES = 10
REFERENCE_IMAGE_PATH = 'reference/rich.jpg'  # Path to reference image
MODEL_PATH = 'models/rat.obj'  # 3D model path
IMAGE_PATH = 'reference/cult.jpg'  # Image overlay path
VIDEO_PATH = 'media/sample_video.mp4'  # Video overlay path

def render(frame, obj, projection, model):
    """Renders a 3D object onto the frame using homography projection."""
    vertices = obj.vertices
    scale_matrix = np.eye(3) * 3
    h, w = model.shape

    for face in obj.faces:
        face_vertices = face[0]
        points = np.array([vertices[vertex - 1] for vertex in face_vertices])
        points = np.dot(points, scale_matrix)
        points = np.array([[p[0] + w / 2, p[1] + h / 2, p[2]] for p in points])
        
        dst = cv2.perspectiveTransform(points.reshape(-1, 1, 3), projection)
        imgpts = np.int32(dst)

        cv2.fillConvexPoly(frame, imgpts, (137, 27, 211))

    return frame

def projection_matrix(camera_matrix, homography):
    """Computes the 3D projection matrix from the homography."""
    homography *= -1
    rt_matrix = np.dot(np.linalg.inv(camera_matrix), homography)

    col_1, col_2, col_3 = rt_matrix[:, 0], rt_matrix[:, 1], rt_matrix[:, 2]
    scale_factor = math.sqrt(np.linalg.norm(col_1, 2) * np.linalg.norm(col_2, 2))

    rot_1, rot_2 = col_1 / scale_factor, col_2 / scale_factor
    translation = col_3 / scale_factor

    c, p = rot_1 + rot_2, np.cross(rot_1, rot_2)
    d = np.cross(c, p)

    rot_1 = (c / np.linalg.norm(c, 2) + d / np.linalg.norm(d, 2)) / math.sqrt(2)
    rot_2 = (c / np.linalg.norm(c, 2) - d / np.linalg.norm(d, 2)) / math.sqrt(2)
    rot_3 = np.cross(rot_1, rot_2)

    projection = np.stack((rot_1, rot_2, rot_3, translation)).T
    return np.dot(camera_matrix, projection)

def main(selected_type="3D"):  # Can be "3D", "IMAGE", or "VIDEO"
    cap = cv2.VideoCapture(0)
    reference_image = cv2.imread(REFERENCE_IMAGE_PATH, 0)
    
    if selected_type == "3D":
        obj = OBJ(MODEL_PATH, swapyz=True)
    elif selected_type == "IMAGE":
        overlay = cv2.imread(IMAGE_PATH)
    elif selected_type == "VIDEO":
        video_cap = cv2.VideoCapture(VIDEO_PATH)

    orb = cv2.ORB_create(nfeatures=5000)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    kp_model, des_model = orb.detectAndCompute(reference_image, None)
    camera_params = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]])

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp_frame, des_frame = orb.detectAndCompute(gray_frame, None)

        if des_frame is not None and len(des_frame) > 0:
            matches = bf.match(des_model, des_frame)
            matches = sorted(matches, key=lambda x: x.distance)

            if len(matches) > MIN_MATCHES:
                src_pts = np.float32([kp_model[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
                
                homography, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                if homography is not None:
                    projection = projection_matrix(camera_params, homography)

                    if selected_type == "3D":
                        frame = render(frame, obj, projection, reference_image)
                    elif selected_type == "IMAGE":
                        frame = overlay_image(frame, homography, overlay)  # Using function from utils.py
                    elif selected_type == "VIDEO":
                        ret_video, video_frame = video_cap.read()
                        if ret_video:
                            frame = overlay_image(frame, homography, video_frame)  # Using function from utils.py

                    h, w = reference_image.shape
                    corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
                    corners_transformed = cv2.perspectiveTransform(corners, homography)
                    frame = cv2.polylines(frame, [np.int32(corners_transformed)], True, (0, 255, 0), 2)

        cv2.imshow('AR Wedding Card', frame)
        if cv2.waitKey(1) == 27:  # Press ESC to exit
            break

    cap.release()
    cv2.destroyAllWindows()
    if selected_type == "VIDEO":
        video_cap.release()

if __name__ == "__main__":
    main("3D")  # Change to "IMAGE" or "VIDEO" based on frontend selection