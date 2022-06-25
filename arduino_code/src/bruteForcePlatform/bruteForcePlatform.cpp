//
// Created by danny on 4/22/22.
//

#include "bruteForcePlatform.h"
#ifndef ARDUINO
#include <cstring>
#endif

#define SIZE_SIGN_IN_PACKAGE 13
#define SIZE_OUT_PACKAGE 7
#define SIZE_PING_PACKAGE 9
#define SIZE_BUSY_PACKAGE 8
#define SIZE_INSTRUCTION_PACKAGE 8
#define REPLAY_SIZE_SIGN_IN_PACKAGE 16
#define REPLAY_SIZE_PING_PACKAGE 7
#define SIZE_MOVE_PACKET 8 + MAX_ITERATIONS_IN_3RD_MOVEMENT * 4
#define SIZE_REQ_MOVE_PACKET 7

#define SIZE_IN_BUFFER 32
#define TIMER_SEND_MOVE_REQ_AGAIN 8000

bool PlatformsBruteForce::check_uint32_from_buffer(const uint8_t* buffer, uint32_t check) {
    uint32_t aux;
    memcpy(&aux, buffer, sizeof(uint32_t));

    return (aux == check);
}

PlatformsBruteForce::PlatformsBruteForce(uint8_t device_add, uint8_t floor, uint8_t broadcast_add, uint8_t server_add) {
    device_floor = floor;
    device_address = device_add;
    broadcast_address = broadcast_add;
    server_address = server_add;
    interState = INIT_PLATFORM;
    expectedMessage = SIGN_IN_NETWORK;
    active = false;
    SerialNumberLow = 0;
    SerialNumberHigh = 0;
    movementActive = 0;
    stopOrganic = false;
    timerPing = 0;
    time = 0;
    stored_time = 0;
    debugFunction = nullptr;
    busy_device = false;
    memset(argumentsMovement, 0, sizeof(data_movement_t) * MAX_ITERATIONS_IN_3RD_MOVEMENT);
    memset(rawData, 0, sizeof(data_movement_t) * MAX_ITERATIONS_IN_3RD_MOVEMENT);
}

PlatformsBruteForce::PlatformsBruteForce() {
    device_floor = 0;
    device_address = 0;
    broadcast_address = 0xFF;
    server_address = 0x00;
    interState = INIT_PLATFORM;
    expectedMessage = SIGN_IN_NETWORK;
    active = false;
    SerialNumberLow = 0;
    SerialNumberHigh = 0;
    movementActive = 0;
    stopOrganic = false;
    timerPing = 0;
    time = 0;
    stored_time = 0;
    debugFunction = nullptr;
    busy_device = false;
    memset(argumentsMovement, 0, sizeof(data_movement_t) * MAX_ITERATIONS_IN_3RD_MOVEMENT);
    memset(rawData, 0, sizeof(data_movement_t) * MAX_ITERATIONS_IN_3RD_MOVEMENT);
}

PlatformsBruteForce::PlatformSate_t PlatformsBruteForce::run(unsigned long actualTime) {

    PlatformsBruteForce::PlatformSate_t rc = PLATFORM_NO_ERROR;
    setActualTime(actualTime);

    switch (interState) {
        case INIT_PLATFORM:
            rc = SignInNetwork();
            break;
        case EXPECTING_MOVE_DATA:
            if (time >= (stored_time + 8000)) {
                rc = SendMoveReqPacket(actualTime);

                if (rc != PLATFORM_NO_ERROR) {
                    break;
                }
            }
        case CONNECTED_PLATFORM:
            rc = WaitingMasterMessage();
            break;
        case SEND_PING:
            if (time >= (stored_time + timerPing)) {
                rc = SendPing();
            } else {
                rc = WaitingMasterMessage();
            }
            break;
        case EXPECTING_REPLAY:
            rc = WaitingReplay();
            break;
        case BUSY_PLATFORM:
            break;
    }

    return rc;
}

