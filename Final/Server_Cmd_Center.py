import socket
import struct
import time
import Trajectory_Utility as util

localIP = ""

localPort1 = 3333
localPort2 = 4444
localPort3 = 5555

bufferSize = 1024

# Create a datagram socket

UDPServerSocket1 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket2 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket3 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip

UDPServerSocket1.bind((localIP, localPort1))
UDPServerSocket2.bind((localIP, localPort2))
UDPServerSocket3.bind((localIP, localPort3))

print("UDP server up and ready to send a packet")

target_theta = 0.5
target_v = 0.2

# Check connection from robot to server

bytesAddressPair1 = UDPServerSocket1.recvfrom(bufferSize)
print("Mouse 1 Address Received")
bytesAddressPair2 = UDPServerSocket2.recvfrom(bufferSize)
print("Mouse 2 Address Received")
bytesAddressPair3 = UDPServerSocket3.recvfrom(bufferSize)
print("Mouse 3 Address Received")


message1 = bytesAddressPair1[0]
address1 = bytesAddressPair1[1]
message2 = bytesAddressPair2[0]
address2 = bytesAddressPair2[1]
message3 = bytesAddressPair3[0]
address3 = bytesAddressPair3[1]


clientMsg1 = "Message from Client1:{}".format(message1)
clientIP1  = "Client1 IP Address:{}".format(address1)
clientMsg2 = "Message from Client2:{}".format(message2)
clientIP2  = "Client2 IP Address:{}".format(address2)
clientMsg3 = "Message from Client3:{}".format(message3)
clientIP3  = "Client3 IP Address:{}".format(address3)

print(clientMsg1)
print(clientIP1)
print(clientMsg2)
print(clientIP2)
print(clientMsg3)
print(clientIP3)

# Get boundary corners
# bound## tuples' first value is the x-pos, second value is the y-pos
boundaries = getBoundaries()
bound00 = boundaries[0:2]
bound01 = boundaries[2:4]
bound10 = boundaries[4:6]
bound11 = boundaries[6:8]

# Calculate midpoints for quadrants (notice mid_3 and mid_2 switch for easier calculation)
mid_x = (bound00[0]+bound01[0]+bound10[0]+bound11[0])/4
mid_y = (bound00[1]+bound01[1]+bound10[1]+bound11[1])/4
mid_0 = ((bound00[0]+mid_x)/2,(bound00[1]+mid_y)/2)
mid_1 = ((bound01[0]+mid_x)/2,(bound01[1]+mid_y)/2)
mid_3 = ((bound10[0]+mid_x)/2,(bound10[1]+mid_y)/2)
mid_2 = ((bound11[0]+mid_x)/2,(bound11[1]+mid_y)/2)
mids = (mid_0, mid_1, mid_2, mid_3, mid_x, mid_y)

#Give time for mice to setup
time.sleep(5) 

# Listen for incoming datagrams

while(True): 
    #Get sound data

    #Get locations from apriltags

    #Calculate headings for both tracking robots and evading robot
    headingSet1 = util.getTrackerHeadings(x1, y1, x2, y2, soundData)
    headingSet2 = util.getEvaderHeading(x1, y1, x2, y2, x3, y3, mids)

    target_theta1 = headingSet1[0]
    target_v1 = headingSet1[1]
    target_theta2 = headingSet1[2]
    target_v2 = headingSet1[3]
    target_theta3 = headingSet2[0]
    target_v3 = headingSet2[1]

    #Creating Packet to Send to Mouse
    #First value sent is the cam theta, the second value is the target_theta, and the third value is the velocity
    offset_pack1 = struct.pack("fff", 0, target_theta1, target_v1)
    offset_pack2 = struct.pack("fff", 0, -target_theta2, target_v2)
    offset_pack3 = struct.pack("fff", 0, target_theta3, target_v3)

    UDPServerSocket1.sendto(offset_pack1, address1)
    UDPServerSocket2.sendto(offset_pack2, address2)
    UDPServerSocket3.sendto(offset_pack3, address3)

    time.sleep(5)