import socket
import struct
import time

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

#Give time for mice to setup
time.sleep(5) 


# Listen for incoming datagrams

while(True): 
    #time.sleep(5)
    #Creating Packet to Send to Mouse
    #First value sent is the cam theta, the second value is the target_theta, and the third value is the velocity
    offset_pack1 = struct.pack("fff", 0, target_theta, target_v)
    offset_pack2 = struct.pack("fff", 0, -target_theta, target_v)
    offset_pack3 = struct.pack("fff", 0, target_theta, target_v)

    UDPServerSocket1.sendto(offset_pack1, address1)
    UDPServerSocket2.sendto(offset_pack2, address2)
    UDPServerSocket3.sendto(offset_pack3, address3)

    time.sleep(5)
    target_theta = -1.5
    target_v = 0.4