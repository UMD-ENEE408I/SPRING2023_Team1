from pupil_apriltags import Detector
import cv2
import numpy as np
import time
import os

# Questions for Levi:
#       How does find_pose_from_tag work?

at_detector = Detector(
    families="tag36h11",
    nthreads=1,
    quad_decimate=1.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
)

# Change directory to a folder that will contain the chessboard pics
laptop = "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\misc_img"
jetson = "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/misc_img"
dir = "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal\\"
# dir = r"C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv"
os.chdir(laptop)

# Straightening the camera feed

jetson_DIM = "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/cal_op/op_webcam/DIM.npy"
jetson_K = "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/cal_op/op_webcam/K.npy"
jetson_D = "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/cal_op/op_webcam/D.npy"
# ----------------------- Jetson Directory v. Laptop directory------------------------
laptop_DIM = "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal_op\\op_webcam\\DIM.npy"
laptop_K = "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal_op\\op_webcam\\K.npy"
laptop_D = "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal_op\\op_webcam\\D.npy"

# Get params
DIM = np.load(laptop_DIM)
K = np.load(laptop_K)
D = np.load(laptop_D)

balance = 0  # Set to 1 to show black space. Set to 0 to crop
new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
    K, D, DIM, np.eye(3), balance=balance)  # Need this step if we don't want to crop
map1, map2 = cv2.fisheye.initUndistortRectifyMap(
    K, D, np.eye(3), new_K, DIM, cv2.CV_16SC2)


def find_pose_from_tag(K, detection):

    m_half_size = tag_size / 2

    marker_center = np.array((0, 0, 0))
    marker_points = []
    marker_points.append(marker_center + (-m_half_size, m_half_size, 0))
    marker_points.append(marker_center + (m_half_size, m_half_size, 0))
    marker_points.append(marker_center + (m_half_size, -m_half_size, 0))
    marker_points.append(marker_center + (-m_half_size, -m_half_size, 0))
    # Marker points is an array that contains the coords of the four corners on the tag.
    # The last coord is always zero as the z dim, since its relative to the tag itself.
    _marker_points = np.array(marker_points)

    object_points = _marker_points
    # The corners of the tag in image pixel coordinates. These always wrap counter-
    # clock wise around the tag
    image_points = detection.corners

    # pnp_ret -> [True | False, rotation vector, translation vector]
    pnp_ret = cv2.solvePnP(object_points, image_points,
                           K, distCoeffs=None, flags=cv2.SOLVEPNP_IPPE_SQUARE)

    # First element tells us if the operation was successful or not
    if pnp_ret[0] == False:
        raise Exception('Error solving PnP')

    # Rotation vector
    r = pnp_ret[1]
    # Translation vector (Why is it labeled 'p'?)
    p = pnp_ret[2]

    # Before reshaping, p and r are arrays of arrays. This reduces them to just
    # arrays whilst maintaining their values
    p_fin = p.reshape((3,))
    r_fin = r.reshape((3,))
    return p_fin, r_fin


