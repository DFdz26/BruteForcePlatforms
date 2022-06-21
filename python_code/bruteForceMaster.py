import struct
import time

import serialReceiver
import load_data


class BruteForceMaster:
    protocol = 'BFP'
    dummy_floor = 254
    ASSIGNED_SIGN_IN_NUMBER = 0
    ASSIGNED_PING_NUMBER = 1
    ASSIGNED_INSTRUCTION_NUMBER = 2
    ASSIGNED_BUSY_NUMBER = 3
    ASSIGNED_SIGN_OUT_NUMBER = 4
    ASSIGNED_MOVE_NUMBER = 5

    little_big_endian = '<'

    instruction_types = {"stop": 1, "activate": 2}

    def __init__(self, available_platforms, baudrate=None, portName=None, master_add=0,
                 broadcast_address=0xFF, xbeeID_reg=None, assign_new_address=True, debug_serial=None):
        self.types_message = {
            "sign_in": self.ASSIGNED_SIGN_IN_NUMBER,
            "ping": self.ASSIGNED_PING_NUMBER,
            "instruction": self.ASSIGNED_INSTRUCTION_NUMBER,
            "busy": self.ASSIGNED_BUSY_NUMBER,
            "sign_out": self.ASSIGNED_SIGN_OUT_NUMBER,
            "move_pack": self.ASSIGNED_MOVE_NUMBER
        }
        self.defaultMaxRetries = 3
        self.debug_serial = debug_serial

        """ The dictionary looks like:
        {
            HIGH_SERIAL_NUMBER1: {
                                    LOW_SERIAL_NUMBER1: {
                                                            "n_platform": 1,
                                                            "floor": 1,
                                                            "active" 1
                                                        },
                                    LOW_SERIAL_NUMBER2: {
                                                            "n_platform": 3,
                                                            "floor": 4,
                                                            "active" 1
                                                        }
                                 },
            HIGH_SERIAL_NUMBER2: {
                                    LOW_SERIAL_NUMBER3: {
                                                            "n_platform": 1,
                                                            "floor": 3,
                                                            "active" 1
                                                        }
                                 },
        }
        """
        self.xbeeID = {} if xbeeID_reg is None else xbeeID_reg
        self.new_address = assign_new_address

        self.serialReceiver = None
        if not (portName is None):
            baudrate = 9600 if baudrate is None else baudrate
            self.serialReceiver = serialReceiver.SerialReceiver(portName, baudrate)

        self.master_address = master_add
        self.broadcast_address = broadcast_address

        """
            Dictionary looks like:
            {
                "1": {
                        "1": {
                                "busy": True,
                                "last_time": time.time(),
                                "movement": 1,
                                'pending': False
                             },
                        "2": {
                                "busy": False,
                                "last_time": time.time(),
                                "movement": 0,
                                'pending': False
                             },
                    },
                "2": {
                        "1": {
                                "busy": True,
                                "last_time": time.time(),
                                "movement": 2,
                                'pending': False
                             }
                    },
            }
       """
        self.active_devices = {}

        """
        Dictionary looks like:
        {
            "1": [1, 2],
            "2": [1, 2],
            "3": [1, 2, 3],
            "4": [1, 2, 3, 4],
            "5": [],
        }
        """
        aux_free_add = {}
        for i in range(len(available_platforms)):
            count_robots = int(available_platforms[i])
            aux_free_add[f"{i + 1}"] = list(range(1, count_robots + 1)) if count_robots > 0 else []

        self.free_add = aux_free_add
        self.inactive_devices = []

        self.list_pending_devices = {}
        self.list_pending_mess = {}

        self.timeout_sign_in = 10
        self.send_again_time = 10
        self.change_flag = False

    def there_are_pending_messages(self):
        return 0 != len(self.list_pending_mess)

    def check_change_flag(self):
        return self.change_flag

    def unset_change_flag(self):
        self.change_flag = False

    def set_serial_configuration(self, portName, baudrate=9600):
        self.serialReceiver = serialReceiver.SerialReceiver(portName, baudrate, self.debug_serial)

    def serialIsSet(self):
        return not (self.serialReceiver is None)

    def run(self):
        # self.debug_serial.write_data('aaaaaaaaaa')
        if self.serialReceiver is None:
            raise ValueError("No serial communication has been set.")

        if not self.serialReceiver.get_started():
            self.serialReceiver.start()

        mes = self.serialReceiver.read_messages()

        if mes is not None:

            if self.check_BFP_message(mes, self.protocol):

                if mes[3] == self.ASSIGNED_SIGN_IN_NUMBER:
                    self.sign_in_process(mes, True)
                elif mes[3] == self.ASSIGNED_PING_NUMBER:
                    self.ping_in_process(mes, True)
                elif mes[3] == self.ASSIGNED_BUSY_NUMBER:
                    self.busy_process(mes, True)
                elif mes[3] == self.ASSIGNED_SIGN_OUT_NUMBER:
                    self.sign_out_process(mes, True)
                elif mes[3] == self.ASSIGNED_MOVE_NUMBER:
                    self.receive_move_packet_process(mes, True)
        else:
            self.check_pending_devices_messages()

    def receive_move_packet_process(self, mes, full_message=False):
        floor, platform = self.parse_move_packet(mes, full_message)

        if self.__check_platform_floor_active__(floor, platform):
            self.active_devices[str(floor)][str(platform)]["last_time"] = time.time()
            type_mov = self.active_devices[str(floor)][str(platform)]["movement"]

            self.send_move_packet_process(type_mov, int(platform), int(floor))

    def add_platform_to_free_add(self, floor, platform):
        if not (floor in self.free_add):
            self.free_add[floor] = {}

        self.free_add[str(floor)].append(platform)
        self.free_add[str(floor)].sort()

    def sign_out_process(self, mes, full_message=False):
        floor, platform = self.parse_sign_out_packet(mes, full_message)

        if self.__check_platform_floor_active__(floor, platform):
            _ = self.active_devices[str(floor)].pop(str(platform))
            self.add_platform_to_free_add(floor, platform)
            self.change_flag = True
        elif platform in self.inactive_devices:
            self.inactive_devices.remove(platform)
            self.change_flag = True

    def busy_process(self, mes, full_message=False):
        floor, platform, busy = self.parse_busy_packet(mes, full_message)

        if platform is not None:
            aux_str = 'busy' if busy else 'free'

            if not (self.debug_serial is None):
                self.debug_serial.write_data(f'Platform nº {platform} in the floor nº {floor} is {aux_str}')
            else:
                print(f'Platform nº {platform} in the floor nº {floor} is {aux_str}')

            self.active_devices[str(floor)][str(platform)]["busy"] = busy
            self.change_flag = True

            if self.__check_message_in_pending__(floor, platform):
                if self.list_pending_mess[str(floor)][str(platform)]["mes"] == self.ASSIGNED_BUSY_NUMBER:
                    _ = self.list_pending_mess[str(floor)].pop(str(platform))
                    self.active_devices[str(floor)][str(platform)]["pending"] = False

                if 0 == len(self.list_pending_mess[str(floor)]):
                    self.list_pending_mess.pop(str(floor))

    def sign_in_process(self, message, full_message=False):
        serialNumberHigh, serialNumberLow = self.parse_sign_in_packet(message, full_message)

        if not (self.debug_serial is None):
            self.debug_serial.write_data(f'NumH: {serialNumberHigh}, NumL: {serialNumberLow}')
        else:
            print(f'NumH: {serialNumberHigh}, NumL: {serialNumberLow}')

        if serialNumberHigh is not None:
            platform = 0
            floor = 0
            active = 0
            new_device = True

            if self.__check_xbee_id_in_pool__(serialNumberHigh, serialNumberLow) and not self.new_address:
                platform = self.xbeeID[str(serialNumberHigh)][str(serialNumberLow)]["n_platform"]
                floor = self.xbeeID[str(serialNumberHigh)][str(serialNumberLow)]["floor"]
                active = self.xbeeID[str(serialNumberHigh)][str(serialNumberLow)]["active"]

                new_device = platform == -1

            if new_device:
                floor, platform, active = self.pick_next_address()

            pack = self.build_sign_in_packet(serialNumberHigh, serialNumberLow, active, floor, platform)

            self.__sending_data__(self.serialReceiver, pack)

            if new_device:
                if not (str(serialNumberHigh) in self.xbeeID):
                    self.xbeeID[str(serialNumberHigh)] = {}

                self.xbeeID[str(serialNumberHigh)][str(serialNumberLow)] = {
                    "n_platform": -1,
                    "floor": -1,
                    "active": active,
                }

                if not (str(floor) in self.list_pending_devices):
                    self.list_pending_devices[str(floor)] = {}

                self.list_pending_devices[str(floor)][str(platform)] = {
                    "high": serialNumberHigh,
                    "low": serialNumberLow,
                    "active": active,
                    "time": time.time(),
                    "retries": 0,
                    "maxRetries": self.defaultMaxRetries
                }

    def send_move_packet_process(self, type_m, platform, floor, pending_flag=False, maxRetries=3, retry_time=None):
        if platform == self.broadcast_address:
            if floor == self.broadcast_address:
                aux_plat = "I will send to all the robots the following info:"
            else:
                aux_plat = f"I will send to all robots in the floor {floor} the data:"
        elif floor == self.broadcast_address:
            aux_plat = f"I will send to all {platform}th robots the following data:"
        else:
            aux_plat = f'I will send to the platform nº {platform} in the floor {floor} the data:'

        if not (self.debug_serial is None):
            self.debug_serial.write_data(aux_plat)
        else:
            print(aux_plat)

        movement_data = load_data.random_generate_data(3, raw_data=(type_m == 5))
        packet = self.build_move_packet_process(type_m, movement_data, platform, floor)

        if not (packet is None):
            self.__sending_data__(self.serialReceiver, packet)

            if int(floor) == self.broadcast_address:
                for fl in self.active_devices.keys():
                    for pl in self.active_devices[fl].keys():
                        if pl == str(platform) or int(platform) == self.broadcast_address:
                            self.__add_movement_information__(fl, pl, type_m, movement_data, pending_flag,
                                                              maxRetries, retry_time)
            elif str(floor) in self.active_devices and int(platform) == self.broadcast_address:
                for pl in self.active_devices[str(floor)].keys():
                    if pl == str(platform) or int(platform) == self.broadcast_address:
                        self.__add_movement_information__(str(floor), pl, type_m, movement_data, pending_flag,
                                                          maxRetries, retry_time)
            elif self.__check_platform_floor_active__(floor, platform):
                self.__add_movement_information__(str(floor), platform, type_m, movement_data, pending_flag,
                                                  maxRetries, retry_time)

    def __add_movement_information__(self, floor, platform, type_movement, movement_data,
                                     pending_flag=False, max_retries=3, retryTime=None):
        self.active_devices[str(floor)][str(platform)]["movement"] = type_movement
        self.active_devices[str(floor)][str(platform)]["pending"] = pending_flag

        if pending_flag:
            if retryTime is None:
                retryTime = self.send_again_time

            if not (str(floor) in self.list_pending_mess):
                self.list_pending_mess[str(floor)] = {}

            self.list_pending_mess[str(floor)][str(platform)] = {
                "mes": self.ASSIGNED_BUSY_NUMBER,
                "time": time.time(),
                "values": {
                    "type": type_movement,
                    "data": movement_data
                },
                "retries": 0,
                "maxRetries": max_retries,
                "send_again_time": retryTime
            }

    def check_busy_device(self, device_add, device_floor):
        ret = None

        if self.__check_platform_floor_active__(device_floor, device_add):
            ret = self.active_devices[str(device_floor)][str(device_add)]["busy"]

        return ret

    def check_pending_devices_messages(self):
        end = False

        if len(self.list_pending_devices) != 0:
            erase_from_pending = []

            for floor in self.list_pending_devices.keys():
                for platform in self.list_pending_devices[floor].keys():

                    selected = self.list_pending_devices[floor][platform]

                    diff_time = time.time() - selected["time"]

                    if diff_time > self.timeout_sign_in:
                        maxRetries = self.list_pending_devices[floor][platform]["maxRetries"]

                        if self.list_pending_devices[floor][platform]["retries"] < maxRetries:
                            pack = self.build_sign_in_packet(selected["high"], selected["low"], selected["active"],
                                                             int(floor), int(platform))

                            if not (self.debug_serial is None):
                                self.debug_serial.write_data(f'Pack: {pack}')
                            else:
                                print(f'Pack: {pack}')

                            self.__sending_data__(self.serialReceiver, pack)

                            self.list_pending_devices[floor][platform]["time"] = time.time()
                            self.list_pending_devices[floor][platform]["retries"] += 1

                            end = True
                            break
                        else:
                            aux = {
                                "selected": selected,
                                "floor": floor,
                                "platform": platform
                            }

                            erase_from_pending.append(aux)

                if end:
                    break

            for efp in erase_from_pending:
                selected = efp["selected"]
                floor = efp["floor"]
                platform = efp["platform"]

                if not (self.debug_serial is None):
                    self.debug_serial.write_data(
                        f"Max retries trying to connect with Xbee: {selected['high']}, {selected['low']}")
                else:
                    print(f"Max retries trying to connect with Xbee: {selected['high']}, {selected['low']}")

                if selected["active"]:
                    self.add_platform_to_free_add(int(floor), int(platform))
                else:
                    self.inactive_devices.remove(int(platform))

                self.list_pending_devices[str(floor)].pop(str(platform))

                if 0 == len(self.list_pending_devices[str(floor)]):
                    self.list_pending_devices.pop(str(floor))

        elif len(self.list_pending_mess) != 0:

            for floor in self.list_pending_mess.keys():
                for platform in self.list_pending_mess[floor].keys():
                    selected = self.list_pending_mess[floor][platform]

                    diff_time = time.time() - selected["time"]

                    if diff_time > self.send_again_time:

                        if selected["mes"] == self.ASSIGNED_BUSY_NUMBER:
                            pack = self.build_move_packet_process(selected["values"]["type"],
                                                                  selected["values"]["data"],
                                                                  int(platform), int(floor))

                            self.__sending_data__(self.serialReceiver, pack)

                        self.list_pending_mess[floor][platform]["time"] = time.time()
                        self.list_pending_mess[floor][platform]["retries"] += 1

                        end = True
                        break

                if end:
                    break

    def ping_in_process(self, message, full_message=False):
        floor, platform = self.parse_ping_packet(message, full_message)

        if floor is not None:

            if not (self.debug_serial is None):
                self.debug_serial.write_data(f'Platform nº {platform} in floor nº {floor} is online.')
            else:
                print(f'Platform nº {platform} in floor nº {floor} is online.')

            if self.__check_device_in_pending__(floor, platform):
                self.activate_from_pending_process(floor, platform)
            elif self.__check_platform_floor_active__(floor, platform):
                self.active_devices[str(floor)][str(platform)]["last_time"] = time.time()

    def activate_from_pending_process(self, floor, platform):
        active = self.list_pending_devices[str(floor)][str(platform)]["active"]
        serialNumberHigh = self.list_pending_devices[str(floor)][str(platform)]["high"]
        serialNumberLow = self.list_pending_devices[str(floor)][str(platform)]["low"]

        if active:
            if not (str(floor) in self.active_devices):
                self.active_devices[str(floor)] = {}

            self.active_devices[str(floor)][str(platform)] = {
                "last_time": time.time(),
                "busy": False,
                "movement": 0,
                "pending": False,
                "unreachable": False
            }

            self.change_flag = True
        else:
            self.inactive_devices.append(platform)
            self.inactive_devices.sort()

        self.xbeeID[str(serialNumberHigh)][str(serialNumberLow)]["floor"] = int(floor)
        self.xbeeID[str(serialNumberHigh)][str(serialNumberLow)]["n_platform"] = int(platform)

        self.list_pending_devices[str(floor)].pop(str(platform))

        if 0 == len(self.list_pending_devices[str(floor)]):
            self.list_pending_devices.pop(str(floor))

    def parse_sign_in_packet(self, message, full_message=False):
        read = 0
        parse_message = True
        serialNumberHigh = None
        serialNumberLow = None

        if full_message:
            parse_message = self.check_BFP_message(message, self.protocol)
            parse_message = parse_message and self.__check_type__(message[3], "sign_in")
            parse_message = parse_message and self.__check_address__(message[4])
            read += 5

        if parse_message:
            serialNumberHigh = self.convert_bytes_uint32_t(message[read:(read + 4)])
            read += 4

            serialNumberLow = self.convert_bytes_uint32_t(message[read:(read + 4)])
            read += 4

        return serialNumberHigh, serialNumberLow

    def parse_sign_out_packet(self, message, full_message=False):
        read = 0
        parse_message = True
        platform = None
        floor = None

        if full_message:
            parse_message = self.check_BFP_message(message, self.protocol)
            parse_message = parse_message and self.__check_type__(message[3], "sing_out")
            parse_message = parse_message and self.__check_address__(message[4])
            read += 5

        if parse_message:
            floor = message[read]
            read += 1

            platform = message[read]
            read += 1

        return floor, platform

    def parse_move_packet(self, message, full_message=False):
        read = 0
        parse_message = True
        platform = None
        floor = None

        if full_message:
            parse_message = self.check_BFP_message(message, self.protocol)
            parse_message = parse_message and self.__check_type__(message[3], "move_pack")
            parse_message = parse_message and self.__check_address__(message[4])
            read += 5

        if parse_message:
            floor = message[read]
            read += 1

            platform = message[read]
            read += 1

        return floor, platform

    def parse_busy_packet(self, message, full_message=False):
        read = 0
        parse_message = True
        platform = None
        floor = None
        busy = None

        if full_message:
            parse_message = self.check_BFP_message(message, self.protocol)
            parse_message = parse_message and self.__check_type__(message[3], "busy")
            parse_message = parse_message and self.__check_address__(message[4])
            read += 5

        if parse_message:
            floor = message[read]
            read += 1

            platform = message[read]
            read += 1

            busy = bool(message[read])
            read += 1

        return floor, platform, busy

    def parse_ping_packet(self, message, full_message=False):
        read = 0
        parse_message = True
        ping_floor = None
        ping_platform = None

        if full_message:
            parse_message = self.check_BFP_message(message, self.protocol)
            parse_message = parse_message and self.__check_type__(message[3], "ping")
            parse_message = parse_message and self.__check_address__(message[4])
            read += 5

        if parse_message:
            ping_floor = message[read]
            read += 1

            ping_platform = message[read]
            read += 1

        return ping_floor, ping_platform

    def build_sign_in_packet(self, serialNumberHigh, serialNumberLow, active, floor, platform):
        header = self.__build_fixed_message__("sign_in")
        packet = header + struct.pack(self.little_big_endian + 'L L B B B B', serialNumberHigh,
                                      serialNumberLow, self.master_address, int(floor), int(platform), int(active))

        return packet

    def build_ping_packet(self, time_in, dest_platform=None, dest_floor=None):
        header = self.__build_fixed_message__("ping")
        address_part = self.__build_dest_address_part__(dest_platform, dest_floor)
        packet = header + address_part + struct.pack(self.little_big_endian + 'H', time_in)

        return packet

    def build_instruction_packet(self, instruction, instruction_value, dest_platform=None, dest_floor=None):
        header = self.__build_fixed_message__("instruction")
        address_part = self.__build_dest_address_part__(dest_platform, dest_floor)
        packet = header + address_part + struct.pack(self.little_big_endian + 'B B',
                                                     self.instruction_types[instruction], instruction_value)

        return packet

    def build_move_packet_process(self, type_movement, move_info, dest_platform=None, dest_floor=None):
        header = self.__build_fixed_message__("move_pack")
        address_part = self.__build_dest_address_part__(dest_platform, dest_floor)

        data = b''

        for single_data in move_info:
            data = data + struct.pack(self.little_big_endian + 'H B B',
                                      single_data["time"], single_data["chamber"], single_data["iterations"])

        packet = header + address_part + struct.pack(self.little_big_endian + 'B', type_movement) + data

        return packet

    def pick_next_address(self):
        floor, platform = self.__check_space_in_free_device__()
        active = False if floor is None else True

        if not active:
            floor = self.dummy_floor
            size_inactive_devices = len(self.inactive_devices)
            platform = self.inactive_devices[size_inactive_devices - 1] + 1 if size_inactive_devices else 1
            self.inactive_devices.append(platform)
            self.inactive_devices.sort()
        else:
            self.free_add[str(floor)].remove(platform)

        return floor, platform, active

    def __get_one_aspect_active_devices__(self, key, address_platform, address_floor):
        ret = []

        if int(address_floor) == 0xFF:

            for floor in self.active_devices.keys():
                for device in self.active_devices[floor].keys():
                    if int(address_platform) == 0xFF or str(address_platform) == str(device):
                        last_time = self.active_devices[floor][device][key]
                        aux = {"floor": int(floor), "platform": int(device), key: last_time}

                        ret.append(aux)

        elif int(address_platform) == 0xFF and str(address_floor) in self.active_devices:

            for device in self.active_devices[str(address_floor)]:
                last_time = self.active_devices[str(address_floor)][device][key]
                aux = {"floor": int(address_floor), "platform": int(device), key: last_time}

                ret.append(aux)

        elif self.__check_platform_floor_active__(address_floor, address_platform):
            last_time = self.active_devices[str(address_floor)][str(address_platform)][key]
            aux = {"floor": int(address_floor), "platform": int(address_platform), key: last_time}

            ret.append(aux)

        return ret

    def get_last_connection(self, address_platform, address_floor):
        return self.__get_one_aspect_active_devices__("last_time", str(address_platform), str(address_floor))

    def get_busy(self, address_platform, address_floor):
        return self.__get_one_aspect_active_devices__("busy", str(address_platform), str(address_floor))

    def get_movement(self, address_platform, address_floor):
        return self.__get_one_aspect_active_devices__("movement", str(address_platform), str(address_floor))

    def get_active_devices(self):
        return self.active_devices

    def get_xbee_ids(self):
        return self.xbeeID

    def full_reset(self):
        self.reset_xbee_id()
        self.reset_active_devices()
        self.reset_inactive_devices()
        self.reset_list_pending_mess()
        self.reset_list_pending_devices()

    def reset_xbee_id(self):
        self.xbeeID = {}

    def reset_active_devices(self):
        self.active_devices = {}

    def reset_list_pending_mess(self):
        self.list_pending_mess = {}

    def reset_inactive_devices(self):
        self.inactive_devices = {}

    def reset_list_pending_devices(self):
        self.list_pending_devices = {}

    def __build_fixed_message__(self, type_mess):
        return struct.pack('3s B', bytes(self.protocol, "utf-8"), self.types_message[type_mess])

    def __build_dest_address_part__(self, dest_platform=None, dest_floor=None):
        if dest_platform is None:
            dest_platform = self.broadcast_address

        if dest_floor is None:
            dest_floor = self.broadcast_address

        return struct.pack(self.little_big_endian + 'B B B', dest_floor, dest_platform, self.master_address)

    def __check_address__(self, mess):
        check = mess

        return self.broadcast_address == check or self.master_address == check

    def __check_type__(self, mess, type_mess):
        check = mess

        return self.types_message[type_mess] == check

    def terminate(self):
        if not (self.serialReceiver is None):
            self.serialReceiver.terminate_process()

            if self.serialReceiver.get_started():
                self.serialReceiver.join()

            self.serialReceiver.close_port()

    @staticmethod
    def __sending_data__(serialPort, message):
        if serialPort is None:
            raise ValueError("Set the serial before using it")

        serialPort.send_message(message)

    def __del__(self):
        if not (self.serialReceiver is None):
            self.serialReceiver.terminate_process()

            if self.serialReceiver.get_started():
                self.serialReceiver.join()

            self.serialReceiver.close_port()

    @staticmethod
    def __check_two_levels_dic(dic, first_level, second_level):
        ret = False

        if first_level is not None:
            if str(first_level) in dic:
                if str(second_level) in dic[str(first_level)]:
                    ret = True

        return ret

    def __check_platform_floor_active__(self, floor, platform):
        return self.__check_two_levels_dic(self.active_devices, floor, platform)

    def __check_xbee_id_in_pool__(self, high_number, low_number):
        return self.__check_two_levels_dic(self.xbeeID, high_number, low_number)

    def __check_device_in_pending__(self, floor, platform):
        return self.__check_two_levels_dic(self.list_pending_devices, floor, platform)

    def __check_message_in_pending__(self, floor, platform):
        return self.__check_two_levels_dic(self.list_pending_mess, floor, platform)

    def __check_space_in_free_device__(self):
        floor = None
        platform = None

        for f in self.free_add.keys():
            if len(self.free_add[f]):
                platform = self.free_add[f][0]
                floor = int(f)
                break

        return floor, platform

    @staticmethod
    def check_BFP_message(message, protocol):
        check = (message[0:3]).decode("utf-8")

        return protocol == check

    @staticmethod
    def convert_bytes_uint32_t(in_bytes):
        return int.from_bytes(in_bytes, "little")
