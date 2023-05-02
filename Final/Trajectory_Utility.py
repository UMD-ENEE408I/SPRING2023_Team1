import math
from gekko import GEKKO

# Given the tangential line at the midpoint of the two Tracker robots and the circle with the closer
# Tracker bot at its center, find the intersection
def getTargetCoordinates(midpt_x, midpt_y, midpt_m, circle_x, circle_y, circle_r):
    m = GEKKO()
    x = m.Var(value=circle_x+1)
    y = m.Var(value=circle_y)
    m.Equations([midpt_m*(x - midpt_x) == (y - midpt_y), (x-circle_x)**2 + (y-circle_y)**2 == circle_r**2])
    m.solve(disp=False)
    return x.VALUE,y.VALUE

#Finds new theta and target_v headings for both tracking robots (should be coordinated with one another)
#Tracking Robot 1: (x1,y1)
#Tracking Robot 2: (x2,y2)
def getTrackerHeadings(x1, y1, x2, y2, soundData):
    midpt_x = (x1+x2)/2
    midpt_y = (y1+y2)/2

    # "m" is slope
    xy_m = (y2-y1)/(x2-x1)
    midpt_m = -(1/xy_m) 
    radius_xy = math.sqrt(pow(abs(x2-x1),2) + pow(abs(y2-y1),2))

    # If soundData == 1, Tracker 1 is closer, else Tracker 2 is closer
    if(soundData == 1):
        target_x, target_y = getTargetCoordinates(midpt_x, midpt_y, midpt_m, x1, y1, radius_xy)
    else:
        target_x, target_y = getTargetCoordinates(midpt_x, midpt_y, midpt_m, x2, y2, radius_xy)

    # Calculates target_v1, target_theta1, target_v2, target_theta2, based on target_x and target_y
    if(soundData == 1):
        target_v1 = 0.0
        target_theta1 = signedAngle(x1, y1, target_x, target_y)
        target_v2 = 0.2
        target_theta2 = signedAngle(x2, y2, target_x, target_y)
    else:
        target_v1 = 0.2
        target_theta1 = signedAngle(x1, y1, target_x, target_y)
        target_v2 = 0.0
        target_theta2 = signedAngle(x2, y2, target_x, target_y)

    return target_theta1, target_v1, target_theta2, target_v2

#Finds target_theta and target_v for evader robot
#Tracking Robot 1: (x1,y1)
#Tracking Robot 2: (x2,y2)
#Evader Robot: (x3,y3)
def getEvaderHeading(x1, y1, x2, y2, x3, y3, mids):
    mid_0 = mids[0]
    mid_1 = mids[1]
    mid_2 = mids[2]
    mid_3 = mids[3]
    mid_x = mids[4]
    mid_y = mids[5]

    target_x = mid_x
    target_y = mid_y

    dist1_3 = math.sqrt(pow(abs(x3-x1),2) + pow(abs(y3-y1),2))
    dist2_3 = math.sqrt(pow(abs(x3-x2),2) + pow(abs(y3-y2),2))

    if(dist1_3 < dist2_3):
        close_x = x1
        close_y = y1
    else:
        close_x = x2
        close_y = y2
    
    quadClose = getQuadrant(close_x, close_y, mid_x, mid_y) # Quadrant Close Tracker is in
    quad3 = getQuadrant(x3, y3, mid_x, mid_y) # Quadrant Evader is in
    # Currently only care about Close Tracker and Evader
    if((quadClose-quad3) == 0):
        #Tracker 1 and Evader in same quadrant
        # Find distance between robots and quadrant dividers
        distClose_x = abs(close_x - mid_x)
        distClose_y = abs(close_y - mid_y)
        dist3_x = abs(x3 - mid_x)
        dist3_y = abs(y3 - mid_y)
        diff_x = dist3_x - distClose_x
        diff_y = dist3_y - distClose_y
        if(diff_x < diff_y):
            if(quad3 == 0 or quad3 == 2):
                nextQuad = quad3 + 1
            else:
                nextQuad = quad3 - 1
        else:
            if(quad3 == 0 or quad3 == 2):
                nextQuad = (quad3 - 1) % 4
            else:
                nextQuad = (quad3 + 1) % 4
    elif(abs(quadClose-quad3) == 1 or abs(quadClose-quad3) == 3):
        #Tracker 1 and Evader in lateral quadrants
        diff = quadClose - quad3
        nextQuad = (quad3 - diff) % 4
    else:
        #Tracker 1 and Evader in diagonal quadrants
        nextQuad = quad3
    if(nextQuad == 0):
        target_x = mid_0[0]
        target_y = mid_0[1]
    elif(nextQuad == 1):
        target_x = mid_1[0]
        target_y = mid_1[1]
    elif(nextQuad == 2):
        target_x = mid_2[0]
        target_y = mid_2[1]
    else:
        target_x = mid_3[0]
        target_y = mid_3[1]

    # Calculate target_v3 and target_theta3 based on target_x and target_y
    target_v3 = 0.1
    if(quad3 == nextQuad):
        target_v3 = 0.0
        target_theta3 = signedAngle(x3, y3, mid_x, mid_y)
    else:
        target_theta3 = signedAngle(x3, y3, target_x, target_y)

    return target_theta3, target_v3

# Gets quadrant the robot is currently in
# Quadrant number starts at 0 top-left, then add 1 moving clockwise
def getQuadrant(x, y, mid_x, mid_y):
    if(x > mid_x):
        if(y > mid_y):
            # Bottom Right
            return 2
        else:
            # Top Right
            return 1
    else:
        if(y > mid_y):
            # Bottom Left
            return 3
        else:
            # Top Left
            return 0
        
#Finds angle of vector from point (x1,y1) to (x2, y2)
def signedAngle(x1, y1, x2, y2):
    x = x2 - x1
    y = y2 - y1
    return math.tan(y/x)