import numpy as np
import math

def projection_matrix(camera_matrix, homography):
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