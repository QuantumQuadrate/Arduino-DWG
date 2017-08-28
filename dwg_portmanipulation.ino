//instantiate constants
const int SERIAL_RATE = 9600;
const int SERIAL_TIMEOUT = 5;
const uint32_t arrayLength = 26;
const uint32_t pinMask = 0x37EFF3FE;
const uint32_t mask1 = 0x000003FE;
const uint32_t mask2 = 0x000FF000;
const uint32_t mask3 = 0x0E700000;
const uint32_t mask4 = 0x30000000;

//declare globals
uint32_t startTime;
uint32_t numWords;
String input;
uint32_t digiTimes[arrayLength];
uint32_t digiWords[arrayLength];
byte trigPin;


void setup() {
  //declare trigger pin and output pins
  trigPin = 3;
  numWords = arrayLength;
  Serial.begin(SERIAL_RATE);
  Serial.setTimeout(SERIAL_TIMEOUT);
  for(uint8_t i = 3; i < 11; i++){
    pinMode(i, OUTPUT);
  }
  for(uint8_t i = 33; i < 42; i++){
    pinMode(i, OUTPUT);
  }
  for(uint8_t i = 44; i < 52; i++){
    pinMode(i, OUTPUT);
  }
  pinMode(trigPin, INPUT_PULLUP);
  //set default array for testing, eventually will be removed, maybe
  for (uint32_t num = 0; num < arrayLength; num++) {
    digiTimes[num] = num * 10;
    digiWords[num] = (num % 16)<<1;
  }
  askForCommand();
}

void loop() {
  //rewrite wave form if there is info availble
  //may require modifaction to acount for large data transfer due to buffer size
  if (Serial.available() > 0) {
    if (Serial.readStringUntil('>') == "u") {
      //find out haw many words are in the wave form
      numWords = readinULong();
      if (numWords > arrayLength) {
        numWords = arrayLength;
      }
      //times and corresponding words are entered in pairs
      for (unsigned long x = 0; x < numWords; x++) {
        digiTimes[x] = readinULong();
        digiWords[x] = correct_pins(readinULong());
      }
    }
    //empty buffer to clear garbage including excess words
    while (Serial.available() > 0) {
      Serial.read();
    }
    //ready to rewrite if needed
    askForCommand();
  }
  //write wave form to pins
  if (digitalRead(trigPin) == 0) {
    startTime = micros();
    //keep writing as long as there are still values left to write
    for (unsigned long count = 0; count < numWords; count++) {
      //wait for enough time to pass to write the current entry
      while (micros() - startTime < digiTimes[count]) {
      }
      write_word(digiWords[count]); //eventually a simultaneous assignments to multiple pins
    }
    delay(10);
    write_word(0);
    delay(200);
  }
}
//indicate to serial connection that ready to rewrite
void askForCommand() {
  Serial.println("r");
}

//read ULong from serial connection
unsigned long readinULong() {
  while (true) {
    if (Serial.available() > 0) {
      input = Serial.readStringUntil('>');
      //convert string to ULong
      unsigned long lon = 0;
      unsigned long power = 1;
      for (int i = 0; i < input.length(); i++) {
        lon += power * (input[input.length() - 1 - i] - '0');
        power *= 10;
      }
      return lon;
    }
  }
}

uint32_t correct_pins(uint32_t raw){
  raw = (raw<<1 & mask1) + (raw<<3 & mask2) + (raw<<4 & mask3) + (raw<<5 & mask4);
  return raw;
}


void write_word(uint32_t out_word){
  REG_PIOC_SODR = out_word & pinMask;
  REG_PIOC_CODR = ~(out_word & pinMask);
}
