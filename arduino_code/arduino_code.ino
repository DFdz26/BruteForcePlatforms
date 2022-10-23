#include <SoftwareSerial.h>
#include "src/bruteForcePlatform/bruteForcePlatform.h"

//#define PRINT_DEBUG
#define MAX_SIZE_BUFFER_IN 30
//#define MOVE_CONTINUES
//#define SERIAL_DEBUG
#define LOADING_DELAY 5000
#define DELAY_NEXT_FREE_PACKET 10000
#define TOP_FILTER_MOV_5 200
#define LOW_FILTER_MOV_5 10

#ifdef SERIAL_DEBUG
SoftwareSerial xbee(2,3);
#endif

PlatformsBruteForce platform;

unsigned long starting_time = millis();
bool resend_im_free_pack = false;
unsigned long start_time_delay_pack = 0;
float random_number_delay = 0;
int ant_code = 0;

#ifdef SERIAL_DEBUG
const int pump1 = 4;
const int pump2 = 7;
#else
const int pump1 = 2;
const int pump2 = 3;
#endif
const int pump3 = 5;
const int pump4 = 6;

const int valve1 = 8;
const int valve2 = 11;   
const int valve3 = 10;
const int valve4 = 9;
const long int inflation_time_move_4 = 25000; //***Changed by Jonas 8-7-22 from 15000
const long int inflation_time_move_5 = 75000; //***Changed by Jonas 8-7-22 from 40000
bool req_pack_in_4_5 = false;

//Data points from "Feeding the Algorithm performance" (2020)
float data2[13] = {7.98, 11.90, 12.00, 13.70, 11.85, 15.70, 10.90, 16.75, 15.67, 10.05, 11.55, 10.82, 11.35,}; //Duration (mins decimals) for class 0

void setup() {
  Serial.begin(9600);
#ifdef SERIAL_DEBUG
  xbee.begin(9600);
  Serial.println("Started, let's wait a bit until everything is set up.");
#endif
  
  randomSeed(analogRead(0));

  pinMode(valve1, OUTPUT);
  pinMode(valve2, OUTPUT);
  pinMode(valve3, OUTPUT);
  pinMode(valve4, OUTPUT);
  
  pinMode(pump1, OUTPUT);
  pinMode(pump2, OUTPUT);
  pinMode(pump3, OUTPUT);
  pinMode(pump4, OUTPUT);
  
  platform.loadCommunicationFunction(receiving_data,sending_data);
  platform.loadDebugger(debugFunction);
  
  delay(LOADING_DELAY);
  platform.getXbeeID();

  starting_time = millis();
}
  