PlatformsBruteForce::PlatformSate_t PlatformsBruteForce::SignInNetwork() {
    uint8_t buffer[SIZE_IN_BUFFER];
    uint8_t length_buffer = SIZE_IN_BUFFER;
    PlatformSate_t rc = (0 != BuildSignInPacket(buffer, &length_buffer)) ?
            PLATFORM_INTERN_ERROR : PLATFORM_NO_ERROR;

    if (rc == PLATFORM_NO_ERROR) {
        dispatcher.Send(buffer, length_buffer, true);
        expectedMessage = SIGN_IN_NETWORK;
        interState = EXPECTING_REPLAY;
    }

    if (rc == PLATFORM_NO_ERROR) {
        length_buffer = SIZE_IN_BUFFER;
        rc = (Dispatcher::DISPATCHER_TIMEOUT == dispatcher.ReceiveCheck(
                buffer,
                &length_buffer,
                true
                )) ?
             PLATFORM_NO_MESS : PLATFORM_NO_ERROR;
    }

    if (rc == PLATFORM_NO_ERROR) {
        length_buffer = SIZE_IN_BUFFER;
        rc = (0 != ParseSignInPacket(buffer, length_buffer)) ?
                PLATFORM_WRONG_MESS : PLATFORM_NO_ERROR;
    }

    if (rc == PLATFORM_NO_ERROR) {
        SendPing();
    }

    return rc;
}

PlatformsBruteForce::PlatformSate_t PlatformsBruteForce::SendPing() {
    uint8_t buffer[REPLAY_SIZE_PING_PACKAGE];
    uint8_t sizeBuffer = REPLAY_SIZE_PING_PACKAGE;

    PlatformSate_t rc = (0 == BuildPingPacket(buffer, &sizeBuffer)) ? PLATFORM_NO_ERROR : PLATFORM_INTERN_ERROR;

    if (rc == PLATFORM_NO_ERROR) {
        if (Dispatcher::DISPATCHER_NO_ERROR != dispatcher.Send(buffer, sizeBuffer, true)) {
            rc = PLATFORM_INTERN_ERROR;
        }
    }

    if (rc == PLATFORM_NO_ERROR) {
        interState = CONNECTED_PLATFORM;
    }

    return rc;
}


PlatformsBruteForce::PlatformSate_t PlatformsBruteForce::SendMoveReqPacket(unsigned long actual_time) {
    uint8_t buffer[SIZE_REQ_MOVE_PACKET];
    uint8_t sizeBuffer = SIZE_REQ_MOVE_PACKET;

    PlatformSate_t rc = (0 == BuildMoveReqPacket(buffer, &sizeBuffer)) ? PLATFORM_NO_ERROR : PLATFORM_INTERN_ERROR;

    if (rc == PLATFORM_NO_ERROR) {
        if (Dispatcher::DISPATCHER_NO_ERROR != dispatcher.Send(buffer, sizeBuffer, true)) {
            rc = PLATFORM_INTERN_ERROR;
        }
    }

    if (rc == PLATFORM_NO_ERROR) {
        interState = EXPECTING_MOVE_DATA;
        stored_time = actual_time;
    }

    return rc;
}


PlatformsBruteForce::PlatformSate_t PlatformsBruteForce::WaitingMasterMessage() {
    uint8_t buffer[SIZE_IN_BUFFER];
    uint8_t length_buffer = SIZE_IN_BUFFER;
    uint8_t type;
    PlatformSate_t rc = (Dispatcher::DISPATCHER_TIMEOUT == dispatcher.ReceiveCheck(
            buffer,
            &length_buffer,
            true)) ?
            PLATFORM_NO_MESS :
            PLATFORM_NO_ERROR;

    if (rc == PLATFORM_NO_ERROR) {
        length_buffer = SIZE_IN_BUFFER;
        type = buffer[3];

        if (!active) {
            if (INSTRUCTION != type) {
                rc = PLATFORM_WRONG_MESS;
            }
        }
#ifndef RECEIVE_SIGN_IN_ONCE_CONNECTED
        else if (SIGN_IN_NETWORK == type) {
            rc = PLATFORM_WRONG_MESS;
        }
#endif
    }

    if (rc == PLATFORM_NO_ERROR) {
        int8_t auxParse;

        switch (type) {
            case PING:
                auxParse = ParsePingPacket(buffer, length_buffer);

                if (0 == auxParse) {
                    stored_time = time;
                    interState = SEND_PING;
                }
                break;
            case INSTRUCTION:
                auxParse = ParseInstructionPacket(buffer, length_buffer);
                break;
            case MOVE:
                if (interState == PlatformsBruteForce::EXPECTING_MOVE_DATA) {
                    interState = CONNECTED_PLATFORM;
                }
                auxParse = ParseMovePacket(buffer, length_buffer);
                break;
            case SIGN_IN_NETWORK:
                auxParse = ParseSignInPacket(buffer, length_buffer);

                if (auxParse == 0) {
                    SendPing();
                }
                break;
            default:
                auxParse = -5;
        }

        if (0 != auxParse) {
            rc = PLATFORM_WRONG_MESS;
        }
    }

    if (rc == PLATFORM_NO_ERROR) {
        if (SEND_PING != interState) {
            rc = PLATFORM_MESS_RECEIVED;
        }
    }

    return rc;
}

