//
// Created by danny on 4/22/22.
//

#include "dispatcher.h"


Dispatcher::Dispatcher() {
    prototypeSending = nullptr;
    prototypeReceiving = nullptr;
    debugFunction = nullptr;
    endLine_chars[0] = {'\r'};
    endLine_chars[1] = {'\n'};
}

Dispatcher::dispatcher_rc_t Dispatcher::ReceiveCheck(uint8_t *packet, uint8_t *length, bool endLine) {
    Dispatcher::dispatcher_rc_t rc = (nullptr == prototypeReceiving) ? DISPATCHER_BAD_ARGS : DISPATCHER_NO_ERROR;
    uint8_t aux_length = *length;

    if (DISPATCHER_NO_ERROR == rc) {
        prototypeReceiving(packet, &aux_length, (endLine) ? endLine_chars : nullptr);
        if (aux_length == 0) {
            rc = DISPATCHER_TIMEOUT;
        }

        *length = aux_length;
    }

    return rc;
}

Dispatcher::dispatcher_rc_t Dispatcher::ReceiveCheck(char *packet, uint8_t* length, bool endLine) {

    return ReceiveCheck((uint8_t*) packet, length, endLine);
}

Dispatcher::dispatcher_rc_t Dispatcher::BlockingReceiver(uint8_t *packet, uint8_t length, bool expected, bool endLine) {
    uint8_t buff[length];
    uint8_t aux_buff_length = length;
    Dispatcher::dispatcher_rc_t rc;
    bool exit = false;

    if (expected) {
        while (!exit) {
            rc = ReceiveCheck(buff, &aux_buff_length, endLine);
            if (rc != DISPATCHER_TIMEOUT) {
                exit = true;
                if (aux_buff_length == length) {
                    for (uint8_t i = 0; i < length; i++) {
                        if (buff[i] != packet[i]) {
                            exit = false;
                            break;
                        }

                    }
                }
            }
            aux_buff_length = length;
            if (rc == DISPATCHER_BAD_ARGS) break;
        }
    } else {
        do {
            rc = ReceiveCheck(packet, &aux_buff_length, endLine);
            aux_buff_length = length;
        } while (rc == DISPATCHER_TIMEOUT);
    }

    return rc;
}

Dispatcher::dispatcher_rc_t Dispatcher::Send(uint8_t *packet, uint8_t length, bool endLine) {
    Dispatcher::dispatcher_rc_t rc = (nullptr == prototypeSending) ? DISPATCHER_BAD_ARGS : DISPATCHER_NO_ERROR;

    if (DISPATCHER_NO_ERROR == rc) {
        prototypeSending(packet, length, (endLine) ? endLine_chars : nullptr);
    }
    return rc;
}
#ifndef ARDUINO
Dispatcher::dispatcher_rc_t Dispatcher::Send(const std::string& packet, bool endLine) {
    return Send((uint8_t *) packet.c_str(), packet.size(), endLine);
}
#else
Dispatcher::dispatcher_rc_t Dispatcher::Send(String& packet, bool endLine) {
    return Send((uint8_t *) packet.c_str(), packet.length(), endLine);
}
#endif

void Dispatcher::loadSendingFunction(prototype_sending sending) {
    prototypeSending = sending;
}

void Dispatcher::loadReceivingFunction(prototype_receiving receiving) {
    prototypeReceiving = receiving;
}

void Dispatcher::loadDebugger(proto_debug protoDebug) {
    debugFunction = protoDebug;
}

void Dispatcher::printDebug(const char *buff, uint8_t length) {
    if (nullptr != debugFunction) {
        debugFunction(buff, length, 0);
    }
}
