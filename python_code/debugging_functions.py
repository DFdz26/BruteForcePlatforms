import time
import copy
import random

field_available_robots = "available_robots"
field_delays = "delays"
field_movement_type = "moves"
field_max_full_rep = "rep"
second_movement = True


class BruteForceMaster:
    def __init__(self, available_platforms, baudrate, portName, master_add=0, broadcast_address=0xFF):
        self.available_final = [{"floor": 1, "platform": 1, "busy": True},
                                {"floor": 1, "platform": 2, "busy": True},
                                {"floor": 2, "platform": 1, "busy": True},
                                {"floor": 2, "platform": 2, "busy": True},
                                {"floor": 3, "platform": 1, "busy": True},
                                {"floor": 3, "platform": 2, "busy": True},
                                {"floor": 3, "platform": 3, "busy": True},
                                ]
        self.available_send_1 = [{"floor": 1, "platform": 1, "busy": True},
                                {"floor": 1, "platform": 2, "busy": True}]

        self.available_send_2 = [{"floor": 2, "platform": 1, "busy": True},
                                {"floor": 2, "platform": 2, "busy": True}]

        self.available_send_3 = [{"floor": 3, "platform": 1, "busy": True},
                                {"floor": 3, "platform": 2, "busy": True},
                                {"floor": 3, "platform": 3, "busy": True}]

        self.avaiable_send = None
        self.once = False
        self.stored_time = 0
        self.floor = 0
        self.active_devices = {}
        self.broadcast_address = 0xFF

        if available_platforms is not None:
            for k in available_platforms[field_available_robots].keys():
                self.active_devices[str(k)] = {}
                for i in available_platforms[field_available_robots][k]:
                    aux_i = str(i)
                    aux_k = str(k)
                    self.active_devices[aux_k][aux_i] = {}
                    self.active_devices[aux_k][aux_i]["busy"] = False
                    self.active_devices[aux_k][aux_i]["last_time"] = 0
                    self.active_devices[aux_k][aux_i]["movement"] = 0
                    self.active_devices[aux_k][aux_i]["pending"] = False

                    if second_movement:
                        self.active_devices[aux_k][aux_i]["once"] = True

    def set_all_platforms(self, value, mov=None):
        for floor in self.active_devices.keys():
            for platforms in self.active_devices[floor].keys():
                self.active_devices[floor][platforms]["busy"] = value

                if mov is not None:
                    self.active_devices[floor][platforms]["movement"] = mov

    def set_time_all_platforms(self, value):
        for floor in self.active_devices.keys():
            for platforms in self.active_devices[floor].keys():
                self.active_devices[floor][platforms]["stored_time"] = value
                time_base = self.active_devices[floor][platforms]["movement"] * 3
                self.active_devices[floor][platforms]["wait"] = random.randint(1, 5) + time_base

    def check_time_all_platforms(self, actual_time):
        for floor in self.active_devices.keys():
            for platforms in self.active_devices[floor].keys():
                diff = actual_time - self.active_devices[floor][platforms]["stored_time"]

                if diff > self.active_devices[floor][platforms]["wait"] and self.active_devices[floor][platforms]["busy"]:
                    self.active_devices[floor][platforms]["busy"] = False
                    print(f"Robot nº {platforms} in floor nº {floor} is free")

    def set_time_all_floor(self, floor, value):
        for platforms in self.active_devices[str(floor)].keys():
            self.active_devices[floor][platforms]["stored_time"] = value
            time_base = self.active_devices[floor][platforms]["movement"] * 3
            self.active_devices[floor][platforms]["wait"] = random.randint(1, 5) + time_base

    def check_time_all_floor(self, floor, actual_time):
        for platforms in self.active_devices[str(floor)].keys():
            diff = actual_time - self.active_devices[floor][platforms]["stored_time"]

            if diff > self.active_devices[floor][platforms]["wait"] and self.active_devices[floor][platforms]["busy"]:
                self.active_devices[floor][platforms]["busy"] = False
                print(f"Robot nº {platforms} in floor nº {floor} is free")

    def set_all_floor(self, floor, value, mov=None):
        for platforms in self.active_devices[str(floor)].keys():
            self.active_devices[str(floor)][platforms]["busy"] = value

            if mov is not None:
                self.active_devices[floor][platforms]["movement"] = mov

    def set_time_specific_robot_all_floor(self, robots, value):
        for floor in self.active_devices.keys():
            for platforms in self.active_devices[floor].keys():
                if int(platforms) == int(robots):
                    self.active_devices[floor][platforms]["stored_time"] = value
                    time_base = self.active_devices[floor][platforms]["movement"] * 3
                    self.active_devices[floor][platforms]["wait"] = random.randint(1, 5) + time_base

    def check_time_specific_robot_all_floor(self, robots, actual_time):
        for floor in self.active_devices.keys():
            for platforms in self.active_devices[floor].keys():
                if int(platforms) == int(robots):
                    diff = actual_time - self.active_devices[floor][platforms]["stored_time"]

                    if diff > self.active_devices[floor][platforms]["wait"] and self.active_devices[floor][platforms]["busy"]:
                        self.active_devices[floor][platforms]["busy"] = False
                        print(f"Robot nº {robots} in floor nº {floor} is free")

    def set_specific_robot_all_floor(self, robots, value, mov=None):
        for floor in self.active_devices.keys():
            for platforms in self.active_devices[floor].keys():
                if int(platforms) == int(robots):
                    self.active_devices[floor][platforms]["busy"] = value

                    if mov is not None:
                        self.active_devices[floor][platforms]["movement"] = mov

    def get_active_devices(self):
        return self.active_devices

    def send_move_packet_process(self, mov, platform, floor):
        platform = str(platform)
        floor = str(floor)
        if int(platform) == self.broadcast_address:
            if int(floor) == self.broadcast_address:
                aux_plat = "I will send to all the robots the following info:"
                self.set_all_platforms(True, mov)
            else:
                aux_plat = f"I will send to all robots in the floor {floor} the data:"
                self.set_all_floor(floor, True, mov)
        elif int(floor) == self.broadcast_address:
            aux_plat = f"I will send to all {platform}th robots the following data:"
            self.set_specific_robot_all_floor(platform, True, mov)
        else:
            aux_plat = f'I will send to the platform nº {platform} in the floor {floor} the data:'
            self.active_devices[floor][platform]["busy"] = True
            self.active_devices[floor][platform]["movement"] = mov

            if second_movement:
                self.active_devices[floor][platform]["once"] = True
        print(aux_plat)
        print(f"Mov: {mov}")

        if not second_movement:
            self.once = True

    def run(self):
        pass

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

        else:
            last_time = self.active_devices[str(address_floor)][str(address_platform)][key]
            aux = {"floor": int(address_floor), "platform": int(address_platform), key: last_time}

            ret.append(aux)

        return ret

    def get_busy(self, platform, floor):
        platform = str(platform)
        floor = str(floor)
        actual_time = time.time()

        if self.once or (second_movement and self.active_devices[floor][platform]["once"]):

            if second_movement:
                if platform != 0xFF:
                    self.active_devices[floor][platform]["once"] = False
                else:
                    for floor1 in self.active_devices.keys():
                        for platforms1 in self.active_devices[floor1].keys():
                            self.active_devices[floor1][platforms1]["once"] = False

            self.once = False

            print("Getting_busy")

            if int(platform) == self.broadcast_address:
                if int(floor) == self.broadcast_address:
                    self.set_time_all_platforms(actual_time)
                else:
                    self.set_time_all_floor(floor, actual_time)
            elif int(floor) == self.broadcast_address:
                self.set_time_specific_robot_all_floor(platform, actual_time)
            else:
                time_base = self.active_devices[floor][platform]["movement"] * 3
                self.active_devices[floor][platform]["stored_time"] = actual_time
                self.active_devices[floor][platform]["wait"] = random.randint(1, 5) + time_base

        if int(platform) == self.broadcast_address:
            if int(floor) == self.broadcast_address:
                self.check_time_all_platforms(actual_time)
            else:
                self.check_time_all_floor(floor, actual_time)
        elif int(floor) == self.broadcast_address:
            self.check_time_specific_robot_all_floor(platform, actual_time)
        else:
            # print(self.active_devices[floor][platform])
            diff = actual_time - self.active_devices[floor][platform]["stored_time"]

            if diff > self.active_devices[floor][platform]["wait"] and self.active_devices[floor][platform]["busy"]:
                self.active_devices[floor][platform]["busy"] = False
                print(f"Robot nº {platform} in floor nº {floor} is free")

        return self.__get_one_aspect_active_devices__("busy", platform, floor)

