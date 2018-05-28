import cv2
import matplotlib.pyplot as plt
import numpy as np
import pickle

def corners_unwarp(img_undistort, pts, mtx, dist):
    # Pass in your image into this function
    # Write code to do the following steps
    img_gray = cv2.cvtColor(img_undistort, cv2.COLOR_BGR2GRAY)
    # a-b) Find the source points (given as input)
    src = pts
    # c) define 4 destination points dst = np.float32([[,],[,],[,],[,]])
    dst = np.float32([[320,720], [320,0], [960, 0], [960,720]])
    # d) use cv2.getPerspectiveTransform() to get M, the transform matrix
    M = cv2.getPerspectiveTransform(src, dst) # src, dst are arrays of points
    Minv = cv2.getPerspectiveTransform(dst, src)
    # e) use cv2.warpPerspective() to warp your image to a top-down view
    img_size = img_gray.shape[::-1]
    warped = cv2.warpPerspective(img_undistort, M, img_size, flags=cv2.INTER_LINEAR)

    return warped, M, Minv

def pipeline_transform(img):
    src_pts = np.float32([[206, 720], [581, 460], [702, 460], [1107, 720]])
    camera_values = pickle.load(open('camera_values.p', 'rb'))
    mtx, dist = camera_values['mtx'], camera_values['dist']
    # Undistort image
    img_undistort = cv2.undistort ( img, mtx, dist, None, mtx)
    warped, M, Minv = corners_unwarp(img_undistort, src_pts, mtx, dist)
    return img_undistort, warped, M, Minv