void loop() {

  if (((DELAY_NEXT_FREE_PACKET + start_time_delay_pack + random_number_delay) < get_actualTime()) && (resend_im_free_pack)) {
    resend_im_free_pack = false;
    platform.SendFreePacket();
  }

  int code = platform.run(get_actualTime());

#ifdef MOVE_CONTINUES
  switch(platform.GetActiveMovement()) {
        case 0:
#ifdef SERIAL_DEBUG
          Serial.println("Stopped");
#endif
          break;
        case 1:
#ifdef SERIAL_DEBUG
          Serial.println("1st movement");
#endif
          platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
           Serial.println("Deflating....");
#endif
          deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
#ifdef SERIAL_DEBUG
          Serial.println("Moving....");
#endif
          preProgrammedMovement1();
#ifdef SERIAL_DEBUG
          Serial.println("Finished");
#endif
          platform.SendFreePacket();
          random_number_delay = random(0, 50) / 10;
          start_time_delay_pack = get_actualTime();
          resend_im_free_pack = true;
          break;
      
      case 2:
#ifdef SERIAL_DEBUG
          Serial.println("2nd movement");
#endif
          platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
           Serial.println("Deflating....");
#endif
          deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
#ifdef SERIAL_DEBUG
          Serial.println("Moving....");
#endif
          preProgrammedMovement2(); 
#ifdef SERIAL_DEBUG
          Serial.println("Finished");
#endif
          platform.SendFreePacket();
          random_number_delay = random(0, 50) / 10;
          start_time_delay_pack = get_actualTime();
          resend_im_free_pack = true;
          break;
      case 3:
#ifdef SERIAL_DEBUG
          Serial.println("3rd movement");
#endif
          platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
           Serial.println("Deflating....");
#endif
          deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
#ifdef SERIAL_DEBUG
          Serial.println("Moving....");
#endif
          preProgrammedMovement3(); 
#ifdef SERIAL_DEBUG
          Serial.println("Finished");
#endif
          platform.SendFreePacket();
          random_number_delay = random(0, 50) / 10;
          start_time_delay_pack = get_actualTime();
          resend_im_free_pack = true;
          break;
      case 4:
#ifdef SERIAL_DEBUG
              Serial.println("4th movement");
#endif
              platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
              Serial.println("Deflating....");
#endif
              deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
#ifdef SERIAL_DEBUG
              Serial.println("Moving....");
#endif
              dataMove2(inflation_time_move_4);
#ifdef SERIAL_DEBUG
              Serial.println("Finished");
#endif
              platform.SendFreePacket();
              random_number_delay = random(0, 50) / 10;
              start_time_delay_pack = get_actualTime();
              resend_im_free_pack = true;
              break;
      case 5:
#ifdef SERIAL_DEBUG
              Serial.println("5th movement");
#endif
              platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
              Serial.println("Deflating....");
#endif
              deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
#ifdef SERIAL_DEBUG
              Serial.println("Moving....");
#endif
              dataMove1(0, 0, 0, inflation_time_move_5);
#ifdef SERIAL_DEBUG
              Serial.println("Finished");
#endif
              platform.SendFreePacket();
              random_number_delay = random(0, 50) / 10;
              start_time_delay_pack = get_actualTime();
              resend_im_free_pack = true;
              break;
      case 6:
#ifdef SERIAL_DEBUG
              Serial.println("6th movement");
#endif
              platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
              Serial.println("Deflating....");
#endif
              deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
#ifdef SERIAL_DEBUG
              Serial.println("Moving....");
#endif
              dataMove3short();
#ifdef SERIAL_DEBUG
              Serial.println("Finished");
#endif
              platform.SendFreePacket();
              random_number_delay = random(0, 50) / 10;
              start_time_delay_pack = get_actualTime();
              resend_im_free_pack = true;
              break;
      case 254:
          platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
          Serial.println("deflating platforms");
#endif
          deflateAllSimul(120000, true);
          delay(30000);
          platform.SendFreePacket();
          random_number_delay = random(0, 50) / 10;
          start_time_delay_pack = get_actualTime();
          resend_im_free_pack = true;
          break;
      case 255:
          platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
          Serial.println("deflating platforms");
#endif
          deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
          platform.SendFreePacket();
          random_number_delay = random(0, 50) / 10;
          start_time_delay_pack = get_actualTime();
          resend_im_free_pack = true;
          break;          
      default:
#ifdef SERIAL_DEBUG
        Serial.println("Other movement");
#endif
        break;
    }
#else
  if (code != ant_code) {
#ifdef SERIAL_DEBUG
    Serial.print("Protocol code (for debugging):  ");
    Serial.println(code);
#endif
    ant_code = code;
    
    if (code == PlatformsBruteForce::PLATFORM_MESS_RECEIVED) {    
      switch(platform.GetActiveMovement()) {
          case 0:
#ifdef SERIAL_DEBUG
              Serial.println("Stopped");
#endif
              platform.SendFreePacket();
              break;
          case 1:
#ifdef SERIAL_DEBUG
              Serial.println("1st movement");
#endif
              platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
              Serial.println("Deflating....");
#endif
              deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
#ifdef SERIAL_DEBUG
              Serial.println("Moving....");
#endif
              preProgrammedMovement1();
#ifdef SERIAL_DEBUG
              Serial.println("Finished");
#endif
              platform.SendFreePacket();
              random_number_delay = random(0, 50) / 10;
              start_time_delay_pack = get_actualTime();
              resend_im_free_pack = true;
              break;

          case 2:
#ifdef SERIAL_DEBUG
              Serial.println("2nd movement");
#endif
              platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
              Serial.println("Deflating....");
#endif
              deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
#ifdef SERIAL_DEBUG
              Serial.println("Moving....");
#endif
              preProgrammedMovement2();
#ifdef SERIAL_DEBUG
              Serial.println("Finished");
#endif
              platform.SendFreePacket();
              random_number_delay = random(0, 50) / 10;
              start_time_delay_pack = get_actualTime();
              resend_im_free_pack = true;
              break;
          case 3:
#ifdef SERIAL_DEBUG
              Serial.println("3rd movement");
#endif
              platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
              Serial.println("Deflating....");
#endif
              deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
#ifdef SERIAL_DEBUG
              Serial.println("Moving....");
#endif
              preProgrammedMovement3();
#ifdef SERIAL_DEBUG
              Serial.println("Finished");
#endif
              platform.SendFreePacket();
              random_number_delay = random(0, 50) / 10;
              start_time_delay_pack = get_actualTime();
              resend_im_free_pack = true;
              break;
          case 4:
#ifdef SERIAL_DEBUG
              Serial.println("4th movement");
#endif
              platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
              Serial.println("Deflating....");
#endif
              deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
#ifdef SERIAL_DEBUG
              Serial.println("Moving....");
#endif
              dataMove2(inflation_time_move_4);
#ifdef SERIAL_DEBUG
              Serial.println("Finished");
#endif
              platform.SendFreePacket();
              random_number_delay = random(0, 50) / 10;
              start_time_delay_pack = get_actualTime();
              resend_im_free_pack = true;
              break;
          case 5:
#ifdef SERIAL_DEBUG
              Serial.println("5th movement");
#endif
              platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
              Serial.println("Deflating....");
#endif
              deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
#ifdef SERIAL_DEBUG
              Serial.println("Moving....");
#endif
              dataMove1(0, 0, 0, inflation_time_move_5);
#ifdef SERIAL_DEBUG
              Serial.println("Finished");
#endif
              platform.SendFreePacket();
              random_number_delay = random(0, 50) / 10;
              start_time_delay_pack = get_actualTime();
              resend_im_free_pack = true;
              break;
          case 6:
#ifdef SERIAL_DEBUG
              Serial.println("6th movement");
#endif
              platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
              Serial.println("Deflating....");
#endif
              deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
#ifdef SERIAL_DEBUG
              Serial.println("Moving....");
#endif
              dataMove3short();
#ifdef SERIAL_DEBUG
              Serial.println("Finished");
#endif
              platform.SendFreePacket();
              random_number_delay = random(0, 50) / 10;
              start_time_delay_pack = get_actualTime();
              resend_im_free_pack = true;
              break;
        case 254:
            platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
            Serial.println("deflating platforms");
#endif
            deflateAllSimul(120000, true);
            delay(30000);
            platform.SendFreePacket();
            random_number_delay = random(0, 50) / 10;
            start_time_delay_pack = get_actualTime();
            resend_im_free_pack = true;
            break;
        case 255:
              platform.SendBusyPacket();
#ifdef SERIAL_DEBUG
              Serial.println("deflating platforms");
#endif
              deflateAllSimul(30000, true); //Deflates all chambers for 30s as a security measure before initiating inflation (the robot code should always start with this)
              platform.SendFreePacket();
              random_number_delay = random(0, 50) / 10;
              start_time_delay_pack = get_actualTime();
              resend_im_free_pack = true;
              break;
        default:
#ifdef SERIAL_DEBUG
              Serial.println("Other movement");
#endif
              break;
      }
    }
  }
#endif
  delay(100);
}


