import numpy as np
import cv2 as cv
import glob

# Straightens an image given camera calibration parameters.

target_name = input("Type name of target file: ")

target_laptop =	"C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal_op\\{}".format(target_name) # Picture to straighten
target_jetson =	"/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/cal/{}".format(target_name)

jetson_DIM =	"/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/cal/op/DIM.npy"
jetson_K =	    "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/cal/op/K.npy"
jetson_D =	    "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/cal/op/D.npy"
# ----------------------- Jetson Directory v. Laptop directory------------------------
laptop_DIM =    "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal_op\\op_webcam\\DIM.npy"
laptop_K =      "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal_op\\op_webcam\\K.npy"
laptop_D =      "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal_op\\op_webcam\\D.npy"
# Get params
DIM = np.load(laptop_DIM)
K = np.load(laptop_K)
D = np.load(laptop_D)

img = cv.imread(target_laptop)
h,w = img.shape[:2]

# See https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-part-2-13990f1b157f

balance = 1 # Set to 1 to show black space. Set to 0 to crop
new_K = cv.fisheye.estimateNewCameraMatrixForUndistortRectify(K, D, DIM, np.eye(3), balance=balance) # Need this step if we don't want to crop

map1, map2 = cv.fisheye.initUndistortRectifyMap(K, D, np.eye(3), new_K, DIM, cv.CV_16SC2)
undistorted_img = cv.remap(img, map1, map2, interpolation=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT)

# Show image
cv.imshow("undistorted", undistorted_img)
cv.waitKey(0)
cv.destroyAllWindows()

op_file_name = input("Type output file name: ")

cv.imwrite('C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\rectified_img\\{}'.format(op_file_name), undistorted_img) # Save it