int8_t PlatformsBruteForce::BuildPingPacket(uint8_t *buffer, uint8_t *bufferSize) {
    return BuildPacket(buffer, bufferSize, PING);
}

int8_t PlatformsBruteForce::BuildBusyPacket(uint8_t *buffer, uint8_t *bufferSize) {
    return BuildPacket(buffer, bufferSize, BUSY);
}

int8_t PlatformsBruteForce::BuildSignOutPacket(uint8_t *buffer, uint8_t *bufferSize) {
    return BuildPacket(buffer, bufferSize, SIGN_OUT_NETWORK);
}

int8_t PlatformsBruteForce::BuildSignInPacket(uint8_t* inBuffer, uint8_t* inBufferSize) {
    return BuildPacket(inBuffer, inBufferSize, SIGN_IN_NETWORK);
}

int8_t PlatformsBruteForce::BuildMoveReqPacket(uint8_t* inBuffer, uint8_t* inBufferSize) {
    return BuildPacket(inBuffer, inBufferSize, MOVE);
}

int8_t PlatformsBruteForce::BuildPacket(uint8_t* inBuffer, uint8_t* inBufferSize, PlatformsBruteForce::messageTypes_t t) {
    int8_t rc = 0;
    uint8_t size = 0;
    uint8_t buffer[SIZE_IN_BUFFER];

    switch (t) {
        case SIGN_IN_NETWORK:
            if (*inBufferSize < SIZE_SIGN_IN_PACKAGE) {
                rc = -1;
            }
            break;
        case PING:
            if (*inBufferSize < REPLAY_SIZE_PING_PACKAGE) {
                rc = -1;
            }
            break;
        case SIGN_OUT_NETWORK:
            if (*inBufferSize < SIZE_OUT_PACKAGE) {
                rc = -1;
            }
            break;
        case BUSY:
            if (*inBufferSize < SIZE_BUSY_PACKAGE) {
                rc = -1;
            }
            break;
        case MOVE:
            if (*inBufferSize < SIZE_REQ_MOVE_PACKET) {
                rc = -1;
            }
            break;
    }

    if (rc == 0) {

        buffer[0] = 'B';
        buffer[1] = 'F';
        buffer[2] = 'P';

        buffer[3] = (uint8_t) t;
        size = 4;

    }

    if (0 == rc) {
        if (SIGN_IN_NETWORK == t) {
            buffer[4] = broadcast_address;

//            Write32tIntoBuffer(buffer + 5, SerialNumberHigh);
//            Write32tIntoBuffer(buffer + 5 + 4, SerialNumberLow);

        memcpy(buffer + 5, &SerialNumberHigh, sizeof(uint32_t));
        memcpy(buffer + 5 + 4, &SerialNumberLow, sizeof(uint32_t));

        size = SIZE_SIGN_IN_PACKAGE;

        } else {
            buffer[4] = server_address;
            buffer[5] = device_floor;
            buffer[6] = device_address;

            size += 3;

            if (BUSY == t) {
                buffer[7] = busy_device;
                size += 1;
            }
        }
    }

    if (0 == rc) {
        memcpy(inBuffer, buffer, size * sizeof(uint8_t));
    }

    *inBufferSize = size;

    return rc;
}

int8_t PlatformsBruteForce::ParseSignInPacket(uint8_t *buffer, uint8_t bufferSize) {
    int8_t rc = CheckProtocolTypeSize(buffer, bufferSize, SIGN_IN_NETWORK, REPLAY_SIZE_SIGN_IN_PACKAGE);
    uint8_t checked = (sizeof(uint8_t) *4);

    if (0 == rc) {
        rc = (check_uint32_from_buffer(buffer + checked, SerialNumberHigh)) ? 0 : -1;
        checked += sizeof(uint32_t);

    }

    if (0 == rc) {
        rc = (check_uint32_from_buffer(buffer + checked, SerialNumberLow)) ? 0 : -1;
        checked += sizeof(uint32_t);
    }

    if (0 == rc) {
        rc = (memcmp(&server_address, buffer + checked, sizeof(uint8_t)) != 0) ? -1 : 0;
        checked += sizeof(uint8_t);
    }

    if (0 == rc) {
        device_floor = buffer[checked];
        device_address = buffer[checked + 1];
        active = (bool)buffer[checked + 2];

        printDebug("Hey, I'm the platform nº", 24, device_address);
        printDebug("In floor nº", 24, device_floor);
    }

    return rc;
}