void protruder(int infTime){
  int randChamber=random(1,3+1);

  if (randChamber==1){
      digitalWrite(pump1, HIGH);    
      digitalWrite(valve1, LOW);
      delay(infTime);
      digitalWrite(pump1, LOW);    
      }

  if (randChamber==2){
      digitalWrite(pump2, HIGH);    
      digitalWrite(valve2, LOW);
      delay(infTime);
      digitalWrite(pump2, LOW);    
      }
      
  if (randChamber==3){
      digitalWrite(pump3, HIGH);    
      digitalWrite(valve3, LOW);
      delay(infTime);
      digitalWrite(pump3, LOW);
      }
  }


void preProgrammedMovement1(){ //This is the second part of the long complete sequence that was used for the Ars Electronica Festical exhibition 2021 (one chamber inflates)

  long startValue;
  long selector;
  long pauseTime;
  long randOrder;
  
  
  rapidInflateOneAtATime(4000, 40, 0);
  
  protruder(27000); 
  
  long randyTime=random(4000,8000);
  pauseClosedValves(randyTime);
  
  deflateAllSimul(40000, true);

//******************

}

void preProgrammedMovement2(){ //This is the first part of the long complete sequence that was used for the Ars Electronica Festical exhibition 2021 (all chambers inflate)

  long startValue;
  long selector;
  long pauseTime;
  long randOrder;

  PlatformsBruteForce::data_movement_t argMov[MAX_ITERATIONS_IN_3RD_MOVEMENT];
  
  platform.CopyMovesArgument(argMov, MAX_ITERATIONS_IN_3RD_MOVEMENT);
  
  rapidInflateOneAtATime(4000, 40, 0);
  
  //***dataMove3******
  for (uint8_t i = 0; i < 3; i++) {
    dataMove3(argMov[i].inflation_time, argMov[i].chamber, argMov[i].iterations);
  }
  
  deflateAllSimul(40000, true);
  
  //******************
  
}



