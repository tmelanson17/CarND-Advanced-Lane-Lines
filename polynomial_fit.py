import numpy as np
import cv2

ym_per_pix = 30/720 # meters per pixel in y dimension
xm_per_pix = 3.7/700 # meters per pixel in x dimension


def find_left_right_lane(img_topdown, img_size):
    bottom = img_topdown[img_size[1]//2:, :] / 255
    hist = np.sum(bottom, axis=0)
    n_cols = len(hist)
    left_lane = np.argmax(hist[:n_cols//2])
    right_lane = np.argmax(hist[n_cols//2:]) + n_cols//2
    return left_lane, right_lane
    
    
def find_lane_points(lane, img_rowed, h_window, v_window):
    initial_lane = lane
    curr_lane = lane

    lane_r = list()
    lane_c = list()

    for i in range(len(img_rowed)-1, -1, -1):
        rel_r_coords, c_coords = np.where(img_rowed[i])
        indices = np.where(np.abs(c_coords - curr_lane) < h_window / 2)
        lane_r.append(rel_r_coords[indices] + i*v_window)
        lane_c.append(c_coords[indices])

        if len(c_coords[indices]) > 0:
            curr_lane = np.mean(c_coords[indices])


    lane_r = np.concatenate(lane_r)
    lane_c = np.concatenate(lane_c)
    return lane_r, lane_c


def vehicle_center(left_fit, right_fit, img_size):
    base_row = img_size[1] - 1
    left_base = left_fit[0]*base_row**2 + left_fit[1]*base_row + left_fit[2]
    right_base = right_fit[0]*base_row**2 + right_fit[1]*base_row + right_fit[2]

    vehicle_center = img_size[0] / 2 # About 600
    lane_center = (left_base + right_base) / 2
    offset_pix = vehicle_center - lane_center
    return xm_per_pix * offset_pix


def lane_center(fit, img_size):
    base_row = img_size[1] - 1
    base_col = fit[0]*base_row**2 + fit[1]*base_row + fit[2]

    vehicle_center = img_size[0] / 2 # About 600
    offset_pix = base_col - vehicle_center
    return xm_per_pix * offset_pix

    
def pipeline_polyfit(img_topdown, img_size, n_windows=20, h_window=70):
    img_rowed = np.vsplit(img_topdown, n_windows)
    v_window = len(img_topdown) / n_windows
    
    left_lane, right_lane = find_left_right_lane(img_topdown, img_size)
    
    left_laney, left_lanex = find_lane_points(left_lane, img_rowed, h_window, v_window)
    right_laney, right_lanex = find_lane_points(right_lane, img_rowed, h_window, v_window)  

    left_fit = np.polyfit(left_laney, left_lanex, 2)
    right_fit = np.polyfit(right_laney, right_lanex, 2)
    
    return left_fit, right_fit

    
def lane_curvature(laney, lanex, height=720):
    ploty = np.linspace(0, height-1, num=height)# to cover same y-range as image
    ploty = ploty[::-1]
    y_eval = np.max(ploty)

    # Fit new polynomials to x,y in world space
    fit_cr = np.polyfit(laney*ym_per_pix, lanex*xm_per_pix, 2)
    # Calculate the new radii of curvature
    curverad = ((1 + (2*fit_cr[0]*y_eval*ym_per_pix + fit_cr[1])**2)**1.5) / np.absolute(2*fit_cr[0])
    # Now our radius of curvature is in meters
    return curverad


def extract_line(fit, ploty):
    fitx = fit[0]*ploty**2 + fit[1]*ploty + fit[2]
    return ploty, fitx
    