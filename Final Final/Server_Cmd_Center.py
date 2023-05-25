import socket
import struct
import time
import Trajectory_Utility as util
import pyaudio as pa
import matplotlib.pyplot as plt
from sound_delay import correlation_algo

# April tag stuff
from pupil_apriltags import Detector
import cv2
import numpy as np
import os

# Change directory to a folder that will contain the chessboard pics (APRILTAGS)
# laptop = "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\misc_img"
jetson = "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/data/raw/set_webcam"
# dir = "C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal\\"
# dir_wsl = "/mnt/c/Users/Dilan/Documents/GitHub/SPRING2023_Team1/DCF_stuff/opencv/data/raw/set_webcam"
# dir = r"C:\\Users\\Dilan\\Documents\\GitHub\\SPRING2023_Team1\\DCF_stuff\\opencv"
nick = "/Users/nicholasboomsma/Documents/ENEE408I/SPRING2023_Team1/DCF_stuff/opencv/data/raw/set_webcam"
adrian = "C:\\Users\\pc\\Documents\\ENEE408I\\SPRING2023_Team1\\DCF_stuff\\opencv\\data\\raw\\set_webcam"
os.chdir(adrian)

# Straightening the camera feed
jetson_DIM = "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/cal_op/op_webcam/DIM.npy"
jetson_K = "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/cal_op/op_webcam/K.npy"
jetson_D = "/home/dilancf/Desktop/docs/spring2023/SPRING2023_Team1/DCF_stuff/opencv/cal_op/op_webcam/D.npy"

nick_DIM = "/Users/nicholasboomsma/Documents/ENEE408I/SPRING2023_Team1/DCF_stuff/opencv/cal_op/op_webcam/DIM.npy"
nick_K = "/Users/nicholasboomsma/Documents/ENEE408I/SPRING2023_Team1/DCF_stuff/opencv/cal_op/op_webcam/K.npy"
nick_D = "/Users/nicholasboomsma/Documents/ENEE408I/SPRING2023_Team1/DCF_stuff/opencv/cal_op/op_webcam/D.npy"


adrian_DIM = "C:\\Users\\pc\\Documents\\ENEE408I\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal_op\\op_webcam\\DIM.npy"
adrian_K = "C:\\Users\\pc\\Documents\\ENEE408I\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal_op\\op_webcam\\K.npy"
adrian_D = "C:\\Users\\pc\\Documents\\ENEE408I\\SPRING2023_Team1\\DCF_stuff\\opencv\\cal_op\\op_webcam\\D.npy"

# Get params (APRILTAGS)
DIM = np.load(adrian_DIM)
K = np.load(adrian_K)
D = np.load(adrian_D)

vid = cv2.VideoCapture(1)

tag_size = 0.13  # tag size in meters

# These will be the tags that we want for the corners
corner_tags = [0, 1, 2, 3]

# Undistorting camera (APRILTAGS)
balance = 0  # Set to 1 to show black space. Set to 0 to crop
new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(
    K, D, DIM, np.eye(3), balance=balance)  # Need this step if we don't want to crop
map1, map2 = cv2.fisheye.initUndistortRectifyMap(
    K, D, np.eye(3), new_K, DIM, cv2.CV_16SC2)


# Used to identify which tag is out of bounds (APRILTAGS)
# [int * 12] -> [bool * 3]
def tags_oob(arr):
    # The input array  is an array of 12 integers. We can think of them as four lists of three integers, 
    # where every sublist contains the projections of the three mice onto the correpsonding vector

    # [[proj_m0_v0, proj_m1_v0, proj_m2_v0], [proj_m0_v1, proj_m1_v1, proj_m2_v1], [proj_m0_v2, proj_m1_v2, proj_m2_v2], [proj_m0_v3, proj_m1_v3, proj_m2_v3]]
    #  |---------vector 0 -> 1------------|  |---------vector 1 -> 2------------|  |---------vector 2 -> 3------------|  |---------vector 3 -> 0------------|
    
    # Since they are stored in this order, we can have cases for each mouse and each vector they may be involved in. 
    mouse00_i = [0, 3, 6, 9]
    mouse01_i = [1, 4, 7, 10]
    mouse02_1 = [2, 5, 8, 11]

    res = [True, True, True]
    for x in range(len(arr)):
        # We have detected a tag to be outside of the arena, check for which tag it is.
        if arr[x] < 0:
            # Check which index x corresponds to
            if x in mouse00_i:
                res[0] = False
            if x in mouse01_i:
                res[1] = False
            if x in mouse02_1:
                res[2] = False
    return res

