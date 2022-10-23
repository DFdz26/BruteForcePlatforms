
int checkInflationTime(int inflationTime, int maxLimit, int minLimit) {
  int ret = inflationTime%maxLimit;

  if (minLimit > ret) {
    ret = minLimit;
  }

  return ret;
}

void sending_data(uint8_t* data, uint8_t length_in, uint8_t* endLine) {
#ifdef SERIAL_DEBUG
  #ifdef PRINT_DEBUG
  Serial.print("Enviado: ");
  for (uint8_t i = 0; i < length_in; i++) {
        const char* aux = ((i + 1) < length_in) ? ", " : "\n";
        Serial.print("\"");
        Serial.print((char)data[i]);
        Serial.print("\":");
        Serial.print(data[i], HEX);
        Serial.print(aux);
    }
    if (NULL != endLine) {
      Serial.write(endLine, 2);
    }

  #endif

    xbee.write(data, length_in);
    
    if (NULL != endLine) {
      xbee.write(endLine, 2);
    }

    xbee.flush();
#else
    Serial.write(data, length_in);

    if (NULL != endLine) {
        Serial.write(endLine, 2);
    }

    Serial.flush();
#endif
}

void receiving_data_using_endLine(uint8_t* buff, uint8_t* received_size, uint8_t length_in, uint8_t* endLine) {
  uint8_t countEndLine = 0;
  uint8_t countWithoutComm = 0;
  
  while (countEndLine != 2) {
#ifdef SERIAL_DEBUG
    if (xbee.available() > 0) {
      
      char rec = xbee.read();
#else
    if (Serial.available() > 0) {

      char rec = Serial.read();
#endif
      countWithoutComm = 0;
      
      if (rec == endLine[countEndLine]) {
        countEndLine++;
      } else countEndLine = 0;
      
      if (length_in >= (*received_size)) {
        buff[*received_size] = (uint8_t)rec;
        (*received_size)++;
      }
    } else {
      countWithoutComm++;

      if (countWithoutComm == 8) break;
    }
  }

  // Flush the received input
#ifdef SERIAL_DEBUG
  while(xbee.available())
    xbee.read();
#else
  while(Serial.available())
    Serial.read();
#endif
}

void receiving_data(uint8_t* data, uint8_t* length_in, uint8_t* endLine) {
    uint8_t auxRec[MAX_SIZE_BUFFER_IN];
    uint8_t receivedBytes = 0;
#ifdef SERIAL_DEBUG
    if (endLine != NULL) {
      
      if (xbee.available() > 0) {
        receiving_data_using_endLine(auxRec, &receivedBytes, *length_in, endLine);
      }

    } else {
      for (uint8_t i = 0; i < 4; i++) {
        while (xbee.available() > 0) {
          char rec = xbee.read();
          if (*length_in >= receivedBytes) {
            auxRec[receivedBytes] = (uint8_t)rec;
            receivedBytes++;
          }
        }
        delay(20);
      }
    }

   

    if (0 != receivedBytes) {
     
      memcpy(data, auxRec, receivedBytes);

      #ifdef PRINT_DEBUG
      Serial.println("Recibido: ");
      if (15 == receivedBytes) {
        for (uint8_t i = 0; i < receivedBytes; i++) {
          const char* aux = ((i + 1) <  receivedBytes) ? ", " : "\n";
          Serial.print("\"");
          Serial.print((char)data[i]);
          Serial.print("\":");
          Serial.print(data[i], HEX);
          Serial.print(aux);
        }
      }
      #endif

    }
    
    *length_in = receivedBytes;
#else
    if (endLine != NULL) {

        if (Serial.available() > 0) {
            receiving_data_using_endLine(auxRec, &receivedBytes, *length_in, endLine);
        }

    } else {
        for (uint8_t i = 0; i < 4; i++) {
            while (Serial.available() > 0) {
                char rec = Serial.read();
                if (*length_in >= receivedBytes) {
                    auxRec[receivedBytes] = (uint8_t)rec;
                    receivedBytes++;
                }
            }
            delay(20);
        }
    }

    if (0 != receivedBytes) {
        memcpy(data, auxRec, receivedBytes);
    }

    *length_in = receivedBytes;
#endif
    
}

void debugFunction(const char* data, uint8_t length, uint8_t num) {
#ifdef SERIAL_DEBUG
    Serial.print(data);
    Serial.print("   ");
    Serial.println(num);
    Serial.println("-----");
#endif
}

bool DelayRunPlatform(long delay_time) {
  unsigned long init_time_pause = millis();
  bool rc = false;
  
  while(millis() < (init_time_pause + delay_time)) {
    if (PlatformsBruteForce::PLATFORM_MESS_RECEIVED == platform.run(get_actualTime())) {
      if (0 == platform.GetActiveMovement()) {
        rc = true;
      } else {
        platform.SendBusyPacket();
      }
    }
    delay(100);
  }

  

  return rc;
}

void printMovArgs(PlatformsBruteForce::data_movement_t* movData) {
#ifdef SERIAL_DEBUG
  for (uint8_t i = 0; i < MAX_ITERATIONS_IN_3RD_MOVEMENT; i++) {
    Serial.print("Inflation time: ");
    Serial.println(movData[i].inflation_time);
    Serial.print("chamber: ");
    Serial.println(movData[i].chamber);
    Serial.print("iterations: ");
    Serial.println(movData[i].iterations);
    Serial.println("-----------------");
  }
#endif
}


unsigned long get_actualTime() {

  if (millis() < starting_time) {
    starting_time = millis();
  }
  
  return (millis() - starting_time);
}

int delay_inflation_mov_5(int del, int top, int low) {
    if (del > top) del = top;
    else if (del < low) del = low;
    delay(del);

    return del;
}
