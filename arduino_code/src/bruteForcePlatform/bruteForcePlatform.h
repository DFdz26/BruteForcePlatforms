//
// Created by danny on 4/22/22.
//


#ifndef NETWORK_CREATOR_BRUTEFORCEPLATFORM_H
#define NETWORK_CREATOR_BRUTEFORCEPLATFORM_H

#include "dispatcher.h"


#define EXPOSE_PRIVATE_DEBUG
#define RECEIVE_SIGN_IN_ONCE_CONNECTED

#define MAX_ITERATIONS_IN_3RD_MOVEMENT 3
#define MIN_DEFLATE_TIME 5000
#define MAX_DEFLATE_TIME 25000
#define MAX_CHAMBER 3
#define MAX_ITERATIONS 3

class PlatformsBruteForce {
public:

    typedef struct data_movement_t_ {
        uint16_t inflation_time; // must be between 5000 and 25000
        uint8_t chamber;
        uint8_t iterations;
    } data_movement_t;

    typedef struct raw_data_t_ {
        uint16_t first;
        uint8_t second;
        uint8_t third;
    } raw_data_t;

    typedef enum __attribute__((packed)) PlatformSate_t_ {
        PLATFORM_NO_ERROR       = 0,
        PLATFORM_NO_MESS        = 1,
        PLATFORM_TIMEOUT        = 2,
        PLATFORM_MESS_RECEIVED  = 3,
        PLATFORM_WRONG_MESS     = 4,
        PLATFORM_INTERN_ERROR   = 5,

    } PlatformSate_t;

    explicit PlatformsBruteForce(uint8_t device_add, uint8_t floor, uint8_t broadcast_add, uint8_t server_add);
    explicit PlatformsBruteForce();
    ~PlatformsBruteForce();

    PlatformSate_t run(unsigned long actualTime);

    uint8_t GetActiveMovement() const;
    bool GetActive() const;
    bool GetOrganicStop() const;
    void setOrganicStop(bool org);

    void setActualTime(unsigned long actualTime);

    PlatformSate_t SignInNetwork();
    PlatformSate_t SignOutNetwork();
    PlatformSate_t SendPing();
    PlatformSate_t SendBusyPacket();
    PlatformSate_t SendFreePacket();
    PlatformSate_t SendMoveReqPacket(unsigned long actual_time);
    PlatformSate_t WaitingMasterMessage();

    void getXbeeID();
    void loadCommunicationFunction(Dispatcher::prototype_receiving receiving, Dispatcher::prototype_sending sending);

    void loadDebugger(proto_debug protoDebug);
    int8_t CopyMovesArgument(data_movement_t* input, uint8_t size);
    int8_t CopyRawMessage(raw_data_t* input, uint8_t size);

#ifndef EXPOSE_PRIVATE_DEBUG
private:
#endif
    typedef enum __attribute__((packed)) internPlatformState_t_ {
        INIT_PLATFORM       = 0,
        CONNECTED_PLATFORM  = 1,
        SEND_PING           = 2,
        EXPECTING_REPLAY    = 3,
        BUSY_PLATFORM       = 4,
        EXPECTING_MOVE_DATA = 5,

    } internPlatformState_t;

    typedef enum __attribute__((packed)) messageTypes_t_ {
        SIGN_IN_NETWORK     = 0,
        PING                = 1,
        INSTRUCTION         = 2,
        BUSY                = 3,
        SIGN_OUT_NETWORK    = 4,
        MOVE                = 5,

    } messageTypes_t;

    typedef enum __attribute__((packed)) instructionTypes_t_ {
        STOP_INSTRUCTION        = 1,
        ACTIVATE_INSTRUCTION    = 2,

    } instructionTypes_t;

    int8_t BuildSignInPacket(uint8_t* buffer, uint8_t* bufferSize);
    int8_t BuildSignOutPacket(uint8_t* buffer, uint8_t* bufferSize);
    int8_t BuildPingPacket(uint8_t* buffer, uint8_t* bufferSize);
    int8_t BuildBusyPacket(uint8_t* buffer, uint8_t* bufferSize);
    int8_t BuildMoveReqPacket(uint8_t *inBuffer, uint8_t *inBufferSize);

    int8_t BuildPacket(uint8_t* buffer, uint8_t* bufferSize, messageTypes_t);

    int8_t ParseSignInPacket(uint8_t* buffer, uint8_t bufferSize);
    int8_t ParsePingPacket(uint8_t* buffer, uint8_t bufferSize);
    int8_t ParseInstructionPacket(uint8_t* buffer, uint8_t bufferSize);
    int8_t ParseMovePacket(uint8_t* buffer, uint8_t bufferSize);

    int8_t CheckProtocolTypeSize(uint8_t* buffer, uint8_t bufferSize, messageTypes_t t, uint8_t expectedSize);
    int8_t CheckAddress(const uint8_t* buffer, uint8_t bufferSize) const;

    static void Write32tIntoBuffer(uint8_t* buffer, unsigned int number);
    PlatformSate_t WaitingReplay();
    void printDebug(const char* buff, uint8_t length, uint8_t num) const;
    PlatformSate_t sendBusyFreePacket();
    static bool check_uint32_from_buffer(const uint8_t* buffer, uint32_t check);

    uint8_t device_address;
    uint8_t device_floor;
    bool active;
    uint8_t broadcast_address;
    uint8_t server_address;
    Dispatcher dispatcher;
    internPlatformState_t interState;
    messageTypes_t expectedMessage;
    uint32_t SerialNumberHigh;
    uint32_t SerialNumberLow;
    uint8_t movementActive;
    data_movement_t argumentsMovement[MAX_ITERATIONS_IN_3RD_MOVEMENT];
    raw_data_t rawData[MAX_ITERATIONS_IN_3RD_MOVEMENT];
    bool stopOrganic;
    bool busy_device;

    uint16_t timerPing;

    unsigned long time;
    unsigned long stored_time;
    proto_debug debugFunction;


};


#endif //NETWORK_CREATOR_BRUTEFORCEPLATFORM_H