# Used for apriltag detection, gives the rotation vector and the translation vectors n stuff (APRILTAGS)
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

# Microphone Setup
# Start of PyAudio code which will record sound from two microphones
p = pa.PyAudio()

# Defines microphone parameters such as chunk size, frequency rate of mic, and data format 
CHUNK = 1024
FORMAT = pa.paInt16
CHANNELS = 1
RATE = 44100

# Checks to see how many audio input devices are being recognized by PyAudio
# for i in range(p.get_device_count()):
#     print(p.get_device_info_by_index(i))

# Starts two audio streams "stream1" and "stream2" corresponding to the two microphones
# and sets the different parameters previously declared
stream1 = p.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    output = True,
    frames_per_buffer = CHUNK,
    input_device_index = 1,
)

stream2 = p.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    output = True,
    frames_per_buffer = CHUNK,
    input_device_index = 2,
)

# Creates a matplotlib figure which will display the decibel rating of the two
# sound intensities and their respective frequencies
fig, (ax1, ax2) = plt.subplots(1, 2)
ax1.set_title("Sound Intensity Recorded from Robot 1")
ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylabel("Magnitude (dB)")
x_fft = np.linspace(0, RATE, CHUNK)
line_fft1, = ax1.semilogx(x_fft, np.random.rand(CHUNK), 'b')
ax1.set_xlim(20, RATE/2)
ax1.set_ylim(-90, 5)

ax2.set_title("Sound Intensity Recorded from Robot 2")
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Magnitude (dB)")
x_fft = np.linspace(0, RATE, CHUNK)
line_fft2, = ax2.semilogx(x_fft, np.random.rand(CHUNK), 'b')
ax2.set_xlim(20, RATE/2)
ax2.set_ylim(-90, 5)

# Server Setup
localIP = "192.168.2.102"

localPort1 = 3333
localPort2 = 4444
localPort3 = 5555

bufferSize = 1024

# Detector object
at_detector = Detector(
    families="tag36h11",
    nthreads=1,
    quad_decimate=1.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
)

# Create a datagram socket

UDPServerSocket1 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket2 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# UDPServerSocket3 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip

UDPServerSocket1.bind((localIP, localPort1))
UDPServerSocket2.bind((localIP, localPort2))
# UDPServerSocket3.bind((localIP, localPort3))

print("UDP server up and ready to send a packet")

# Check connection from robot to server

bytesAddressPair1 = UDPServerSocket1.recvfrom(bufferSize)
print("Mouse 1 Address Received")
offset_pack1 = struct.pack("f", 1)
address1 = bytesAddressPair1[1]
UDPServerSocket1.sendto(offset_pack1, address1)


bytesAddressPair2 = UDPServerSocket2.recvfrom(bufferSize)
print("Mouse 2 Address Received")
offset_pack2 = struct.pack("f", 1)
address2 = bytesAddressPair2[1]
UDPServerSocket2.sendto(offset_pack2, address2)
# bytesAddressPair3 = UDPServerSocket3.recvfrom(bufferSize)
# print("Mouse 3 Address Received")


message1 = bytesAddressPair1[0]
address1 = bytesAddressPair1[1]
message2 = bytesAddressPair2[0]
address2 = bytesAddressPair2[1]
# message3 = bytesAddressPair3[0]
# address3 = bytesAddressPair3[1]


