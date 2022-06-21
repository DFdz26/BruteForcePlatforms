from threading import Thread, Lock
import time
import serial


def lists_available_ports():
    from serial.tools import list_ports
    ret = {}

    all_port_tuples = list_ports.comports()
    for port, info, _ in all_port_tuples:
        ret[port] = []
        ret[port] = info

    return ret


class SerialReceiver(Thread):
    def __init__(self, port_name, baudrate=9600, timeout=None, debug_serial=None):
        Thread.__init__(self)

        self.previous_time = time.time()
        self.buffer = b''
        self.raw_messages = []
        self.eofl = b'\r\n'
        self.terminate = False
        self.mutex_port = Lock()
        self.port = serial.Serial()
        self.port.port = port_name
        self.port.baudrate = baudrate
        self.port.timeout = timeout
        self.internTimeout = 9000 / 1000   # Seconds
        self.sleep = 1 / 1000   # Seconds
        self.started = False
        self.debug_serial = debug_serial

    def get_started(self):
        return self.started

    def open_port(self):
        self.port.open()

    def close_port(self):
        if self.port.is_open:
            self.port.close()

    def read_messages(self):
        ret = None

        if len(self.raw_messages) != 0:
            ret = self.raw_messages.pop(0)

            if self.debug_serial is None:
                print(f'Received: {ret}')
            else:
                self.debug_serial.write_data(f'Received: {ret}')

        return ret

    def send_message(self, message):
        self.mutex_port.acquire()
        self.port.write(message + self.eofl)
        self.port.flush()
        self.mutex_port.release()

        if self.debug_serial is None:
            print(f'Sent: {message}')
        else:
            self.debug_serial.write_data(f'Sent: {message}')

    def terminate_process(self):
        self.terminate = True

    def run(self):
        self.started = True

        if not self.port.is_open:
            self.open_port()
            if self.debug_serial is None:
                print('Port opened')
            else:
                self.debug_serial.write_data('Port opened')

        if self.debug_serial is None:
            print('Running')
        else:
            self.debug_serial.write_data('Running')

        while not self.terminate:
            if self.port.inWaiting() > 0:
                self.mutex_port.acquire()
                aux = self.port.read()
                self.mutex_port.release()

                if aux != b'':
                    self.buffer += aux
                    self.previous_time = time.time()

                    if self.debug_serial is None:
                        print(f'{aux}')
                    else:
                        self.debug_serial.write_data(f'{aux}')

                if self.eofl == self.buffer[-len(self.eofl):]:
                    self.raw_messages.append(self.buffer[:-len(self.eofl)])
                    self.buffer = b''

            elif self.internTimeout > (time.time() - self.previous_time):
                self.buffer = b''

            time.sleep(self.sleep)

    def __del__(self):
        self.terminate_process()
        self.close_port()


if __name__ == "__main__":
    ports = lists_available_ports()
    available_names = list(ports.keys())
    print(available_names)

    print(ports)
