import random
import time
from threading import Thread, Lock
import tools_BF
import debugging_functions as bruteForceMaster
import copy

MAX_SEQUENCES = 5
field_available_robots = "available_robots"
field_delays = "delays"
field_movement_type = "moves"
field_max_full_rep = "rep"
field_novelty_population = "novelty"
field_print_label_sequence = "print_sequence"
field_erase_label_sequence = "erase_sequence"
field_choose_sequence = "choose_sequence"


class SequenceGenerator:
    def __init__(self, master):
        self.master = master
        self.options = {}
        self.options_copy = {}
        self.sequences_executing = 0
        self.lock_sequences_executing = Lock()
        self.executing = 0
        self.lock_executing = Lock()
        self.threading = None
        self.novelty_pop = None
        self.functions = None
        self.threadingSafe = None

        self.sequences_functions = [
            self.first_sequence,
            self.second_sequence,
            self.third_sequence,
            self.forth_sequence,
            self.fifth_sequence
        ]

    def read_executing(self):
        self.lock_executing.acquire()
        ret = self.executing
        self.lock_executing.release()

        return ret

    def read_sequences_executing(self):
        self.lock_sequences_executing.acquire()
        ret = self.sequences_executing
        self.lock_sequences_executing.release()

        return ret

    def set_executing(self, val):
        self.lock_executing.acquire()
        self.executing = val
        self.lock_executing.release()

    def set_sequences_executing(self, val):
        self.lock_sequences_executing.acquire()
        self.sequences_executing = val
        self.lock_sequences_executing.release()

    def delay_no_blocking(self, delay):
        org_time = time.time()
        print(f"Delay: {delay}")

        while self.read_executing() and time.time() < (org_time + delay):
            time.sleep(0.1)

    def wait_until_all_finished(self):
        all_free = False

        while not all_free and self.read_executing():
            self.master["Lock"].acquire()
            busy = self.master["object"].get_busy(
                self.master["object"].broadcast_address,
                self.master["object"].broadcast_address
            )
            self.master["Lock"].release()

            for b in busy:
                all_free = not b["busy"]

                if not all_free:
                    self.delay_no_blocking(1)
                    break

    def first_sequence(self):
        print("First")
        if 0 == len(self.options_copy):
            raise ValueError(f'Before starting fill the options')

        min_delay, max_delay, max_count, available_robots = self.get_individual_data()
        i = 0

        while self.read_executing():
            if i == 0:
                floor = random.choice(list(available_robots))
                robot = random.choice(available_robots[floor])
                available_robots[floor].remove(robot)

                movement = random.choice(self.options_copy[field_movement_type])

                delay = self.__select_delay__(min_delay, max_delay, True)

                self.master["Lock"].acquire()
                self.master["object"].send_move_packet_process(
                    movement,
                    robot,
                    floor,
                    pending_flag=True,
                    retry_time=2
                )
                self.master["Lock"].release()

                self.delay_no_blocking(delay)

                if 0 == len(available_robots[floor]):
                    available_robots.pop(floor)

                if 0 == len(available_robots):
                    self.wait_until_all_finished()
                    break

        self.set_executing(0)

    def second_sequence(self):
        if 0 == len(self.options_copy):
            raise ValueError(f'Before starting fill the options')

        min_delay, max_delay, max_count, available_robots = self.get_individual_data()
        available = self.options_copy[field_available_robots]
        max_len = 0

        for k in available.keys():
            aux = len(available[k])

            if aux > max_len:
                max_len = aux

        i = 0

        if self.novelty_pop is None:
            right = True
        else:
            _, _, right = self.novelty_pop.transform_genome_into_usable_data(None, sequence=2, store_next_genome=True)

        robot = 1 if right else max_len
        all_busy = False
        delay = 0
        init_time = 0

        print("I'm starting from the right" if right else "I'm starting from the left")

        while self.read_executing():
            if i == 0:
                all_busy = False

                movement = random.choice(self.options_copy[field_movement_type])
                self.master["Lock"].acquire()
                self.master["object"].send_move_packet_process(
                    movement,
                    robot,
                    self.master["object"].broadcast_address,
                    pending_flag=True,
                    retry_time=3
                )
                self.master["Lock"].release()

                init_time = time.time()
                delay = self.__select_delay__(min_delay, max_delay, True)

                i = 1
            elif i == 1:

                all_received = False
                while not all_received and self.read_executing():
                    self.master["Lock"].acquire()
                    all_received = not self.master["object"].there_are_pending_messages()
                    self.master["Lock"].release()

                    self.delay_no_blocking(1)

                if not all_busy:
                    self.master["Lock"].acquire()
                    busy = self.master["object"].get_busy(robot, self.master["object"].broadcast_address)
                    self.master["Lock"].release()

                    all_busy = True

                    for b in busy:
                        all_busy = b["busy"]

                        if not all_busy:
                            self.delay_no_blocking(1)
                            break

                if all_busy and time.time() > (init_time + delay):
                    if right and robot == max_len or (not right and robot == 1):
                        i = 2
                        self.delay_no_blocking(3)
                    else:
                        i = 0
                        robot = robot + 1 if right else robot - 1

            elif i == 2:

                self.master["Lock"].acquire()
                busy = self.master["object"].get_busy(robot, self.master["object"].broadcast_address)
                self.master["Lock"].release()

                all_busy = True
                for b in busy:
                    all_busy = b["busy"]

                    if all_busy:
                        self.delay_no_blocking(1)
                        break

                if not all_busy:
                    self.set_executing(0)

    def third_sequence(self):
        print("Third")
        if 0 == len(self.options_copy):
            raise ValueError(f'Before starting fill the options')

        min_delay, max_delay, max_count, available_robots = self.get_individual_data()

        i = 0
        delay = 0
        floor = 0
        counts = 0

        while self.read_executing():
            if i == 0:
                delay = self.__select_delay__(min_delay, max_delay, False)

                if self.novelty_pop is None:
                    floor = random.choice(list(available_robots))
                else:
                    _, _, aux_floor = self.novelty_pop.transform_genome_into_usable_data(len(available_robots),
                                                                                         sequence=3,
                                                                                         store_next_genome=True)
                    floor = list(available_robots.keys())[int(aux_floor)]

                movement = random.choice(self.options_copy[field_movement_type])

                self.master["Lock"].acquire()
                self.master["object"].send_move_packet_process(
                    movement,
                    0xFF,
                    floor,
                    pending_flag=True,
                    retry_time=2
                )
                self.master["Lock"].release()

                i = 1
            elif i == 1:
                self.delay_no_blocking(delay)
                i = 2
            elif i == 2:
                available_robots.pop(floor)

                if 0 == len(available_robots):
                    self.wait_until_all_finished()
                    counts += 1
                    break

                i = 0

        self.set_executing(0)

    def forth_sequence(self):
        print("Forth")
        already_selected = {}

        min_delay, max_delay, max_count, available_robots = self.get_individual_data()
        self.master["Lock"].acquire()
        self.master["object"].send_move_packet_process(1, 0xFF, 0xFF)
        self.master["Lock"].release()

        all_received = False
        while not all_received and self.read_executing():
            self.master["Lock"].acquire()
            all_received = not self.master["object"].there_are_pending_messages()
            self.master["Lock"].release()

            self.delay_no_blocking(1)

        while self.read_executing():
            allFree = True

            self.master["Lock"].acquire()
            busy_devices = self.master["object"].get_busy(0xFF, 0xFF)
            self.master["Lock"].release()

            for device in busy_devices:
                if self.__check_two_levels_in_dictionary__(available_robots, device["floor"], device["platform"]):
                    if not device["busy"]:

                        if not (
                                self.__check_two_levels_in_dictionary__(already_selected,
                                                                        device["floor"],
                                                                        device["platform"]
                                                                        )
                        ):

                            if not (device["floor"] in already_selected):
                                already_selected[device["floor"]] = []

                            already_selected[device["floor"]].append(device["platform"])

                            if self.novelty_pop is None:
                                movement = random.choice(self.options_copy[field_movement_type])
                            else:
                                _, _, aux_mov = self.novelty_pop.transform_genome_into_usable_data(
                                    len(self.options_copy[field_movement_type]),
                                    sequence=4,
                                    store_next_genome=True
                                )
                                movement = self.options_copy[field_movement_type][aux_mov]

                            self.master["Lock"].acquire()
                            self.master["object"].send_move_packet_process(movement,
                                                                           device["platform"],
                                                                           device["floor"],
                                                                           pending_flag=True,
                                                                           retry_time=3)
                            self.master["Lock"].release()

                            self.delay_no_blocking(0.2)
                            allFree = False

                    else:
                        allFree = False

                if not self.read_executing():
                    break

                if allFree and already_selected == available_robots:
                    break

            self.delay_no_blocking(4)

        self.set_executing(0)

    def fifth_sequence(self):
        print("fifth")

        def choose_one_from_a_place_in_b(dic_a, dic_b):
            floor_i = random.choice(dic_a)
            robot_i = random.choice(dic_a[floor_i])

            dic_a[floor_i].remove(robot_i)

            if not len(dic_a[floor_i]):
                dic_a.remove(floor_i)

            if not (floor_i in dic_b):
                dic_b[floor_i] = []

            dic_b[floor_i].append(robot_i)

            return dic_a, dic_b

        if 0 == len(self.options_copy):
            raise ValueError(f'Before starting fill the options')

        min_delay, max_delay, max_count, available_robots = self.get_individual_data()

        i = 0
        active_robots = {}
        max_steps = 5

        while self.read_executing() and i < max_steps:
            if self.novelty_pop is None:
                add = 0.5 > random.random()
            else:
                _, _, add = self.novelty_pop.transform_genome_into_usable_data(None, sequence=5, store_next_genome=True)

            if len(active_robots):
                if add and len(available_robots):
                    available_robots, active_robots = choose_one_from_a_place_in_b(available_robots, active_robots)
                else:
                    active_robots, available_robots = choose_one_from_a_place_in_b(active_robots, available_robots)

            if not len(active_robots):
                available_robots, active_robots = choose_one_from_a_place_in_b(available_robots, active_robots)

            # send the signal and wait until all of them has finished.
            movement = random.choice(self.options_copy[field_movement_type])

            for floor in active_robots:
                for robot in active_robots[floor]:
                    self.master["Lock"].acquire()
                    self.master["object"].send_move_packet_process(
                        movement,
                        robot,
                        floor,
                        pending_flag=True,
                        retry_time=2
                    )
                    self.master["Lock"].release()

            all_received = False
            while not all_received and self.read_executing():
                self.master["Lock"].acquire()
                all_received = not self.master["object"].there_are_pending_messages()
                self.master["Lock"].release()

                self.delay_no_blocking(3)

            all_busy = True
            while all_busy and self.read_executing():
                for floor in active_robots:
                    for robot in active_robots[floor]:
                        self.master["Lock"].acquire()
                        busy_device = self.master["object"].get_busy(robot, floor)[0]
                        self.master["Lock"].release()

                        all_busy = busy_device["busy"]

                if all_busy:
                    self.delay_no_blocking(2)

            i += 1

        self.set_executing(0)

    def run_sequence_print_it(self, selectedSequence):
        print("run_sequence_print_it")

        self.threadingSafe["Lock"].acquire()
        self.threadingSafe["value"] = selectedSequence
        self.threadingSafe["Lock"].release()

        self.sequences_functions[selectedSequence - 1]()

        self.threadingSafe["Lock"].acquire()
        self.threadingSafe["value"] = 0
        self.threadingSafe["Lock"].release()

    def run_continue_sequences(self):
        while self.read_sequences_executing():
            selectedSequence = self.functions[field_choose_sequence]()
            self.run_sequence_print_it(selectedSequence)

    def run_sequence(self, options, functions, homeThreadingSafe, selectedSequence=None):
        if not (None is self.threading):
            if self.threading.is_alive():
                raise ValueError(f'Before starting another sequence close the opened one.')

        if 1 > selectedSequence or MAX_SEQUENCES < selectedSequence and not (selectedSequence is None):
            raise ValueError(f'The sequence must be between 1 and {MAX_SEQUENCES}. Please define sequence nº '
                             f'{selectedSequence}')
        print("run_sequence")
        self.options = options
        if field_novelty_population in self.options:
            self.novelty_pop = self.options[field_novelty_population]
        print("run_sequence2")

        self.functions = functions
        self.threadingSafe = homeThreadingSafe

        self.options_copy = copy.deepcopy(self.options)
        print("run_sequence3")

        if not (selectedSequence is None):
            print("not(selectedSequence is None)")
            self.threading = Thread(target=self.run_sequence_print_it, args=(selectedSequence,))
            self.set_executing(selectedSequence)
            self.threading.start()
        else:
            self.set_sequences_executing(1)
            self.threading = Thread(target=self.run_continue_sequences)
            self.set_executing(255)
            self.threading.start()

    def stop_sequence(self):
        self.set_sequences_executing(0)

        if self.threading is not None:
            print("Not closed")
            self.set_executing(0)
            self.threading.join()
            self.threading = None

    def transform_available_mov_second_sequence(self, makeCopy=False):
        if makeCopy:
            self.deep_copy_available_robots()

        available = self.options_copy[field_available_robots]
        aux_available_robots = {}

        for key in available.keys():
            aux_available_robots[key] = {}
            aux_available_robots[key]["available"] = available[key]
            aux_available_robots[key]["robot"] = 0
            aux_available_robots[key]["finished"] = True

        return aux_available_robots

    def deep_copy_available_robots(self):
        self.options_copy = copy.deepcopy(self.options)
        return self.options_copy[field_available_robots]

    def get_individual_data(self):
        min_delay, max_delay = self.options_copy[field_delays]
        max_count = self.options_copy[field_max_full_rep]
        available_robots = self.options_copy[field_available_robots]

        return min_delay, max_delay, max_count, available_robots

    def __select_delay__(self, min_delay, max_delay, store_next=False, step=False, smax=False):
        if self.novelty_pop is None:
            delay = round(random.uniform(min_delay, max_delay), 2)
        else:
            delay = self.novelty_pop.transform_delta_value_delay(max_delay, min_delay, store_next, step=step,
                                                                 selectMax=smax)

        return delay

    @staticmethod
    def __check_two_levels_in_dictionary__(dic, firstLevel, secondLevel):
        ret_val = False

        if firstLevel in dic:
            if secondLevel in dic[firstLevel]:
                ret_val = True

        return ret_val

    def __del__(self):
        if self.threading is not None:
            self.stop_sequence()


if __name__ == '__main__':
    # charge_excels()
    data_aux = {
        field_available_robots: {1: [1, 2], 2: [1, 2], 3: [1, 2, 3]},
        field_delays: [0.1, 10],
        field_movement_type: [1, 2, 3],
        field_max_full_rep: 2
    }
    master = {
        "object": bruteForceMaster.BruteForceMaster(tools_BF.baud_arduino, 'COM7', data_aux),
        "Lock": Lock()
    }
    # print(master["object"].get_active_devices())

    sequence = SequenceGenerator(master)

    sequence.run_sequence(2, data_aux)
    try:
        while sequence.executing:
            continue
    except KeyboardInterrupt:
        sequence.stop_sequence()
    except Exception as _:
        sequence.stop_sequence()
