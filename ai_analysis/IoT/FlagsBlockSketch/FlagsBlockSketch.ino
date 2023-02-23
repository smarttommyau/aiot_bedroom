// Flag's Block 產生的草稿碼

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
//#include "data/webpages.h"

ESP8266WebServer _esp8266WebServer(7777);
bool fan_state;

void handleRoot() {
    _esp8266WebServer.send(200, "text/plain", String(u8"OK"));
//#ifndef WEBPAGE_IN_PROGMEM
//  _esp8266WebServer.send(200, "text/html", mainPage);
//#else
//  _esp8266WebServer.send_P(200, PSTR("text/html"), mainPage);
//#endif
}

void handleNotFound() {
    _esp8266WebServer.send(404, "text/plain", String(u8"err"));
//#ifndef WEBPAGE_IN_PROGMEM
//  _esp8266WebServer.send(404, "text/html", errorPage);
//#else
//  _esp8266WebServer.send_P(404, PSTR("text/html"), errorPage);
//#endif
}


void fan_control(const String control) {
  if (control == String(u8"On")) {
    digitalWrite(D1, HIGH);
    fan_state = true;
    _esp8266WebServer.send(200, u8"text/plain", String(u8"OK"));
  } else if (control == String(u8"Off")) {
    digitalWrite(D1, LOW);
    fan_state = false;
  } else if (control == String("State")) {
    _esp8266WebServer.send(200, "text/plain", fan_state?String(u8"On"):String(u8"Off"));
    
  }
}

void web_reciever() {
  if (_esp8266WebServer.hasArg(u8"fan")) {
    fan_control(_esp8266WebServer.arg(u8"fan"));
  }
}


// setup() will be run at first once
void setup() {
  Serial.begin(9600);

  //setup pin
  pinMode(D1, OUTPUT);
  digitalWrite(D1, LOW);
  fan_state = false;
  
  WiFi.begin(u8"", u8"");
  _esp8266WebServer.on("/", handleRoot);
  _esp8266WebServer.onNotFound(handleNotFound);
//  _esp8266WebServer.on("/setting", handleSetting);
  _esp8266WebServer.begin();
  _esp8266WebServer.on("/controller", HTTP_GET, web_reciever);//set web_reciever as the handler of /controller 
  Serial.println((WiFi.localIP().toString())); // print the ip to pc
  

}

// loop() will run forever
void loop() {
  _esp8266WebServer.handleClient();

}