void preProgrammedMovement3(){ //This is the long complete sequence that was used for the Ars Electronica Festical exhibition 2021

  long startValue;
  long selector;
  long pauseTime;
  long randOrder;
  PlatformsBruteForce::data_movement_t argMov[MAX_ITERATIONS_IN_3RD_MOVEMENT];
  
  rapidInflateOneAtATime(4000, 40, 0);
  
  for (int i=0; i<4; i++){ //Run 4 times
    
    platform.CopyMovesArgument(argMov, MAX_ITERATIONS_IN_3RD_MOVEMENT);
#ifdef SERIAL_DEBUG
    printMovArgs(argMov);
#endif
    //***dataMove3******
    for (uint8_t i = 0; i < MAX_ITERATIONS_IN_3RD_MOVEMENT; i++) {
      dataMove3(argMov[i].inflation_time, argMov[i].chamber, argMov[i].iterations);
    }
    
    if ((i+1) < 4){
#ifdef SERIAL_DEBUG
      Serial.println("I will ask the next data to master.");
#endif
      platform.SendMoveReqPacket(get_actualTime());
    }
    
    deflateAllSimul(4000, true);
    
    protruder(27000); 
    
    long randyTime=random(4000,8000);
    pauseClosedValves(randyTime);
    deflateAllSimul(20000,true);

#ifdef SERIAL_DEBUG
    if((i+1) < 4) Serial.println("While I was waiting I received: ");
#endif
    
  }

#ifdef SERIAL_DEBUG
  Serial.println("Now a big pause");
#endif
  //***PAUSE*********
  deflateAllSimul(100,false);
  selector = random(0, 12+1); //Random number from 0 to 14
  pauseTime= data2[selector]; //~100 
  pauseTime= pauseTime*60*1000/3; // Pause time range 8-17 mins. => 2.3 mins - 5.6 mins.
#ifdef SERIAL_DEBUG
  Serial.print("pauseTime=");
  Serial.println(pauseTime);
#endif
  
  deflateAllSimul(120000,false);
  delay(pauseTime-120000);
  
  //******************


}


void dataMove3(int infaltionTime, uint8_t chamber, uint8_t iterations){ //
//DESCRIPTION:  Two chambers take turns in inflating (a kind of dialogue between the two perhaps) (similar to Video #2).

  infaltionTime = checkInflationTime(infaltionTime, 25000, 5000);
#ifdef SERIAL_DEBUG
  Serial.println("dataMove3()");
#endif

  int randJitter= random(3);
  int randSeg(6,10);

  if (randJitter==0) {
    rapidInflateOneAtATimeJitter(500, randSeg, 1);
    rapidInflateOneAtATime(1000, 40, 0);
  } 
  else {
    rapidInflateOneAtATime(1500, 40, 0);
  }

  digitalWrite(valve4, HIGH); //Open skin layer air inlet
    for (uint8_t i = 0; i < iterations; i++) {
      movement2(infaltionTime, chamber%3);
    
    }
    //Comment: Would be cool to also integrate more rapid shifts, as the valves make clicking noise that can be used as an element to generate a sensation of rapid movements/higher arousal
}



