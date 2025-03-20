import cv2
import numpy as np
import math
from ar_core.feature_detector import detect_and_match_features
from overlay_modules.object_loader import OBJ
from utils.projection import projection_matrix
from overlay_modules.image_overlay import overlay_image
from overlay_modules.video_overlay import overlay_video_on_frame # Add this line

def render(frame, obj, projection, model):
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

def process_frame(frame, reference_image, camera_params, obj, overlay_image_content, video_capture, overlay_type, min_matches):
    homography = detect_and_match_features(frame, reference_image, min_matches)
    if homography is not None:
        projection = projection_matrix(camera_params, homography)
        if overlay_type == "3D":
            frame = render(frame, obj, projection, reference_image)
        elif overlay_type == "IMAGE" and overlay_image_content is not None:
            frame = overlay_image(frame, homography, overlay_image_content)
        elif overlay_type == "VIDEO" and video_capture is not None:
            ret_video, video_frame = video_capture.read()
            if not ret_video:
                video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_video, video_frame = video_capture.read()
            if ret_video:
                # Warp the video frame using homography
                h, w = reference_image.shape
                corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
                corners_transformed = cv2.perspectiveTransform(corners, homography)
                matrix = cv2.getPerspectiveTransform(corners, corners_transformed)
                warped_video = cv2.warpPerspective(video_frame, matrix, (frame.shape[1], frame.shape[0]))

                # Ensure target_shape has 3 dimensions
                target_shape = (reference_image.shape[0], reference_image.shape[1], 3)

                frame = overlay_video_on_frame(frame, warped_video, homography, target_shape)
        h, w = reference_image.shape
        corners = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
        corners_transformed = cv2.perspectiveTransform(corners, homography)
        frame = cv2.polylines(frame, [np.int32(corners_transformed)], True, (0, 255, 0), 2)
    return frame