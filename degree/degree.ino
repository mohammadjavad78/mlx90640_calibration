#define sensorPin A0

void setup() {
  Serial.begin(9600);
}

void loop() {
  int n=5;
  int reading;
  float voltage;
  float temperature;
  
  String s1 = Serial.readString();
  Serial.print("Received Data => \n");
//  Serial.print(s1);
  if(s1=="read\n"||s1=="read")
  {
    float a=0;
    for(int i=0;i<n;i++)
    {
      reading = analogRead(sensorPin);
      voltage = reading * (5000 / 1024.0);
      temperature = voltage / 10;
      a+=temperature;
    }
    a=a/n;
    Serial.print(a);
    Serial.print(" \xC2\xB0");
    Serial.println("C");
  }
  delay(1000);
}
