import cv2
import os
cam = cv2.VideoCapture(0)

cv2.namedWindow("test")

img_counter = 0

# Change directory to a folder that will contain the chessboard pics
dir = r"/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/cam_cal"
os.chdir(dir)

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("test", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1

cam.release()

cv2.destroyAllWindows()