void PlatformsBruteForce::getXbeeID() {
    uint8_t endPacket = 0x0D;
    uint8_t expected_pack[] = {0x4F, 0x4B, 0x0D};
    uint8_t size_expected = 3;
    char aux_receiver[9];
    uint8_t length_receive = 9;
#ifndef ARDUINO
    std::string aux_command = "+++";
#else
    String aux_command = "+++";
#endif
    Dispatcher::dispatcher_rc_t dispatcherRc;
    printDebug("Receiving XbeeID", 16, 0);

    dispatcher.Send(aux_command, false);
    dispatcher.BlockingReceiver(expected_pack, size_expected, true, false);

    aux_command = "ATSL";
    dispatcher.Send(aux_command, false);
    dispatcher.Send(&endPacket, 1, false);

    do {
        dispatcherRc = dispatcher.ReceiveCheck(aux_receiver, &length_receive, false);
        length_receive = 9;
    } while (Dispatcher::DISPATCHER_TIMEOUT == dispatcherRc);

    aux_receiver[8] = '\0';
    SerialNumberLow = (uint32_t) strtol(aux_receiver, 0, 16);

    aux_command = "ATSH";
    dispatcher.Send(aux_command, false);
    dispatcher.Send(&endPacket, 1, false);
    do {
        dispatcherRc = dispatcher.ReceiveCheck(aux_receiver, &length_receive, false);
    } while (Dispatcher::DISPATCHER_TIMEOUT == dispatcherRc);

    aux_receiver[8] = '\0';
    SerialNumberHigh = (uint32_t) strtol(aux_receiver, 0, 16);

    aux_command = "ATCN";
    dispatcher.Send(aux_command, false);
    dispatcher.Send(&endPacket, 1, false);
    dispatcher.BlockingReceiver(expected_pack, size_expected,  true, false);
    printDebug("Finished xbee ID", 16, 0);
}

void PlatformsBruteForce::Write32tIntoBuffer(uint8_t *buffer, unsigned int number) {
    for (uint8_t i = 0; i < 4; i++) {
        buffer[3 - i] = 0xFF & number;
        number >>= 8;
    }
}

PlatformsBruteForce::PlatformSate_t PlatformsBruteForce::WaitingReplay() {
    uint8_t buffer[REPLAY_SIZE_SIGN_IN_PACKAGE];
    uint8_t length_buffer = REPLAY_SIZE_SIGN_IN_PACKAGE;
    PlatformsBruteForce::PlatformSate_t rc = (Dispatcher::DISPATCHER_TIMEOUT == dispatcher.ReceiveCheck(
            buffer,
            &length_buffer,
            true
            )) ?
         PLATFORM_NO_MESS : PLATFORM_NO_ERROR;

    if (rc == PLATFORM_NO_ERROR) {
        length_buffer = REPLAY_SIZE_SIGN_IN_PACKAGE;
        if ( 0 != CheckProtocolTypeSize(buffer, length_buffer, expectedMessage, length_buffer)) {
            rc = PLATFORM_WRONG_MESS;
        }
    }

    if (rc == PLATFORM_NO_ERROR) {
        int8_t aux_rc = 0;
        switch (expectedMessage) {
            case SIGN_IN_NETWORK:
                aux_rc = ParseSignInPacket(buffer, length_buffer);
                break;
            case PING:
                aux_rc = ParsePingPacket(buffer, length_buffer);
                break;
            case INSTRUCTION:
                aux_rc = ParseInstructionPacket(buffer, length_buffer);
                break;
            case BUSY:
                break;
            case SIGN_OUT_NETWORK:
                break;
            case MOVE:
                break;
        }

        if (aux_rc != 0) {
            rc = PLATFORM_WRONG_MESS;
        }
    }

    if (rc == PLATFORM_NO_ERROR) {
        if (expectedMessage == SIGN_IN_NETWORK) {
            rc = SendPing();
        }
    }

    if (rc == PLATFORM_NO_ERROR) {
        interState = CONNECTED_PLATFORM;
    }

    return rc;
}

