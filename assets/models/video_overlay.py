# import cv2
# import numpy as np

# def warp_video_to_target(video_frame, matrix, frame_shape):
#     """
#     Warps the video frame using the given homography matrix.
    
#     :param video_frame: The frame from the video to overlay.
#     :param matrix: The homography matrix.
#     :param frame_shape: Shape of the target frame (height, width).
#     :return: Warped video frame.
#     """
#     return cv2.warpPerspective(video_frame, matrix, (frame_shape[1], frame_shape[0]))

# def overlay_video_on_frame(img_webcam, img_aug, img_warp, dst):
#     """
#     Overlays the warped video onto the detected target area in the webcam frame.
    
#     :param img_webcam: The original webcam frame.
#     :param img_aug: The augmented frame.
#     :param img_warp: The warped video frame.
#     :param dst: The transformed points of the detected target.
#     :return: Final augmented frame with the video overlay.
#     """
#     mask_new = np.zeros((img_webcam.shape[0], img_webcam.shape[1]), np.uint8)
#     cv2.fillPoly(mask_new, [np.int32(dst)], (255, 255, 255))
#     mask_inv = cv2.bitwise_not(mask_new)

#     # Black out the target area in the original frame
#     img_aug = cv2.bitwise_and(img_aug, img_aug, mask=mask_inv)
#     # Overlay the warped video
#     img_aug = cv2.bitwise_or(img_warp, img_aug)

#     return img_aug


# import cv2
# import numpy as np

# def warp_video_to_target(video_frame, matrix, frame_shape):
#     """
#     Warps the video frame using the given homography matrix.
    
#     :param video_frame: The frame from the video to overlay.
#     :param matrix: The homography matrix.
#     :param frame_shape: Shape of the target frame (height, width).
#     :return: Warped video frame.
#     """
#     if matrix is None:
#         print("Error: Homography matrix is None!")
#         return np.zeros((frame_shape[0], frame_shape[1], 3), dtype=np.uint8)
    
#     return cv2.warpPerspective(video_frame, matrix, (frame_shape[1], frame_shape[0]))

# def overlay_video_on_frame(img_webcam, img_warp, dst):
#     """
#     Overlays the warped video onto the detected target area in the webcam frame.
    
#     :param img_webcam: The original webcam frame.
#     :param img_warp: The warped video frame.
#     :param dst: The transformed points of the detected target.
#     :return: Final augmented frame with the video overlay.
#     """
#     mask_new = np.zeros((img_webcam.shape[0], img_webcam.shape[1]), np.uint8)
#     cv2.fillPoly(mask_new, [np.int32(dst)], 255)
#     mask_inv = cv2.bitwise_not(mask_new)

#     # Remove the target area in the original frame
#     img_webcam_bg = cv2.bitwise_and(img_webcam, img_webcam, mask=mask_inv)

#     # Keep only the overlay area in the warped video
#     img_warp_fg = cv2.bitwise_and(img_warp, img_warp, mask=mask_new)

#     # Merge both images
#     result = cv2.add(img_webcam_bg, img_warp_fg)

#     return result

# def main():
#     cap_video = cv2.VideoCapture("./reference/refVideo.mp4")  # Load your video
#     cap_webcam = cv2.VideoCapture(0)  # Open webcam

#     while cap_webcam.isOpened():
#         ret_webcam, img_webcam = cap_webcam.read()
#         if not ret_webcam:
#             print("Error: Cannot read webcam frame!")
#             break

#         ret_video, video_frame = cap_video.read()
#         if not ret_video:
#             cap_video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video when it ends
#             continue

#         # Define your homography matrix `matrix` and destination points `dst` here
#         matrix = np.eye(3)  # Replace with actual computed homography
#         dst = np.array([[100, 100], [500, 100], [500, 400], [100, 400]])  # Replace with detected corners

#         frame_shape = (img_webcam.shape[0], img_webcam.shape[1])  # Target frame size
#         img_warp = warp_video_to_target(video_frame, matrix, frame_shape)

#         # Overlay video onto the target area
#         img_aug = overlay_video_on_frame(img_webcam, img_warp, dst)

#         cv2.imshow("Augmented Reality", img_aug)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap_webcam.release()
#     cap_video.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()

import cv2
import numpy as np

def warp_video_to_target(video_frame, matrix, frame_shape):
    """
    Warps the video frame using the given homography matrix.
    
    :param video_frame: The frame from the video to overlay.
    :param matrix: The homography matrix.
    :param frame_shape: Shape of the target frame (height, width).
    :return: Warped video frame.
    """
    if matrix is None or matrix.shape != (3, 3):
        print("Error: Invalid homography matrix!")
        return np.zeros((frame_shape[0], frame_shape[1], 3), dtype=np.uint8)

    return cv2.warpPerspective(video_frame, matrix, (frame_shape[1], frame_shape[0]))

def overlay_video_on_frame(img_webcam, img_warp, dst):
    """
    Overlays the warped video onto the detected target area in the webcam frame.
    
    :param img_webcam: The original webcam frame.
    :param img_warp: The warped video frame.
    :param dst: The transformed points of the detected target.
    :return: Final augmented frame with the video overlay.
    """
    mask_new = np.zeros((img_webcam.shape[0], img_webcam.shape[1]), np.uint8)
    cv2.fillPoly(mask_new, [np.int32(dst)], 255)
    mask_inv = cv2.bitwise_not(mask_new)

    # Remove the target area in the original frame
    img_webcam_bg = cv2.bitwise_and(img_webcam, img_webcam, mask=mask_inv)

    # Keep only the overlay area in the warped video
    img_warp_fg = cv2.bitwise_and(img_warp, img_warp, mask=mask_new)

    # Merge both images
    result = cv2.add(img_webcam_bg, img_warp_fg)

    return result

def main():
    cap_video = cv2.VideoCapture("video.mp4")  # Load the video
    cap_webcam = cv2.VideoCapture(0)  # Open webcam

    # Ensure video properties
    video_fps = int(cap_video.get(cv2.CAP_PROP_FPS))
    video_width = int(cap_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Debugging print
    print(f"Video FPS: {video_fps}, Width: {video_width}, Height: {video_height}")

    while cap_webcam.isOpened():
        ret_webcam, img_webcam = cap_webcam.read()
        if not ret_webcam:
            print("Error: Cannot read webcam frame!")
            break

        ret_video, video_frame = cap_video.read()
        if not ret_video:
            cap_video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video when it ends
            continue

        # TODO: Replace with actual homography detection logic
        matrix = np.eye(3)  # Temporary placeholder
        dst = np.array([[100, 100], [500, 100], [500, 400], [100, 400]])  # Placeholder points

        frame_shape = (img_webcam.shape[0], img_webcam.shape[1])  # Target frame size
        img_warp = warp_video_to_target(video_frame, matrix, frame_shape)

        # Overlay video onto the target area
        img_aug = overlay_video_on_frame(img_webcam, img_warp, dst)

        cv2.imshow("Augmented Reality", img_aug)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap_webcam.release()
    cap_video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()