void movement2(long inflationTime, int startChamber) { //Two chambers take turns in inflating and deflating
  
  //1. Inflates first hill and releases second
  //2. inflates second hill and deflates first hill (possibly goes to 1.)

//"inflationTime" must be between 5000 to 25000

  digitalWrite(valve1, LOW);
  digitalWrite(valve2, LOW);
  digitalWrite(valve3, LOW);
  digitalWrite(valve4, LOW);

 if (startChamber==0){
  digitalWrite(valve3, HIGH);
  
  //1. Inflates first hill
  digitalWrite(valve2, HIGH);
  digitalWrite(valve1, LOW);
  digitalWrite(pump1, HIGH); 
  delay(inflationTime);
  digitalWrite(pump1, LOW);  

  //2. inflates second hill and deflates first hill
  digitalWrite(valve1, HIGH);
  digitalWrite(valve2, LOW);
  digitalWrite(pump2, HIGH); 
  delay(inflationTime);
  digitalWrite(pump2, LOW);  
  }


 if (startChamber==1){
  digitalWrite(valve1, HIGH);
  
  //1. Inflates first hill
  digitalWrite(valve3, HIGH);
  digitalWrite(valve2, LOW);
  digitalWrite(pump2, HIGH); 
  delay(inflationTime);
  digitalWrite(pump2, LOW);  

  //2. inflates second hill and deflates first hill
  digitalWrite(valve2, HIGH);
  digitalWrite(valve3, LOW);
  digitalWrite(pump3, HIGH); 
  delay(inflationTime);
  digitalWrite(pump3, LOW);  
  }



 if (startChamber==2){
  digitalWrite(valve2, HIGH);
  
  //1. Inflates first hill
  digitalWrite(valve1, HIGH);
  digitalWrite(valve3, LOW);
  digitalWrite(pump3, HIGH); 
  delay(inflationTime);
  digitalWrite(pump3, LOW);  

  //2. inflates second hill and deflates first hill
  digitalWrite(valve3, HIGH);
  digitalWrite(valve1, LOW);
  digitalWrite(pump1, HIGH); 
  delay(inflationTime);
  digitalWrite(pump1, LOW);  
  }
  
}

  
void rapidInflateOneAtATimeJitter(long totInflateTime, int segment, bool jitterOn) { //Duration: totInflateTime*3

 
  int n = totInflateTime/segment;
  int randomnumber;

#ifdef SERIAL_DEBUG
  Serial.print("Rapid inflate (Jitter), wait ");
  Serial.print("3*");
  Serial.print(totInflateTime);
  Serial.println("ms.");
#endif
  
  for (int i=0; i<=n; i++){
  
  randomnumber = random(10); //Random number from 0 to 2
  if (randomnumber==0) digitalWrite(valve4, HIGH); //JITTER 

  digitalWrite(valve1, LOW);
  digitalWrite(pump1, HIGH);  
  delay(segment);
  digitalWrite(pump1, LOW);  
  
  digitalWrite(valve4, LOW);  //JITTER
  randomnumber = random(10); //Random number from 0 to 2
  if (randomnumber==0) digitalWrite(valve4, HIGH); //JITTER 

  digitalWrite(valve2, LOW);
  digitalWrite(pump2, HIGH);  
  delay(segment);
  digitalWrite(pump2, LOW);  

  digitalWrite(valve4, LOW);  //JITTER
  randomnumber = random(10); //Random number from 0 to 2
  if (randomnumber==0) digitalWrite(valve4, HIGH); //JITTER 

  digitalWrite(valve3, LOW);
  digitalWrite(pump3, HIGH);  
  delay(segment);
  digitalWrite(pump3, LOW); 

  digitalWrite(valve4, LOW);  //JITTER
  randomnumber = random(10); //Random number from 0 to 2
  if (randomnumber==0) digitalWrite(valve4, HIGH); //JITTER 

  digitalWrite(valve4, LOW);
  digitalWrite(pump4, HIGH);  
  delay(segment);
  digitalWrite(pump4, LOW); 
  
    digitalWrite(valve4, LOW);  //JITTER

   }
  }



