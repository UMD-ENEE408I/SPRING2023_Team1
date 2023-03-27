import numpy as np
import cv2 as cv
import glob

# Hello there
# Outputs camera calibration parameters from photos.

name = "" # Pictures to process

# Get corners from pictures of checkerboard

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 50, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,6,0)
objp = np.zeros((9*6,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.


jetson = '/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/cal/raw/set3/'
laptop = 'C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal\\raw\\set_webcam\\'
images = glob.glob(laptop + '*.png')



_img_shape = None

i = 0 # Iteration number
#global gray

for fname in images:
    img = cv.imread(fname)

    if _img_shape == None:
        _img_shape = img.shape[:2]


    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
 

    # Find the chess board corners
    par = cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_NORMALIZE_IMAGE
    ret, corners = cv.findChessboardCorners(gray, (9,6), par)
    # If found, add object points, image points (after refining them)

    # Print iteration number
    
    print("Image", i, end=" ")
    i = i + 1
    if ret == True:
        print("(SUCCESS!)") # Indicate if that picture was processed successfully

        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (9,6), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)

    else:
        print("(FAILED)") # Indicate failure
cv.destroyAllWindows()

# Calibrate camera
# See https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-333b05afa0b0

calibration_flags = cv.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv.fisheye.CALIB_FIX_SKEW

N_OK = len(objpoints)
K = np.zeros((3, 3))
D = np.zeros((4, 1)) # Look up docs for fisheye_calibrate models
rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
rms, _, _, _, _ = \
    cv.fisheye.calibrate(
        np.expand_dims(np.asarray(objpoints), -2),
        imgpoints,
        gray.shape[::-1],
        K,
        D,
        rvecs,
        tvecs,
        calibration_flags,
        (cv.TERM_CRITERIA_EPS+cv.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
    )
print("Found " + str(N_OK) + " valid images for calibration.")
DIM = _img_shape[::-1]
K = K.tolist()
print("K array: ")
print(K)
# PRINT THIS OUT!! -DCF
D = D.tolist()

# Save outputs to files

jetson_DIM = "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/op/DIM"
jetson_K = "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/op/K"
jetson_D = "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/op/D"
# ----------------------- Jetson Directory v. Laptop directory------------------------
laptop_DIM =    "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal\\op_webcam\\DIM.npy"
laptop_K =      "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal\\op_webcam\\K.npy"
laptop_D =      "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal\\op_webcam\\D.npy"

np.save(laptop_DIM, DIM)
np.save(laptop_K, K)
np.save(laptop_D, D)
