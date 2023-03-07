/*
 *  This sketch sends random data over UDP on a ESP32 device
 *
 */
#include <WiFi.h>
#include <WiFiUdp.h>
#include <string.h>
#include <iostream>

// WiFi network name and password:
const char * networkName = "408ITerps";
const char * networkPswd = "goterps2022";
char pbuff[255];

// IP address to send UDP data to:
// either use the ip address of the server or 
// a network broadcast address
const char * udpAddress = "192.168.2.102";
const int udpPort = 3333;

// Are we currently connected?
boolean connected = false;

// The udp library class
WiFiUDP udp;

// Wifi event handler
void WiFiEvent(WiFiEvent_t event){
    switch(event) {
      case ARDUINO_EVENT_WIFI_STA_GOT_IP:
          //When connected set 
          Serial.print("WiFi connected! IP address: ");
          Serial.println(WiFi.localIP());  
          //initializes the UDP state
          //This initializes the transfer buffer
          udp.begin(WiFi.localIP(),udpPort);
          connected = true;
          break;
      case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
          Serial.println("WiFi lost connection");
          connected = false;
          break;
      default: break;
    }
}

void connectToWiFi(const char * ssid, const char * pwd){
  Serial.println("Connecting to WiFi network: " + String(ssid));

  // delete old config
  WiFi.disconnect(true);
  //register event handler
  WiFi.onEvent(WiFiEvent);
  
  //Initiate connection
  WiFi.begin(ssid, pwd);

  Serial.println("Waiting for WIFI connection...");
}

void setup(){
  // Initilize hardware serial:
  Serial.begin(115200);
  
  // Stop the right motor by setting pin 14 low
  // this pin floats high or is pulled
  // high during the bootloader phase for some reason
  pinMode(14, OUTPUT);
  digitalWrite(14, LOW);
  delay(100);

  //Connect to the WiFi network
  connectToWiFi(networkName, networkPswd);

  //Send a packet
  udp.beginPacket(udpAddress, udpPort);
  udp.printf("Hi Jetson");
  udp.endPacket();
}

void loop(){
  //only send data when connected
  if(connected){
    //Send a packet
    udp.beginPacket(udpAddress,udpPort);
    udp.printf("Seconds since boot: %lu", millis()/1000);
    udp.endPacket();
  }
  //Wait for 1 second
  delay(100);

  int packetSize = udp.parsePacket();
    if(packetSize >= sizeof(float))
    {
      Serial.printf("packet size is %d\n", packetSize);
      float my_array[1]; 
      udp.read((char*)my_array, sizeof(my_array)); 
      udp.flush();
      Serial.printf("received value is %f\n", my_array[0]);
      float target = my_array[0];
      Serial.printf("target is %f\n", target);
    }
}