void rapidInflateOneAtATime(long totInflateTime, int segment, bool jitterOn) { //Duration: totInflateTime*3
  
  int n = totInflateTime/segment;
#ifdef SERIAL_DEBUG
  Serial.print("Rapid inflate, wait ");
  Serial.print("3*");
  Serial.print(totInflateTime);
  Serial.print("ms.");
#endif

  for (int i=0; i<=n; i++){
  digitalWrite(valve1, LOW);
  digitalWrite(pump1, HIGH);  
  delay(segment);
  digitalWrite(pump1, LOW);  
 
  digitalWrite(valve2, LOW);
  digitalWrite(pump2, HIGH);  
  delay(segment);
  digitalWrite(pump2, LOW);  


  digitalWrite(valve3, LOW);
  digitalWrite(pump3, HIGH);  
  delay(segment);
  digitalWrite(pump3, LOW); 


  digitalWrite(valve4, LOW);
  digitalWrite(pump4, HIGH);  
  delay(segment);
  digitalWrite(pump4, LOW); 
   }
  }


void testOneAtATime() {

  digitalWrite(valve1, HIGH);
  delay(1000);
  digitalWrite(valve1, LOW);
  delay(1000);
  digitalWrite(valve2, HIGH);
  delay(1000);
  digitalWrite(valve2, LOW);
  delay(1000);
  digitalWrite(valve3, HIGH);
  delay(1000);
  digitalWrite(valve3, LOW);
  delay(1000);
  digitalWrite(valve4, HIGH);
  delay(1000);
  digitalWrite(valve4, LOW);
  delay(1000);


  digitalWrite(pump1, HIGH);
  delay(1000);
  digitalWrite(pump1, LOW);
  delay(1000);
  digitalWrite(pump2, HIGH);
  delay(1000);
  digitalWrite(pump2, LOW);
  delay(1000);
  digitalWrite(pump3, HIGH);
  delay(1000);
  digitalWrite(pump3, LOW);
  delay(1000);
  digitalWrite(pump4, HIGH);
  delay(1000);
  digitalWrite(pump4, LOW);
  delay(1000);
}

bool deflateAllSimul(long deflateTimeAll, bool checkMess) {
  bool rc = false;
  
  digitalWrite(pump1, LOW);  
  digitalWrite(pump2, LOW);  
  digitalWrite(pump3, LOW);
  digitalWrite(pump4, LOW);  

  digitalWrite(valve1, HIGH);
  digitalWrite(valve2, HIGH);
  digitalWrite(valve3, HIGH);
  digitalWrite(valve4, HIGH);

#ifdef SERIAL_DEBUG
  Serial.print("Wait ");
  Serial.print(deflateTimeAll);
  Serial.println("ms until I deflate the platform");
#endif
  if (checkMess) {
#ifdef SERIAL_DEBUG
    Serial.println("I will check if there's a message from the master and replay if needed");
#endif
    rc = DelayRunPlatform(deflateTimeAll);
  } else {
    delay(deflateTimeAll);
  }
  
  digitalWrite(valve1, LOW);
  digitalWrite(valve2, LOW);
  digitalWrite(valve3, LOW);
  digitalWrite(valve4, LOW);

  return rc;
}

void dataMove3short(){ //
//DESCRIPTION:  One chamber inflates followed by a second chamber (no jitter with valves)

//   Serial.println("dataMove3short()");

  rapidInflateOneAtATime(1500, 40, 0);


  int segment1; //~100
  int segment2; //~100
  long int inflationTime = 5000;
  PlatformsBruteForce::raw_data_t rawData[MAX_ITERATIONS_IN_3RD_MOVEMENT];

  platform.CopyRawMessage(rawData, MAX_ITERATIONS_IN_3RD_MOVEMENT);
  
  digitalWrite(valve4, HIGH); //Open skin layer air inlet

  segment1 = rawData[0].first + 1; // Added 1 to prevent zero value
  segment2 = rawData[0].second + 1;

  //  inflationTime = segment1 * 66 + 1000; //***Changed by Jonas 8-7-22 from "= segment1 * 44 + 1000"
  inflationTime = 80000;//***Changed by Jonas 8-7-22
  inflationTime %= 25000;

  if (inflationTime < 5000) inflationTime = 5000;

  movement2(inflationTime, segment2 % 3); // [inflation time, chamber] "inflationTime" must be between 5000 to 25000. "%" calculates modulus (the remainder upon division)
  
  deflateAllSimul(40000, false);
}


