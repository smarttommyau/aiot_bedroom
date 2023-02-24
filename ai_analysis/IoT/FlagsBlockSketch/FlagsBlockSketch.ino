#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

ESP8266WebServer _esp8266WebServer(7777);
bool fan_state,light_state,buzzer_state;


void handleRoot() {
    _esp8266WebServer.send(200, "text/plain", String(u8"OK"));
}

void handleNotFound() {
    _esp8266WebServer.send(404, "text/plain", String(u8"err"));
}


void pin_control(const String control,uint8_t pin,bool &state) {
  if (control == String(u8"On")) {
    digitalWrite(pin, HIGH);
    state = true;
    _esp8266WebServer.send(200, u8"text/plain", String(u8"On"));
  } else if (control == String(u8"Off")) {
    digitalWrite(pin, LOW);
    state = false;
    _esp8266WebServer.send(200, u8"text/plain", String(u8"Off"));
  } else if (control == String("State")) {
    _esp8266WebServer.send(200, "text/plain", state?String(u8"On"):String(u8"Off"));
    
  }
}
void buzzer_control(const String freq,const String duration,uint8_t pin) {
  if(!isInt(freq) || !isInt(duration)) return;
  tone(pin,(unsigned int)freq.toInt(),toUnsignedLong(duration)==0?1000:toUnsignedLong(duration));
  _esp8266WebServer.send(200, u8"text/plain", String(u8"Ok"));
}
bool isInt(String tString) {
  String tBuf;
  boolean decPt = false;
  
  if(tString.charAt(0) == '-') tBuf = &tString[1];
  else tBuf = tString;  

  for(int x=0;x<tBuf.length();x++)
  {
    if(tBuf.charAt(x) < '0' || tBuf.charAt(x) > '9') return false;
  }
  return true;
}
unsigned long int toUnsignedLong(const String str){
  unsigned long int result = 0;
  for(int i=0;i<str.length();i++){
    result*=10;
    result += (str.charAt(i)-'0');
  }
  return result;
}
void web_reciever() {
  //logging
  Serial.print("Recieved a request from ");
  Serial.println(_esp8266WebServer.client().remoteIP().toString());
  if (_esp8266WebServer.hasArg(u8"fan")) {
    pin_control(_esp8266WebServer.arg(u8"fan"),D1,fan_state);
  }else if (_esp8266WebServer.hasArg(u8"light")) {
    pin_control(_esp8266WebServer.arg(u8"light"),D2,light_state);
  }else if (_esp8266WebServer.hasArg(u8"buzzer")) {
    buzzer_control(_esp8266WebServer.arg(u8"buzzer-freq"),_esp8266WebServer.arg(u8"buzzer-dur"),D3);
  }
}


// setup() will be run at first once
void setup() {
  Serial.begin(9600);

  //setup pin
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);
  pinMode(D3, OUTPUT);
  digitalWrite(D1, LOW);
  digitalWrite(D2, LOW);
  digitalWrite(D3, LOW);
  fan_state = false;
  light_state = false;
  //propmt serial to connect wifi
  Serial.println("Enter WIFIName:");
  while (Serial.available() == 0) {}
  String wifiname = Serial.readString();
  wifiname.trim();
  Serial.println("Enter WIFIPass:");
  while (Serial.available() == 0) {}
  String wifipass = Serial.readString();
  WiFi.begin(wifiname, wifipass);
  while(WiFi.isConnected() == false) {
    delay(1);
    Serial.print(".");
  }
  Serial.println("WiFi Connected");
  _esp8266WebServer.on("/", handleRoot);
  _esp8266WebServer.onNotFound(handleNotFound);
  _esp8266WebServer.begin();
  _esp8266WebServer.on("/controller", HTTP_GET, web_reciever);//set web_reciever as the handler of /controller 
  Serial.println((WiFi.localIP().toString())); // print the ip to pc
  

}

// loop() will run forever
void loop() {
  _esp8266WebServer.handleClient();

}
