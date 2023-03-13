from pupil_apriltags import Detector
import cv2
import numpy as np
import time



at_detector = Detector(
    families="tag36h11",
    nthreads=1,
    quad_decimate=1.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
)

def find_pose_from_tag(K, detection):
    m_half_size = tag_size / 2

    marker_center = np.array((0, 0, 0))
    marker_points = []
    marker_points.append(marker_center + (-m_half_size, m_half_size, 0))
    marker_points.append(marker_center + ( m_half_size, m_half_size, 0))
    marker_points.append(marker_center + ( m_half_size, -m_half_size, 0))
    marker_points.append(marker_center + (-m_half_size, -m_half_size, 0))
    _marker_points = np.array(marker_points)

    object_points = _marker_points
    image_points = detection.corners

    pnp_ret = cv2.solvePnP(object_points, image_points, K, distCoeffs=None,flags=cv2.SOLVEPNP_IPPE_SQUARE)
    if pnp_ret[0] == False:
        raise Exception('Error solving PnP')

    r = pnp_ret[1]
    p = pnp_ret[2]

    return p.reshape((3,)), r.reshape((3,))


if __name__ == '__main__':
    vid = cv2.VideoCapture(1)

    tag_size=0.16 # tag size in meters

    while True:
        try:
            ret, img = vid.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray.astype(np.uint8)

            # The K matrix below is the result of running camera calibration
            # it has to be calibrated per camera model, these numbers
            # are not correct for a robot mouse or any student's
            # particular laptop
            K=np.array([[203.71832715762605, 0.0, 319.5], [0.0, 203.71832715762605, 239.5], [0.0, 0.0, 1.0]])

            results = at_detector.detect(gray, estimate_tag_pose=False)

            for res in results:
                pose = find_pose_from_tag(K, res)
                rot, jaco = cv2.Rodrigues(pose[1], pose[1])
                print(rot)

                pts = res.corners.reshape((-1, 1, 2)).astype(np.int32)
                img = cv2.polylines(img, [pts], isClosed=True, color=(0, 0, 255), thickness=5)
                cv2.circle(img, tuple(res.center.astype(np.int32)), 5, (0, 0, 255), -1)

                print(pose)

            cv2.imshow("img", img)
            cv2.waitKey(10)

        except KeyboardInterrupt:
            vid.release()
            cv2.destroyAllWindows()
            print ('Exiting')
            exit(1)