void movement1(long inflationTime, bool wait_and_communicate) { //Round of hills
//Function used by dataMove2()
  
  //1. Inflates first hill and releases third
  //2. inflates second hill and deflates first hill
  //3. inflates third hill and deflates second hill
  //4. Deflates third hill (possibly call function again to repeat from 1.)

//"inflationTime" must be between 5000 to 25000

  digitalWrite(valve1, LOW);
  digitalWrite(valve2, LOW);
  digitalWrite(valve3, LOW);
  digitalWrite(valve4, LOW);

  //1. Inflates first hill
  digitalWrite(valve3, HIGH);
  digitalWrite(valve1, LOW);
  digitalWrite(pump1, HIGH); 
  delay(inflationTime);
  digitalWrite(pump1, LOW);  

  //2. inflates second hill and deflates first hill
  digitalWrite(valve1, HIGH);
  digitalWrite(valve2, LOW);
  digitalWrite(pump2, HIGH); 
  delay(inflationTime);
  digitalWrite(pump2, LOW);  

  
  //3. inflates third hill and deflates second hill
  digitalWrite(valve2, HIGH);
  digitalWrite(valve3, LOW);
  digitalWrite(pump3, HIGH); 
  delay(inflationTime);
  digitalWrite(pump3, LOW);  
 
  }

void dataMove2(long totInflateTime){
//DESCRIPTION: Each chamber inflated in turn in circular motion (similar to Video #1)
//  Serial.println("dataMove2()");

  //long totInflateTime = 120000; //27000 max
  long iterInflatedTime = 0;
  long inflationTime = 0;
  uint8_t i = 0;
  uint8_t max_i = 3;
  PlatformsBruteForce::raw_data_t rawData[MAX_ITERATIONS_IN_3RD_MOVEMENT];
  if (!req_pack_in_4_5) {
      platform.CopyRawMessage(rawData, MAX_ITERATIONS_IN_3RD_MOVEMENT);
  }

  while (iterInflatedTime < totInflateTime){

    if ((i == 0) && (req_pack_in_4_5)) {
        platform.CopyRawMessage(rawData, MAX_ITERATIONS_IN_3RD_MOVEMENT);
    }
    
    inflationTime = (rawData[i].first + 1) * 200; //***Changed by Jonas 8-7-22 from 100
    movement1(inflationTime, false);
    iterInflatedTime += inflationTime;

    inflationTime = (rawData[i].second + 1) * 200;//***Changed by Jonas 8-7-22 from 100
    movement1(inflationTime, false);
    iterInflatedTime += inflationTime;

    inflationTime = (rawData[i].third + 1) * 200;//***Changed by Jonas 8-7-22 from 100
    movement1(inflationTime, ((max_i - 1) == i) && (req_pack_in_4_5));
    iterInflatedTime += inflationTime;

    i++;
    i %= max_i;
  }
  
  deflateAllSimul(40000, false);

}