int8_t PlatformsBruteForce::ParsePingPacket(uint8_t *buffer, uint8_t bufferSize) {
    int8_t rc = CheckProtocolTypeSize(buffer, bufferSize, PING, SIZE_PING_PACKAGE);
    uint8_t checked = (sizeof(uint8_t) *4);

    if (0 == rc) {
        rc = CheckAddress(buffer + checked, bufferSize - checked);
        checked += sizeof(uint8_t) * 3;
    }

    if (0 == rc) {
        memcpy(&timerPing, buffer + checked, sizeof(uint16_t));
    }

    return rc;
}

int8_t PlatformsBruteForce::CheckProtocolTypeSize(uint8_t *buffer, uint8_t bufferSize, messageTypes_t t, uint8_t expectedSize) {
    int8_t rc;
    uint8_t first_check[] = {'B', 'F', 'P', t};

    // I don't know why my editor doesn't allow me to type rc = (bufferSize < expectedSize) ? -1 : 0; so yep...
    if (bufferSize < expectedSize) {
        rc = -1;
    } else {
        rc = 0;
    }

    if (0 == rc) {
        rc = (memcmp(first_check, buffer, sizeof(uint8_t) *4) != 0) ? -1 : 0;
    }

    return rc;
}

int8_t PlatformsBruteForce::CheckAddress(const uint8_t *buffer, uint8_t bufferSize) const {
    int8_t rc = (bufferSize < 3) ? -1 : 0;

    if (0 == rc) {
        uint8_t dest_add = buffer[0];
        rc = -2;

        if ((dest_add == broadcast_address) || (dest_add == device_floor)) {
            rc = 0;
        }
    }

    if (0 == rc) {
        uint8_t dest_add = buffer[1];
        rc = -2;

        if ((dest_add == broadcast_address) || (dest_add == device_address)) {
            rc = 0;
        }
    }

    if (0 == rc) {
        if (server_address != buffer[2])
            rc = -3;
    }

    return rc;
}

int8_t PlatformsBruteForce::ParseInstructionPacket(uint8_t *buffer, uint8_t bufferSize) {
    int8_t rc = CheckProtocolTypeSize(buffer, bufferSize, INSTRUCTION, SIZE_INSTRUCTION_PACKAGE);
    uint8_t checked = (sizeof(uint8_t) *4);
    uint8_t typeInstruction;

    if (0 == rc) {
        rc = CheckAddress(buffer + checked, bufferSize - checked);
        checked += sizeof(uint8_t) * 3;
    }

    if (0 == rc) {
        typeInstruction = buffer[checked];

        if ((!active) && (ACTIVATE_INSTRUCTION != typeInstruction)) {
            rc = -4;
        }
    }

    if (0 == rc) {
        uint8_t arg = buffer[checked + 1];

        switch (typeInstruction) {
            case STOP_INSTRUCTION:
                movementActive = 0;
                stopOrganic = (bool)arg;
                break;
            case ACTIVATE_INSTRUCTION:
                if (bufferSize < SIZE_INSTRUCTION_PACKAGE + 1) {
                    rc = -2;
                    break;
                }
                active = true;
                device_floor = arg;
                device_address = buffer[checked + 2];
                break;
            default:
                rc = -5;
        }
    }

    return rc;
}

int8_t PlatformsBruteForce::ParseMovePacket(uint8_t *buffer, uint8_t bufferSize) {
    int8_t rc = CheckProtocolTypeSize(buffer, bufferSize, MOVE, SIZE_MOVE_PACKET);
    uint8_t checked = (sizeof(uint8_t) *4);

    if (0 == rc) {
        rc = CheckAddress(buffer + checked, bufferSize - checked);
        checked += sizeof(uint8_t) * 3;
    }

    if (0 == rc) {
        movementActive = buffer[checked];
        checked++;

        for (uint8_t i = 0; i < MAX_ITERATIONS_IN_3RD_MOVEMENT; i++) {
            memcpy(&argumentsMovement[i].inflation_time, buffer + checked, sizeof(uint16_t));
            memcpy(&rawData[i].first, buffer + checked, sizeof(uint16_t));

            argumentsMovement[i].inflation_time %= MAX_DEFLATE_TIME;
            if (argumentsMovement[i].inflation_time < MIN_DEFLATE_TIME) {
                argumentsMovement[i].inflation_time = MIN_DEFLATE_TIME;
            }

            checked += sizeof(uint16_t);
            memcpy(&argumentsMovement[i].chamber, buffer + checked, sizeof(uint8_t));
            memcpy(&rawData[i].second, buffer + checked, sizeof(uint8_t));

            argumentsMovement[i].chamber %= MAX_CHAMBER;
            checked += sizeof(uint8_t);

            memcpy(&argumentsMovement[i].iterations, buffer + checked, sizeof(uint8_t));
            memcpy(&rawData[i].third, buffer + checked, sizeof(uint8_t));

            argumentsMovement[i].iterations %= MAX_ITERATIONS;
            checked += sizeof(uint8_t);
        }
    }

    return rc;
}

