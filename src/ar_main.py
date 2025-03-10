import cv2
import numpy as np
import math
import os
from objloader_simple import OBJ

MIN_MATCHES = 10  

def render(frame, obj, projection, model):
    """Renders 3D object onto the frame using homography projection."""
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