void dataMove1(bool skinLayerAirIn, bool skinLayerPumpOn, bool erraticClicks, long totInflateTime){
//DESCRIPTION:
//Maja's suggestion
//Each chamber is in turn inflated with a tiny amount of air based on data (similar to Video #3)
// Serial.println("dataMove1()");

  int segment1; //~100
  int segment2; //~100
  int segment3; //

  int startColum=1;
  long inflatedTime=0;
  PlatformsBruteForce::raw_data_t rawData[MAX_ITERATIONS_IN_3RD_MOVEMENT];

  if (!req_pack_in_4_5) {
      platform.CopyRawMessage(rawData, MAX_ITERATIONS_IN_3RD_MOVEMENT);
  }

  digitalWrite(valve4, LOW); //Close skin layer air inlet

  while (inflatedTime < totInflateTime){

      if (req_pack_in_4_5) {
          platform.CopyRawMessage(rawData, MAX_ITERATIONS_IN_3RD_MOVEMENT);
      }
  
      //First round of data inflations
      segment1 = rawData[0].first + 1; //~100
      segment2 = rawData[0].second + 1; //~100
      segment3 = rawData[0].third + 1; //


      if (skinLayerAirIn==1){digitalWrite(valve4, HIGH);}//Let air into skin layer
      if (skinLayerPumpOn==1){digitalWrite(pump4, HIGH);}

      digitalWrite(valve1, LOW);
      digitalWrite(pump1, HIGH);
      segment1 = delay_inflation_mov_5(segment1, TOP_FILTER_MOV_5, LOW_FILTER_MOV_5);
//       delay(segment1);
      inflatedTime=inflatedTime+segment1;
      digitalWrite(pump1, LOW);

      segment3 = delay_inflation_mov_5(segment3, TOP_FILTER_MOV_5, LOW_FILTER_MOV_5);
      inflatedTime=inflatedTime+segment3;

      digitalWrite(valve2, LOW);
      digitalWrite(pump2, HIGH);
      segment2 = delay_inflation_mov_5(segment2, TOP_FILTER_MOV_5, LOW_FILTER_MOV_5);
      inflatedTime=inflatedTime+segment2;
      digitalWrite(pump2, LOW);

      segment3 = delay_inflation_mov_5(segment3, TOP_FILTER_MOV_5, LOW_FILTER_MOV_5);
      inflatedTime=inflatedTime+segment3;


      digitalWrite(pump4, LOW);

    //Second round of data inflations

      segment1 = rawData[1].first + 1; //~100
      segment2 = rawData[1].second + 1; //~100
      segment3 = rawData[1].third + 1; //

      digitalWrite(valve3, LOW);
      digitalWrite(pump3, HIGH);
      segment1 = delay_inflation_mov_5(segment1, TOP_FILTER_MOV_5, LOW_FILTER_MOV_5);
      inflatedTime=inflatedTime+segment1;
      digitalWrite(pump3, LOW);

      segment3 = delay_inflation_mov_5(segment3, TOP_FILTER_MOV_5, LOW_FILTER_MOV_5);
      inflatedTime=inflatedTime+segment3;

      digitalWrite(valve1, LOW);
      digitalWrite(pump1, HIGH);
      segment2 = delay_inflation_mov_5(segment2, TOP_FILTER_MOV_5, LOW_FILTER_MOV_5);
      inflatedTime=inflatedTime+segment2;
      digitalWrite(pump1, LOW);

      segment3 = delay_inflation_mov_5(segment3, TOP_FILTER_MOV_5, LOW_FILTER_MOV_5);
      inflatedTime=inflatedTime+segment3;

      //Third round of data inflations
      if (req_pack_in_4_5) {
          platform.SendMoveReqPacket(get_actualTime());
      }
      segment1 = rawData[2].first + 1; //~100
      segment2 = rawData[2].second + 1; //~100
      segment3 = rawData[2].third + 1; //

      digitalWrite(valve2, LOW);
      digitalWrite(pump2, HIGH);
      segment1 = delay_inflation_mov_5(segment1, TOP_FILTER_MOV_5, LOW_FILTER_MOV_5);
      inflatedTime=inflatedTime+segment1;
      digitalWrite(pump2, LOW);

      segment3 = delay_inflation_mov_5(segment3, TOP_FILTER_MOV_5, LOW_FILTER_MOV_5);
      inflatedTime=inflatedTime+segment3;

      digitalWrite(valve3, LOW);
      digitalWrite(pump3, HIGH);
      segment2 = delay_inflation_mov_5(segment2, TOP_FILTER_MOV_5, LOW_FILTER_MOV_5);
      inflatedTime=inflatedTime+segment2;
      digitalWrite(pump3, LOW);

      segment3 = delay_inflation_mov_5(segment3, TOP_FILTER_MOV_5, LOW_FILTER_MOV_5);
      inflatedTime=inflatedTime+segment3;

  }

  //digitalWrite(pump4, HIGH); //***Changed by Jonas 8-7-22
  //delay(24000); //***Changed by Jonas 8-7-22 
  digitalWrite(pump4, LOW);

  deflateAllSimul(40000, false);

}

void pauseClosedValves(long pauseTime){
  digitalWrite(valve1, LOW);
  digitalWrite(valve2, LOW);
  digitalWrite(valve3, LOW);
  digitalWrite(valve4, LOW);
  delay(pauseTime);
  }
