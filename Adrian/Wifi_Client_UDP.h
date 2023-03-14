//Imports
#include <WifiUDP.h>
#include <string.h>
#include <iostream>

class UDPClient{
    private:
        const char * udpAddress;
        int udpPort;
        boolean connected;
        WifiUDP udp;
        void WiFiEvent(WiFiEvent_t event);
        void connectToWiFi(const char * ssid, const char * pwd);

    public:
        UDPClient(int port);
        void setup();
        int[] getPacket();
}