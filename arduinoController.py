# -*- coding: utf-8 -*-
"""
Created on Thu Aug 03 23:32:23 2017

@author: Cody
"""

import serial

class Arduino(object):
    """
    Acts as a python prototype of an Arduino.
    All communication between Arduino and Python is handled through as serial connection.
    Python can not have access to all arduino constants because several are board specific. 
    The most common are implemented here as alternatives to memorizing integers for convenience.
    All outputs to the Arduino are typecasted as ints using toInt(), which converts non-integers to 0.
    Minimal augmentation to python and arduino code could allow for communication other data types.
    """

    def __init__(self, port, baudrate=9600,timeout=1,dtr=False,rts=True,open=True):
        """
        Constructs an Arduino object which allows for access to arduino functions from python.

        Parameters:
        port -- The Computer port to which the Arduino is physically connected. Examples include "COM5" and "/dev/ttyUSB1"
        baudrate -- Rate at which information is communicated in the serial connection. 
        Must match the baudrate selected by the Arduino software. (Default = 9600)
        timeout -- Time in seconds that getData() is willing to wait before timing out. (Default = 1)
        dtr -- dtr and rts control whether or not the Arduino resets upon python opening the serial connection.
        The default values ensure no reset on the Arduino DUE (Default = False)
        Resetting the Arduino program can cause unforseen communications issues. 
        rts -- see dtr (Default = True)
        open -- If open is set to true, the constructor opens the serial connection. (Default = True)
        """

        #Common default constants in arduino. Use at own risk - Board may for whatever reason not follow convention.
        self.LOW = 0
        self.HIGH = 1
        self.INPUT = 0
        self.OUTPUT = 1
        self.INPUT_PULLUP = 2
        self.LED_BUILTIN = 13
        self.true = True
        self.false = False

        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.timeout = timeout
        self.ser.setDTR(dtr)
        self.ser.setRTS(rts)
        self.outputPins=set()
        self.inputPins=set()
        if (open):
            self.ser.open()



    def __str__(self):
        """Returns a string detailing the port, baudrate, and timeout of the serial connection."""
        return "Arduino is on port {} at {:d} baudrate with timeout {:d}".format(self.serial.port, self.serial.baudrate,
                                                                                 self.serial.timeout)

    def addOutputs(self, pinArray):
        """
        Sets the pin mode of each given pin to output.
        Calls pinMode(each_pin,OUTPUT) on each unique element of pinArray on the Arduino side.

        Parameters:
        pinArray -- object that can be converted to a set() containing the pins to set as output.
        """
        for each_pin in pinArray:
            self.pinMode(each_pin,self.OUTPUT)
        pinset = set(pinArray)
        self.outputPins.update(pinset)
        self.inputPins.difference_update(pinset)

    def addInputs(self, pinArray):
        """
        Sets the pin mode of each given pin to input.
        Calls pinMode(each_pin,INPUT) on each unique element of pinArray on the Arduino side.

        Parameters:
        pinArray -- object that can be converted to a set() containing the pins to set as input.
        """
        for each_pin in pinArray:
            self.pinMode(each_pin,self.INPUT)
        pinset = set(pinArray)
        self.inputPins.update(pinset)
        self.ouputPins.difference_update(pinset)

    def pinMode(self,pin,mode):
        """
        Calls pinMode(pin,mode) on the Arduino.

        Parameters:
        pin -- The pin to set the mode of.
        mode -- INPUT, OUTPUT, or INPUT_PULLUP modes (commonly 0, 1, and 2, respectively)
        """
        if mode == self.INPUT or mode == self.INPUT_PULLUP:
            self.inputPins.update({pin})
            self.outputPins.difference_update({pin})
        if mode == self.OUTPUT:
            self.outputPins.update({pin})
            self.inputPins.difference_update({pin})
        self.sendData("1>"+str(pin)+">"+str(mode)+">")

    def digitalWrite(self,pin,value):
        """
        Calls digitalWrite(pin,value) on Arduino.

        Parameters:
        pin -- The pin to set LOW.
        value -- 0 for LOW and 1 for HIGH
        """
        self.sendData("2>"+str(pin)+">"+str(value)+">")

    def digitalRead(self, pin):
        """
        Calls digitalRead(pin) on the Arduino side.

        Parameters:
        pin -- The pin to read.

        Returns:
        The state of pin: 0 for LOW and 1 for HIGH.
        """
        self.sendData("3>"+str(pin)+">")
        return self.getData()

    def analogReference(self,type):
        """
        Calls analogReference(type) on the Arduino side.

        Parameters:
        type -- See Arduino Documentation for analogReference
        """
        self.sendData("4>"+str(type)+">")

    def analogRead(self, pin):
        """
        Calls the analogRead(pin) on the Arduino side.

        Parameters:
        pin -- The analog pin to read from.

        Returns:
        Number specifying the voltage at pin. Not the value in volts - See Arduino documentation for analogRead
        """
        self.sendData("5>"+str(pin)+">")
        return self.getData()

    def analogWrite(self, pin, value):
        """
        Calls analogWrite(pin,value) on the Arduino side.

        Parameters:
        pin -- The analog pin to write to.
        value -- Number specifying the voltage to write to pin. Not the value in volts - See Arduino documentation for analogWrite
        """
        self.sendData("6>"+str(pin)+">"+str(value)+">")

    def analogReadResolution(self,bits):
        """
        calls analogReadResolution(bits) on the Arduino side. Only implemented on DUE and ZERO.

        Parameters:
        bits -- The resolution of the bits returned by analogRead()
        """
        self.sendData("7>"+str(bits)+">")

    def analogWriteResolution(self,pin,bits):
        """
        calls analogWriteResolution(bits) on the Arduino side. Only implemented on DUE and ZERO.

        Parameters:
        pin -- The analog pin to write to
        bits -- The resolution of the bits used by analogWrite()
        """
        self.sendData("8>"+str(pin)+">"+str(bits)+">")

    def echo(self,message):
        """
        Arduino echos back what it converted message into

        Parameters:
        message -- The message to have interpreted and echo'd back.
        Don't include a > in message if you know what's good for you.
        """
        self.sendData("9>"+str(message)+">")
    
    def delay(self,millis):
        """
        calls delay(millis) on the Arduino side.
        
        Parameters:
            millis -- The number of milliseconds to make the Arduino wait for.
        """
        self.sendData("10>"+str(millis)+">")
    
    def delayMicroseconds(self,micros):
        """
        calls delayMicroseconds(micros) on the Arduino side.
        
        Parameters:
            micros -- Number of microseconds to make the Arduino wait for.
            Use if less than 16384 if you want an accurate delay. Otherwise, use delay(millis).
        """
        self.sendData("11>"+str(micros)+">")

    def sendData(self, serial_data):
        """
        Waits for a signal from the Arduino to need a command, then sends it out.

        Parameters:
        serial_data -- The data to send.
        """
        while self.getData() != "r":
            pass
        serial_data = str(serial_data).encode("utf-8")
        self.ser.write(serial_data)

    def getData(self):
        """
        Reads input from Arduino until a newline character is encountered.

        Returns: Input from Arduino converted to utf-8 with leading and trailing whitespace removed.
        """
        input_string = self.ser.readline()
        input_string = input_string.decode("utf-8",errors="ignore")
        return input_string.strip()

    def closeConnection(self):
        """Closes the serial connection."""
        self.ser.close()


    def openConnection(self, reset = False ):
        """Opens the serial connection

        Parameters:
        reset -- Set true to reset Arduino on opening connection. (Default = False) 
        Known to work for DUE. May require modification for other boards.
        Setting True can cause unforseen communications issues.
        """
        self.ser.setDTR(reset)
        self.ser.open()
    
    def update(self, times, words):
        out = 'u>' + str(len(times)) + '>'
        for ind in range(len(times)):
            out += str(times[ind]) + '>' + str(words[ind]) + '>'
        self.sendData(out)
        
if __name__ == '__main__':
    """
    Example of use. 
    This python code should resemble the blink program tutorial for Arduino beginners.
    It will turn the LED on and off repeatedly for a while.
    As an example of the communications issues cause by resetting upon connection, try setting myDTR=True.
    The program will hitch and need to be terminated if you do so. 
    You will then need to close the connection via the console.
    """
    
    port    = '/dev/tty.usbmodem1421'    #Must be modified to your port
    myDTR   = False                      #True => Reset board upon connection
    arduino = Arduino(port,dtr=myDTR)    #Instantiate Arduino object to begin connection
    
    #Setup
    arduino.pinMode(arduino.LED_BUILTIN,arduino.OUTPUT)
    
    #Loop - Not infinite here for convenience.
    for x in range(5):
        arduino.digitalWrite(arduino.LED_BUILTIN,arduino.LOW)
        arduino.delay(1000)
        arduino.digitalWrite(arduino.LED_BUILTIN,arduino.HIGH)
        arduino.delay(1000)

    arduino.closeConnection()
        
        
        