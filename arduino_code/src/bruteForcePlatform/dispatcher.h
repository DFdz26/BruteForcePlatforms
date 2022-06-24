//
// Created by danny on 4/22/22.
//

#ifndef NETWORK_CREATOR_DISPATCHER_H
#define NETWORK_CREATOR_DISPATCHER_H


#ifndef ARDUINO
#include <iostream>
#else
//#include <String.h>
#include <WString.h>

#endif
typedef void (*proto_debug)(const char* , uint8_t length, uint8_t num);

class Dispatcher {

public:
    typedef enum __attribute__((packed)) dispatcher_rc_t_ {
        DISPATCHER_NO_ERROR = 0,
        DISPATCHER_TIMEOUT  = 1,
        DISPATCHER_BAD_ARGS  = 2,

    } dispatcher_rc_t;


    typedef void (*prototype_sending)(uint8_t* packet, uint8_t length, uint8_t* endLine);
    typedef void (*prototype_receiving)(uint8_t* packet, uint8_t* length, uint8_t* endLine);
    Dispatcher();

#ifndef ARDUINO
    dispatcher_rc_t Send(const std::string& packet, bool endLine);
#else
    dispatcher_rc_t Send(String& packet, bool endLine);
#endif
    dispatcher_rc_t Send(uint8_t* packet, uint8_t length, bool endLine);

    dispatcher_rc_t BlockingReceiver(uint8_t* packet, uint8_t length, bool expected, bool endLine);

    dispatcher_rc_t ReceiveCheck(uint8_t* packet, uint8_t* length, bool endLine);
    dispatcher_rc_t ReceiveCheck(char* packet, uint8_t* length, bool endLine);

    void loadSendingFunction(prototype_sending sending);
    void loadReceivingFunction(prototype_receiving receiving);

    void loadDebugger(proto_debug protoDebug);

private:

    prototype_sending prototypeSending;
    prototype_receiving prototypeReceiving;
    proto_debug debugFunction;


    void printDebug(const char* buff, uint8_t length);
    uint8_t endLine_chars[2];

};
#endif //NETWORK_CREATOR_DISPATCHER_H
