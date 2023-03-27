//Imports
#include <WiFi.h>
#include <WifiUDP.h>
#include <string.h>
#include <iostream>

class UDPClient{
        const char * udpAddress = "192.168.2.102";
        int udpPort;
        boolean connected = false;
        WiFiUDP udp;

    public:
        UDPClient(int port);
        void setup();
        float * getPacket();
}