import cv2 as cv

vid = cv.VideoCapture(1)

while(True):
	ret, frame = vid.read()
	cv.imshow('Hello there', frame)
	if cv.waitKey(1) & 0XFF == ord('q'):
		break
vid.release()
cv.destroyAllWindows()
