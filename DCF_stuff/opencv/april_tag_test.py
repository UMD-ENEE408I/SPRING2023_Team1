import cv2
# The original code used the default apriltag library. Since we're using the pupil
# variant, importing as apriltag means we dont have to go through and change each
# call to the apriltag library -DCF
import pupil_apriltags as apriltag

LINE_LENGTH = 5
CENTER_COLOR = (0, 255, 0)
CORNER_COLOR = (255, 0, 255)

# Some utility functions to simplify drawing on the camera feed

# This function is used to draw a crosshair
# Sig: (cam.read() result, float[1], RGB color)


def plotPoint(image, center, color):
    # parse center elements as integers
    center = (int(center[0]), int(center[1]))
    # cv2.line(image, start_point, end_point, color, thickness)
    image = cv2.line(image,
                     (center[0] - LINE_LENGTH, center[1]),
                     (center[0] + LINE_LENGTH, center[1]),
                     color,
                     3)
    image = cv2.line(image,
                     (center[0], center[1] - LINE_LENGTH),
                     (center[0], center[1] + LINE_LENGTH),
                     color,
                     3)
    return image

# plot a little text


def plotText(image, center, color, text):
    # Write test to the right by a little
    center = (int(center[0]) + 4, int(center[1]) - 4)
    # cv2.putText(image, text, coords desired, font, fontScale, color, thickness)
    return cv2.putText(image, str(text), center, cv2.FONT_HERSHEY_SIMPLEX,
                       1, color, 3)


# setup and the main loop
# This line makes a new 'Detector' object and sets any parameters we want -DCF
# families='tag36h11' by default
detector = apriltag.Detector()

# Open the cam
cam = cv2.VideoCapture(0)

# ??? just say while true dude -DCF
looping = True

while looping:
    # In essence, what this does is, every time this loop runs, take the current frame from
    # the camera and set it to both 'image' and 'result' -DCF
    result, image = cam.read()
    # Convert the image we took to grayscale -DCF
    grayimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Look for detections using the grayscale image that we used
    detections = detector.detect(grayimg)
    if not detections:
        print("Nothing")
    else:
        detect = detections
        # found some tags, report them and update the camera image
        # for detect in detections:
        print("tag_id: %s, center: %s" % (detect.tag_id, detect.center))
        image = plotPoint(image, detect.center, CENTER_COLOR)
        image = plotText(image, detect.center, CENTER_COLOR, detect.tag_id)
        for corner in detect.corners:
            image = plotPoint(image, corner, CORNER_COLOR)
# refresh the camera image
    cv2.imshow('Result', image)
# let the system event loop do its thing
    key = cv2.waitKey(100)
# terminate the loop if the 'Return' key his hit
    if key == 13:
        looping = False

# loop over; clean up and dump the last updated frame for convenience of debugging
cv2.destroyAllWindows()
cv2.imwrite("final.png", image)