clientMsg1 = "Message from Client1:{}".format(message1)
clientIP1 = "Client1 IP Address:{}".format(address1)
clientMsg2 = "Message from Client2:{}".format(message2)
clientIP2 = "Client2 IP Address:{}".format(address2)
# clientMsg3 = "Message from Client3:{}".format(message3)
# clientIP3 = "Client3 IP Address:{}".format(address3)

print(clientMsg1)
print(clientIP1)
print(clientMsg2)
print(clientIP2)
# print(clientMsg3)
# print(clientIP3)


# Give time for mice to setup
time.sleep(5)

# The loop runs 10 times to calculate the average time delay "error"
count = 0
time_delay_list = []
while (count < 3):
    time_delay_list.append(correlation_algo(stream1, stream2, CHUNK))
    count += 1

avg_time_offset = sum(time_delay_list)/len(time_delay_list)

# Listen for incoming datagrams

while (True):
    """ SOUND SECTION """
    final_time_delay = correlation_algo(stream1, stream2, CHUNK)
    final_time_delay = final_time_delay - avg_time_offset
    print(final_time_delay)

    """ APRILTAG SECTION """
    k = cv2.waitKey(1)
    print('hi')
    try:
        print("hi2")
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

                    # If there is an additional tag in the array of detected tags, we want to perform boundary detection
                    # print("sorted_dict: ", sorted_dict)
                    if len(detect_keys) > 4:
                        # Arrays to hold our stuff
                        corners = []
                        mice_tags = []
                        b_arr = {}
                        d_arr = []
                        a_arr = []
                        res_arr = []
                        mouse_tt = []
                        # Coordinates of center of tags
                        # corner_tags (List) -> [(x_coord, y_coord)]
                        for x in corner_tags:
                            corners.append(
                                np.array([int(sorted_dict[x].center[0]), int(sorted_dict[x].center[1])]))
                        print("corners: ", corners)

                        # Find difference from each pair of tags
                        # Arrowhead - nock
                        # d_arr (List) -> [()]
                        for x in range(3):
                            # print( corners[x+1][0] - corners[x][0],corners[x+1][1] - corners[x][1])
                            d_arr.append(
                                np.array((corners[x+1][0] - corners[x][0], corners[x+1][1] - corners[x][1])))
                        d_arr.append(
                            np.array((corners[0][0] - corners[3][0], corners[0][1] - corners[3][1])))

                        print("d_arr: ", d_arr)
                        # Rotation matrix
                        rot = np.array([[0, -1], [1, 0]])

                        # Take dot product of each difference and the rotation matrix to make the norm (?)
                        for x in range(len(corner_tags)):
                            a_arr.append(np.dot(rot, d_arr[x]))
                        print("a_arr: ", a_arr)

                        # print("")
                        # Coordinates of the mouse
                        # This code breaks if tag 4 is not one of the mice in frame. if only 5 and/or 6 are in frame the code complains
                        for x in range(4, len(detect_keys)):
                            mice_tags.append(
                                np.array((int(sorted_dict[x].center[0]), int(sorted_dict[x].center[1]))))
                        print("mice_tags: ", mice_tags)

                        mouse_len = len(mice_tags)
                        if mouse_len == 1:
                            b_arr.update({0: [np.array((mice_tags[0][0] - corners[0][0], mice_tags[0][1] - corners[0][1])),
                                              np.array(
                                                  (mice_tags[0][0] - corners[1][0], mice_tags[0][1] - corners[1][1])),
                                              np.array(
                                                  (mice_tags[0][0] - corners[2][0], mice_tags[0][1] - corners[2][1])),
                                              np.array((mice_tags[0][0] - corners[3][0], mice_tags[0][1] - corners[3][1]))]})
                        elif mouse_len == 2:
                            b_arr.update({0: [np.array((mice_tags[0][0] - corners[0][0], mice_tags[0][1] - corners[0][1])),
                                              np.array(
                                                  (mice_tags[0][0] - corners[1][0], mice_tags[0][1] - corners[1][1])),
                                              np.array(
                                                  (mice_tags[0][0] - corners[2][0], mice_tags[0][1] - corners[2][1])),
                                              np.array((mice_tags[0][0] - corners[3][0], mice_tags[0][1] - corners[3][1]))]})

                            b_arr.update({1: [np.array((mice_tags[1][0] - corners[0][0], mice_tags[1][1] - corners[0][1])),
                                              np.array(
                                                  (mice_tags[1][0] - corners[1][0], mice_tags[1][1] - corners[1][1])),
                                              np.array(
                                                  (mice_tags[1][0] - corners[2][0], mice_tags[1][1] - corners[2][1])),
                                              np.array((mice_tags[1][0] - corners[3][0], mice_tags[1][1] - corners[3][1]))]})

                        elif mouse_len == 3:
                            b_arr.update({0: [np.array((mice_tags[0][0] - corners[0][0], mice_tags[0][1] - corners[0][1])),
                                              np.array(
                                                  (mice_tags[0][0] - corners[1][0], mice_tags[0][1] - corners[1][1])),
                                              np.array(
                                                  (mice_tags[0][0] - corners[2][0], mice_tags[0][1] - corners[2][1])),
                                              np.array((mice_tags[0][0] - corners[3][0], mice_tags[0][1] - corners[3][1]))]})

                            b_arr.update({1: [np.array((mice_tags[1][0] - corners[0][0], mice_tags[1][1] - corners[0][1])),
                                              np.array(
                                                  (mice_tags[1][0] - corners[1][0], mice_tags[1][1] - corners[1][1])),
                                              np.array(
                                                  (mice_tags[1][0] - corners[2][0], mice_tags[1][1] - corners[2][1])),
                                              np.array((mice_tags[1][0] - corners[3][0], mice_tags[1][1] - corners[3][1]))]})
                            b_arr.update({2: [np.array((mice_tags[2][0] - corners[0][0], mice_tags[2][1] - corners[0][1])),
                                              np.array(
                                                  (mice_tags[2][0] - corners[1][0], mice_tags[2][1] - corners[1][1])),
                                              np.array(
                                (mice_tags[2][0] - corners[2][0], mice_tags[2][1] - corners[2][1])),
                                np.array((mice_tags[2][0] - corners[3][0], mice_tags[2][1] - corners[3][1]))]})
                        else:
                            print("Mouse length array OOB")
                        # print("b_arr: ", b_arr)
                        # print("b_arr[0]: ", b_arr[0])
                        # print("a_arr: ", a_arr)
                        # Find the result from each dot product
                        # print("a_arr and b_arr (BEFORE): ", a_arr[0], b_arr[0][0])
                        # a_arr = np.reshape(4,1)
                        # b_arr = np.reshape(4,1)
                        for x in range(len(a_arr)):
                            for y in range(len(b_arr)):
                                # print("a_arr and b_arr(AFTER): ", a_arr[x], b_arr[y])
                                res_arr.append(np.dot(a_arr[x], b_arr[y][x]))
                        for x in range(0, len(res_arr)):
                            print(res_arr[x])

                        mouse_tt = tags_oob(res_arr)
                        mice_tags = list(map(tuple, mice_tags))
                        corners = list(map(tuple, corners))

                        cv2.putText(ud_img, "{}".format(
                            mouse_tt),    (5, 350), cv2.FONT_HERSHEY_COMPLEX, .5, (0, 0, 255), 1)
                        cv2.putText(ud_img, "{}".format(
                            mice_tags),   (5, 400), cv2.FONT_HERSHEY_COMPLEX, .5, (0, 0, 255), 1)
                        cv2.putText(ud_img, "{}".format(
                            corners),     (5, 450), cv2.FONT_HERSHEY_COMPLEX, .5, (0, 0, 255), 1)

                        fin_arr = [mouse_tt] + [mice_tags] + [corners]
                        print(fin_arr)
                        # "{}".format(res_arr)
                        corners = []
                        mice_tags = []
                        b_arr = {}
                        d_arr = []
                        a_arr = []
                        res_arr = []
                        mouse_tt = []
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
                ud_img = cv2.polylines(
                    ud_img, [pts], isClosed=True, color=(0, 0, 255), thickness=5)
                cv2.circle(ud_img, tuple(res.center.astype(np.int32)),
                           5, (0, 0, 255), -1)

                text_loc = (int(res.center[0]) + 5, int(res.center[1]) + 5)

                cv2.putText(ud_img, "{}".format(text_loc), text_loc,
                            cv2.FONT_HERSHEY_COMPLEX, .5, (0, 0, 255), 1)

        cv2.imshow("img", ud_img)
    except KeyboardInterrupt:
        vid.release()
        cv2.destroyAllWindows()
        print('Exiting')
        exit(1)
    cv2.waitKey(10)

    # fin_arr a list of lists. That way, each relevant array may be pulled with ease,
    # i.e the array indicating whether a certain mouse is in bounds is at index 0 and so on.
    # [[bool, bool, bool],[(tuple), (tuple), (tuple)],[(tuple), (tuple), (tuple), (tuple)]]
    # [[m1_oob, m2_oob, m3_oob], [(m1_coords), (m2_coords), (m3_coords)], [(corner0_coords), (corner1_coords), (corner2_coords), (corner3_coords)]]

    # Get boundary corners
    # bound## tuples' first value is the x-pos, second value is the y-pos
    # bound00 = fin_arr[2][0]
    # bound01 = fin_arr[2][1]
    # bound10 = fin_arr[2][3]
    # bound11 = fin_arr[2][2]

    # # Calculate midpoints for quadrants (notice mid_3 and mid_2 switch for easier calculation)
    # mid_x = (bound00[0]+bound01[0]+bound10[0]+bound11[0])/4
    # mid_y = (bound00[1]+bound01[1]+bound10[1]+bound11[1])/4
    # mid_0 = ((bound00[0]+mid_x)/2, (bound00[1]+mid_y)/2)
    # mid_1 = ((bound01[0]+mid_x)/2, (bound01[1]+mid_y)/2)
    # mid_3 = ((bound10[0]+mid_x)/2, (bound10[1]+mid_y)/2)
    # mid_2 = ((bound11[0]+mid_x)/2, (bound11[1]+mid_y)/2)
    # mids = (mid_0, mid_1, mid_2, mid_3, mid_x, mid_y)

    # # Mouse Location List
    # mouse_locs = fin_arr[1]

    target_theta1 = 0.0
    target_theta2 = 0.0
    if(final_time_delay < 0):
        target_v1 = 0.0
        target_v2 = 0.1
    else:
        target_v1 = 0.1
        target_v2 = 0.0

    # Calculate headings for both tracking robots and evading robot
    #headingSet1 = util.getTrackerHeadings(
    #    mouse_locs[0], mouse_locs[1], soundData)
    #headingSet2 = util.getEvaderHeading(
    #    mouse_locs[0], mouse_locs[1], mouse_locs[2], mids)

    # target_theta1 = headingSet1[0]
    # target_v1 = headingSet1[1]
    # target_theta2 = headingSet1[2]
    # target_v2 = headingSet1[3]
    #target_theta3 = headingSet2[0]
    #target_v3 = headingSet2[1]

    # Creating Packet to Send to Mouse
    # First value sent is the cam theta, the second value is the target_theta, and the third value is the velocity
    #offset_pack1 = struct.pack("fff", 0, target_theta1, target_v1)
    #offset_pack2 = struct.pack("fff", 0, -target_theta2, target_v2)
    #offset_pack3 = struct.pack("fff", 0, target_theta3, target_v3)

    offset_pack1 = struct.pack("fff", 0, target_theta1, target_v1)
    offset_pack2 = struct.pack("fff", 0, target_theta2, target_v2)
    #offset_pack3 = struct.pack("fff", 0, 0.0, 0.0)

    UDPServerSocket1.sendto(offset_pack1, address1)
    UDPServerSocket2.sendto(offset_pack2, address2)
    #UDPServerSocket3.sendto(offset_pack3, address3)