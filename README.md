# BruteForcePlatforms

This project contains two main folders plus.
The main idea is to control some soft robotic platforms using a master connected to a laptop. The communication is
made using xbee modules. In order to establish a correct communication, a protocol was designed (BFP). 
The sent data is related to the gathered data during the performances that Maja did and using a genetic algorithm 
-novelty search- these data is transformed. 
The user can control some parameters of the platform's performance and see the state of them a simple GUI.

* * *
# Arduino/platform code

The code inside the arduino_code folder contains the control of the soft robots as well as the 
programmed library BFP that allows the correct communication between platform and master.

## Uploading the code to the platforms.

In order to upload the code to a desired platform, it's mandatory to have installed Arduino. Connect the Arduino
platform to the computer with the installed Arduino program and upload the code using it. As soon as the code has been
uploading, the code will start to run. Please connect the platform using the available connector in the platform to a
5V/2A transformer in order to have a correct functioning.

* * *

# Python code

In the python_code folder one can find the programming of the communication as well as the programming of the novelty search
algorithm and the programming of the behaviour of a minimalistic GUI. In order to execute the program please make sure to
have installed the libraries defined in "python_code/requirements.txt". Command to execute the code:

    $ python simpleGUI.py