uint8_t PlatformsBruteForce::GetActiveMovement() const {
    return movementActive;
}

bool PlatformsBruteForce::GetActive() const {
    return active;
}

void PlatformsBruteForce::setOrganicStop(bool org) {
    stopOrganic = org;
}

bool PlatformsBruteForce::GetOrganicStop() const {
    return stopOrganic;
}

PlatformsBruteForce::PlatformSate_t PlatformsBruteForce::SignOutNetwork() {
    uint8_t buffer[SIZE_OUT_PACKAGE];
    uint8_t sizeBuffer = SIZE_OUT_PACKAGE;

    PlatformSate_t rc = (0 == BuildSignOutPacket(buffer, &sizeBuffer)) ? PLATFORM_NO_ERROR : PLATFORM_INTERN_ERROR;

    if (rc == PLATFORM_NO_ERROR) {
        if (Dispatcher::DISPATCHER_NO_ERROR != dispatcher.Send(buffer, sizeBuffer, true)) {
            rc = PLATFORM_INTERN_ERROR;
        }
    }

    if (rc == PLATFORM_NO_ERROR) {
        interState = INIT_PLATFORM;
    }

    return rc;
}

PlatformsBruteForce::~PlatformsBruteForce() {
    if (interState != INIT_PLATFORM)
        SignOutNetwork();
}

void PlatformsBruteForce::setActualTime(unsigned long actualTime) {
    time = actualTime;
}

void PlatformsBruteForce::loadCommunicationFunction(Dispatcher::prototype_receiving receiving,
                                                   Dispatcher::prototype_sending sending) {

    dispatcher.loadSendingFunction(sending);
    dispatcher.loadReceivingFunction(receiving);
}

void PlatformsBruteForce::loadDebugger(proto_debug protoDebug) {
    dispatcher.loadDebugger(protoDebug);
    debugFunction = protoDebug;
}

void PlatformsBruteForce::printDebug(const char *buff, uint8_t length, uint8_t num) const {
    if (nullptr != debugFunction) {
        debugFunction(buff, length, num);
    }
}

PlatformsBruteForce::PlatformSate_t PlatformsBruteForce::SendBusyPacket() {
    busy_device = true;

    return PlatformsBruteForce::sendBusyFreePacket();
}

PlatformsBruteForce::PlatformSate_t PlatformsBruteForce::SendFreePacket() {
    busy_device = false;

    return PlatformsBruteForce::sendBusyFreePacket();
}

PlatformsBruteForce::PlatformSate_t PlatformsBruteForce::sendBusyFreePacket() {
    uint8_t buffer[SIZE_BUSY_PACKAGE];
    uint8_t sizeBuffer = SIZE_BUSY_PACKAGE;

    PlatformSate_t rc = (0 == BuildBusyPacket(buffer, &sizeBuffer)) ? PLATFORM_NO_ERROR : PLATFORM_INTERN_ERROR;

    if (rc == PLATFORM_NO_ERROR) {
        if (Dispatcher::DISPATCHER_NO_ERROR != dispatcher.Send(buffer, sizeBuffer, true)) {
            rc = PLATFORM_INTERN_ERROR;
        }
    }

    if (rc == PLATFORM_NO_ERROR) {
        interState = CONNECTED_PLATFORM;
    }

    return rc;
}

int8_t PlatformsBruteForce::CopyMovesArgument(data_movement_t* input, uint8_t size) {
    int8_t rc = (0 == input) ? -1 : 0;

    if (0 == rc) {
        memcpy(input, argumentsMovement, sizeof(data_movement_t)*size);
    }

    return rc;
}

int8_t PlatformsBruteForce::CopyRawMessage(raw_data_t* input, uint8_t size) {
    int8_t rc = (0 == input) ? -1 : 0;

    if (0 == rc) {
        memcpy(input, rawData, sizeof(raw_data_t)*size);
    }

    return rc;
}