if __name__ == '__main__':
    vid = cv2.VideoCapture(1)

    tag_size = 0.13  # tag size in meters

    # These will be the tags that we want for the corners
    corner_tags = [0, 1, 2, 3]
    while True:
        k = cv2.waitKey(1)
        try:
            detect_arr = dict()
            ret, img = vid.read()
            # Undistorted image
            ud_img = cv2.remap(
                img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            gray = cv2.cvtColor(ud_img, cv2.COLOR_BGR2GRAY)
            gray.astype(np.uint8)

            # The K matrix below is the result of running camera calibration
            # it has to be calibrated per camera model, these numbers
            # are not correct for a robot mouse or any student's
            # particular laptop
            # K=np.array([[207.9878620183829, 0.0, 338.10802140849563], [0.0, 208.9172074014061, 229.54749116130657], [0.0, 0.0, 1.0]])

            results = at_detector.detect(gray, estimate_tag_pose=False)
            # print(results[0].tag_id)
            # make detect_arr a dictionary
            # when a tag is found that is in corner_tags, add it to the dictionary with tag_id as its index.
            # use detect_arr 125 - 128
            for res in results:
                for x in range(len(results)):
                    detect_arr.update({results[x].tag_id: results[x]})
                detect_keys = list(detect_arr.keys())
                detect_keys.sort()
                # Codeblock Poggers
                sorted_dict = {i: detect_arr[i] for i in detect_keys}
                # print(detect_keys)

                # Idea: Use the dictionary that we made eariler and pass it as an argument in a draw_frame function
                if set(detect_keys) & set(corner_tags) == set(corner_tags):
                    # Draw box lines
                    cv2.line(ud_img, (int(sorted_dict[0].center[0]), int(sorted_dict[0].center[1])), (int(
                        sorted_dict[1].center[0]), int(sorted_dict[1].center[1])), color=(0, 255, 0), thickness=5)
                    cv2.line(ud_img, (int(sorted_dict[1].center[0]), int(sorted_dict[1].center[1])), (int(
                        sorted_dict[2].center[0]), int(sorted_dict[2].center[1])), color=(0, 255, 0), thickness=5)
                    cv2.line(ud_img, (int(sorted_dict[2].center[0]), int(sorted_dict[2].center[1])), (int(
                        sorted_dict[3].center[0]), int(sorted_dict[3].center[1])), color=(0, 255, 0), thickness=5)
                    cv2.line(ud_img, (int(sorted_dict[3].center[0]), int(sorted_dict[3].center[1])), (int(
                        sorted_dict[0].center[0]), int(sorted_dict[0].center[1])), color=(0, 255, 0), thickness=5)

                    # Finally, we need the midpoints in order to find the normal vector
                    mid0 = (int((sorted_dict[0].center[0] + sorted_dict[1].center[0])/2), int(
                        (sorted_dict[0].center[1] + sorted_dict[1].center[1])/2))
                    mid1 = (int((sorted_dict[1].center[0] + sorted_dict[2].center[0])/2), int(
                        (sorted_dict[1].center[1] + sorted_dict[2].center[1])/2))
                    mid2 = (int((sorted_dict[2].center[0] + sorted_dict[3].center[0])/2), int(
                        (sorted_dict[2].center[1] + sorted_dict[3].center[1])/2))
                    mid3 = (int((sorted_dict[3].center[0] + sorted_dict[0].center[0])/2), int(
                        (sorted_dict[3].center[1] + sorted_dict[0].center[1])/2))

                    # If there is an additional tag in the array of detected tags, we want to perform boundary detection
                    if len(detect_keys) > 4:
                        # Arrays to hold our stuff
                        corners = []
                        mice_tags = []
                        b_arr = {}
                        d_arr = []
                        a_arr = []
                        res_arr = []
                        # Coordinates of tags
                        for x in corner_tags:
                            corners.append(
                                np.array([int(sorted_dict[x].center[0]), int(sorted_dict[x].center[1])]))

                        # Find difference from each pair of tags
                        # Arrowhead - nock
                        for x in range(3):
                             d_arr.append(corners[x+1] - corners[x])
                             d_arr.append(corners[0] - corners[3])

                        # Rotation matrix
                        rot = np.array([[0, -1], [1, 0]])

                        # Take dot product of each difference and the rotation matrix to make the norm (?)
                        for x in range(len(corner_tags)):
                            a_arr.append(np.dot(rot, d_arr[x]))

                        print("")
                        # print(a_arr)

                        # Coordinates of the mouse
                        for x in range(4, len(detect_keys)):
                            mice_tags.append(
                                np.array([int(sorted_dict[x].center[0]), int(sorted_dict[x].center[1])]))

                        
                        match len(mice_tags):
                            case 1:
                                b_arr.update({1:[(mice_tags[0][0] - corners[0][0],mice_tags[0][1] - corners[0][1]),
                                                         (mice_tags[0][0] - corners[1][0],mice_tags[0][1] - corners[1][1]),
                                                         (mice_tags[0][0] - corners[2][0],mice_tags[0][1] - corners[2][1]),
                                                         (mice_tags[0][0] - corners[3][0],mice_tags[0][1] - corners[3][1])]})
                            case 2:
                                b_arr.update({1:[(mice_tags[0][0] - corners[0][0],mice_tags[0][1] - corners[0][1]),
                                                         (mice_tags[0][0] - corners[1][0],mice_tags[0][1] - corners[1][1]),
                                                         (mice_tags[0][0] - corners[2][0],mice_tags[0][1] - corners[2][1]),
                                                         (mice_tags[0][0] - corners[3][0],mice_tags[0][1] - corners[3][1])]})
                                
                                b_arr.update({2:[(mice_tags[1][0] - corners[0][0],mice_tags[1][1] - corners[0][1]),
                                                         (mice_tags[1][0] - corners[1][0],mice_tags[1][1] - corners[1][1]),
                                                         (mice_tags[1][0] - corners[2][0],mice_tags[1][1] - corners[2][1]),
                                                         (mice_tags[1][0] - corners[3][0],mice_tags[1][1] - corners[3][1])]})

                            case 3:
                                b_arr.update({1:[(mice_tags[0][0] - corners[0][0],mice_tags[0][1] - corners[0][1]),
                                                         (mice_tags[0][0] - corners[1][0],mice_tags[0][1] - corners[1][1]),
                                                         (mice_tags[0][0] - corners[2][0],mice_tags[0][1] - corners[2][1]),
                                                         (mice_tags[0][0] - corners[3][0],mice_tags[0][1] - corners[3][1])]})
                                
                                b_arr.update({2:[(mice_tags[1][0] - corners[0][0],mice_tags[1][1] - corners[0][1]),
                                                         (mice_tags[1][0] - corners[1][0],mice_tags[1][1] - corners[1][1]),
                                                         (mice_tags[1][0] - corners[2][0],mice_tags[1][1] - corners[2][1]),
                                                         (mice_tags[1][0] - corners[3][0],mice_tags[1][1] - corners[3][1])]})
                                
                                b_arr.update({3:[(mice_tags[2][0] - corners[0][0],mice_tags[2][1] - corners[0][1]),
                                                         (mice_tags[2][0] - corners[1][0],mice_tags[2][1] - corners[1][1]),
                                                         (mice_tags[2][0] - corners[2][0],mice_tags[2][1] - corners[2][1]),
                                                         (mice_tags[2][0] - corners[3][0],mice_tags[2][1] - corners[3][1])]})

                            case _:
                                print("Mouse length array OOB")
                        """ b_arr.append(
                                [mice_tags[x] - corners[0], mice_tags[x] - corners[1], mice_tags[x] - corners[2], mice_tags[x] - corners[3]]) """

                        print(b_arr)

                        # Find the result from each dot product
                        for x in range(len(a_arr)):
                            for y in range(len(b_arr)):
                                res_arr.append(np.dot(a_arr[x], b_arr[y]))

                        for x in range(0,len(res_arr)):
                            print(res_arr[x])

                # Gets back both the rotation and translation matrices from solvePNP
                pose = find_pose_from_tag(K, res)
                # This will take in our translation VECTOR and turn it into a translation MATRIX.
                # It will then set the value to itself, effectively overwritting the the vertex from before
                # rot -> rotation matrix from previous
                # jaco -> jacobian transform or nah (We don't use this)

                # Is "rot" Rwa from the slides?
                # Where is the translation matrix? Is it in "pose"?

                rot, jaco = cv2.Rodrigues(pose[1], pose[1])
                # print(rot)

                pts = res.corners.reshape((-1, 1, 2)).astype(np.int32)
                # print("VVVV")
                # print("VVVV")
                # print("VVVV")
                # print(pts)
                # print("^^^")
                # print("^^^")
                # print("^^^")
                ud_img = cv2.polylines(
                    ud_img, [pts], isClosed=True, color=(0, 0, 255), thickness=5)
                cv2.circle(ud_img, tuple(res.center.astype(np.int32)),
                           5, (0, 0, 255), -1)

                text_loc = (int(res.center[0]) + 5, int(res.center[1]) + 5)

                cv2.putText(ud_img, "{}".format(text_loc), text_loc,
                            cv2.FONT_HERSHEY_COMPLEX, .5, (0, 0, 255), 1)

                # cv2.line(ud_img, )

                # print(pose)

            cv2.imshow("img", ud_img)

        except KeyboardInterrupt:
            vid.release()
            cv2.destroyAllWindows()
            print('Exiting')
            exit(1)
        cv2.waitKey(10)
        if k % 256 == 0:
            # SPACE pressed
            img_name = "putText.png"
            cv2.imwrite(img_name, ud_img)
            print("{} written!".format(img_name))
