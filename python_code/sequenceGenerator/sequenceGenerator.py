import random
import time
from threading import Thread, Lock
import tools.tools_BF as tools_BF
import debugging_functions as bruteForceMaster
# import python_code.tools.tools_BF as tools_BF
# import python_code.debugging_functions as bruteForceMaster
import copy

MINUTES_AFTER_CHECKING_PLATFORMS = 3.5
RETRIES_BEFORE_CONTINUING = 2
maxRetriesSecondSequence = 10
MAX_SEQUENCES = 5
field_available_robots = "available_robots"
field_delays = "delays"
field_all_delays = "all_delays"
field_movement_type = "moves"
field_full_movement_types = "moves_full"
field_retry_time = "retry_time"
field_max_full_rep = "rep"
field_novelty_population = "novelty"
field_print_label_sequence = "print_sequence"
field_erase_label_sequence = "erase_sequence"
field_choose_sequence = "choose_sequence"

step_novelty = True


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
        self.stopped = False
        self.stop_mov = 254
        self.banned_platform = {}
        self.threadingBannedPlatforms = Lock()

        self.sequences_functions = [
            self.first_sequence,
            self.second_sequence,
            self.third_sequence,
            self.forth_sequence,
            self.fifth_sequence
        ]

    def check_robot_in_unavailable(self, floor, robot):
        rc = False

        self.threadingBannedPlatforms.acquire()
        if int(floor) in self.banned_platform:
            if int(robot) in self.banned_platform[floor]:
                rc = True

        self.threadingBannedPlatforms.release()
        
        return rc

    def modify_unavailable_robots_online(self, banned):
        self.threadingBannedPlatforms.acquire()
        self.banned_platform = banned
        self.threadingBannedPlatforms.release()

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

    def delay_no_blocking(self, delay, text=None):
        org_time = time.time()
        print(f"Delay: {delay} {'' if text is None else text}")

        while self.read_executing() and time.time() < (org_time + delay):
            time.sleep(0.1)

    def wait_until_all_finished(self):
        all_free = False
        beginning = time.time()
        count_times_check = 0

        while not all_free and self.read_executing():
            elapsed = time.time() - beginning

            self.master["Lock"].acquire()
            busy = self.master["object"].get_busy(
                self.master["object"].broadcast_address,
                self.master["object"].broadcast_address
            )
            self.master["Lock"].release()

            for b in busy:
                floor = b["floor"]
                rob = b["platform"]
                
                if not self.check_robot_in_unavailable(floor, rob):
                    all_free = not b["busy"]

                    if not all_free:
                        self.delay_no_blocking(1)
                        break

            print(f"elapsed time {elapsed}, waiting until {MINUTES_AFTER_CHECKING_PLATFORMS * 60}, counter: "
                  f"{count_times_check}")

            if elapsed > (MINUTES_AFTER_CHECKING_PLATFORMS * 60):
                beginning = time.time()
                count_times_check += 1

                if self.check_available_platforms(count_times_check):
                    all_free = True

    def check_available_platforms(self, retries):
        self.master["Lock"].acquire()
        busy = self.master["object"].get_busy(
            self.master["object"].broadcast_address,
            self.master["object"].broadcast_address
        )
        self.master["Lock"].release()
        robots = {}
        last_retry = retries >= RETRIES_BEFORE_CONTINUING
        continue_program = False

        for b in busy:
            free = not b["busy"]

            if not free:
                if not(b["floor"] in robots):
                    robots[b["floor"]] = []
                robots[b["floor"]].append(b["platform"])

        print(f"Stuck robots: {robots}")

        if robots is {}:
            continue_program = True

        for floor in robots:
            for robot in robots[floor]:
                self.master["Lock"].acquire()
                self.master["object"].send_move_packet_process(
                    0,
                    robot,
                    floor,
                )
                self.master["Lock"].release()

                self.delay_no_blocking(1 if not last_retry else 2)

        if last_retry:
            self.master["Lock"].acquire()
            busy = self.master["object"].get_busy(
                self.master["object"].broadcast_address,
                self.master["object"].broadcast_address
            )
            self.master["Lock"].release()

            for b in busy:
                free = not b["busy"]

                if not free:
                    continue_program = True
                    floor = b["floor"]
                    rob = b["platform"]

                    self.master["Lock"].acquire()
                    self.master["object"].include_banned_platforms(floor, rob)
                    self.master["Lock"].release()

        return continue_program

    def first_sequence(self):
        print("First")
        if 0 == len(self.options_copy):
            raise ValueError(f'Before starting fill the options')

        min_delay, max_delay, max_count, available_robots, retry_time = self.get_individual_data(1)
        i = 0

        movement = random.choice(self.options_copy[field_movement_type])

        while self.read_executing():
            if i == 0:
                floor, robot = self.__random_novelty_selection_robot_selection__(available_robots, 1)
                available_robots[floor].remove(robot)

                while self.check_robot_in_unavailable(floor, robot):
                    floor, robot = self.__random_novelty_selection_robot_selection__(available_robots, 1)
                    available_robots[floor].remove(robot)

                delay = self.__select_delay__(min_delay, max_delay, True)

                self.master["Lock"].acquire()
                self.master["object"].send_move_packet_process(
                    movement,
                    robot,
                    floor,
                    pending_flag=True,
                    retry_time=retry_time['first']
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

        min_delay, max_delay, max_count, available_robots, retry_time = self.get_individual_data(2)
        available = self.options_copy[field_available_robots]
        max_len = 0

        for k in available.keys():
            aux = len(available[k])

            if aux > max_len:
                max_len = aux

        available_columns = [(i + 1) for i in range(max_len)]
        self.random_second_sequence(min_delay, max_delay, retry_time, available_columns)

    def random_second_sequence(self, min_delay, max_delay, retry_time, available_columns):
        i = 0

        all_busy = False
        delay = 0
        init_time = 0
        robot = 0
        count_times_check = 0

        movement = random.choice(self.options_copy[field_movement_type])
        beginning = 0
        beginning_all_busy = 0

        while self.read_executing():
            if i == 0:
                all_busy = False

                robot = random.choice(available_columns)
                available_columns.remove(robot)

                self.master["Lock"].acquire()
                self.master["object"].send_move_packet_process(
                    movement,
                    robot,
                    self.master["object"].broadcast_address,
                    pending_flag=True,
                    retry_time=retry_time['second'],
                    maxRetries=maxRetriesSecondSequence
                )
                self.master["Lock"].release()

                init_time = time.time()
                delay = self.__select_delay__(min_delay, max_delay, True, step=step_novelty)

                i = 1
            elif i == 1:

                all_received = False
                while not all_received and self.read_executing():
                    self.master["Lock"].acquire()
                    all_received = not self.master["object"].there_are_pending_messages()
                    self.master["Lock"].release()

                    self.delay_no_blocking(1, text="2nd all_received process")

                i = 2
                beginning_all_busy = 0
            elif i == 2:

                if not all_busy:
                    if beginning_all_busy == 0:
                        beginning_all_busy = time.time()

                    elapsed = time.time() - beginning_all_busy

                    if elapsed > (3 * 60):
                        self.set_executing(0)                        
                        
                    self.master["Lock"].acquire()
                    busy = self.master["object"].get_busy(robot, self.master["object"].broadcast_address)
                    self.master["Lock"].release()

                    all_busy = True

                    for b in busy:
                        all_busy = b["busy"]

                        if not all_busy:
                            self.delay_no_blocking(1, text="2nd all_busy process")
                            break

                if all_busy and time.time() > (init_time + delay):
                    if len(available_columns):
                        i = 0
                    else:
                        self.delay_no_blocking(3, text="2nd wait and step further")
                        i = 3

            elif i == 3:

                if beginning == 0:
                    beginning = time.time()

                elapsed = time.time() - beginning

                if elapsed > (MINUTES_AFTER_CHECKING_PLATFORMS * 60):
                    beginning = time.time()
                    count_times_check += 1
                    if self.check_available_platforms(count_times_check):
                        self.set_executing(0)
                        break

                self.master["Lock"].acquire()
                busy = self.master["object"].get_busy(0xFF, self.master["object"].broadcast_address)
                self.master["Lock"].release()

                all_busy = True
                for b in busy:

                    floor = b["floor"]
                    rob = b["platform"]
                    
                    if not self.check_robot_in_unavailable(floor, rob):
                        all_busy = b["busy"]

                        if all_busy:
                            self.delay_no_blocking(1, text="2nd last checking")
                            print(elapsed)
                            print(MINUTES_AFTER_CHECKING_PLATFORMS * 60)
                            break

                if not all_busy:
                    self.set_executing(0)

    def third_sequence(self):
        print("Third")
        if 0 == len(self.options_copy):
            raise ValueError(f'Before starting fill the options')

        min_delay, max_delay, max_count, available_robots, retry_time = self.get_individual_data(3)

        i = 0
        delay = 0
        floor = 0
        counts = 0

        movement = random.choice(self.options_copy[field_movement_type])

        while self.read_executing():
            if i == 0:
                delay = self.__select_delay__(min_delay, max_delay, False)

                if self.novelty_pop is None:
                    floor = random.choice(list(available_robots))
                else:
                    _, _, aux_floor = self.novelty_pop.transform_genome_into_usable_data(len(available_robots),
                                                                                         sequence=3,
                                                                                         store_next_genome=True,
                                                                                         step=step_novelty)
                    floor = list(available_robots.keys())[int(aux_floor)]

                self.master["Lock"].acquire()
                self.master["object"].send_move_packet_process(
                    movement,
                    0xFF,
                    floor,
                    pending_flag=True,
                    retry_time=retry_time['third']
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

        min_delay, max_delay, max_count, available_robots, retry_time = self.get_individual_data(4)
        beginning = 0
        count_times_check = 0

        while self.read_executing():
            allFree = True

            if already_selected == available_robots:
                if beginning == 0:
                    beginning = time.time()

                elapsed = time.time() - beginning

                if elapsed > (MINUTES_AFTER_CHECKING_PLATFORMS * 60):
                    beginning = time.time()
                    count_times_check += 1
                    if self.check_available_platforms(count_times_check):
                        self.set_executing(0)
                        break

            self.master["Lock"].acquire()
            busy_devices = self.master["object"].get_busy(0xFF, 0xFF)
            self.master["Lock"].release()

            for device in busy_devices:
                floor = device["floor"]
                rob = device["platform"]
                
                if not self.check_robot_in_unavailable(floor, rob):
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
                                    print(len(self.options_copy[field_movement_type]))
                                    _, _, aux_mov = self.novelty_pop.transform_genome_into_usable_data(
                                        len(self.options_copy[field_movement_type]),
                                        sequence=4,
                                        store_next_genome=True,
                                        step=step_novelty
                                    )
                                    print(aux_mov)
                                    print(self.options_copy[field_movement_type])

                                    movement = self.options_copy[field_movement_type][aux_mov]

                                self.master["Lock"].acquire()
                                self.master["object"].send_move_packet_process(movement,
                                                                               device["platform"],
                                                                               device["floor"],
                                                                               pending_flag=True,
                                                                               retry_time=retry_time['fourth'],
                                                                               maxRetries=999)
                                self.master["Lock"].release()

                                self.delay_no_blocking(0.1)
                                allFree = False

                        else:
                            allFree = False

                if not self.read_executing():
                    break

            self.delay_no_blocking(4)

            if allFree and already_selected == available_robots:
                break

        self.set_executing(0)

    def fifth_sequence(self):
        print("fifth")

        def choose_one_from_a_place_in_b(dic_a, dic_b):
            print(dic_a)
            print(dic_b)
            floor_i = random.choice(list(dic_a))
            robot_i = random.choice(dic_a[floor_i])

            dic_a[floor_i].remove(robot_i)

            if not len(dic_a[floor_i]):
                dic_a.pop(floor_i)

            if not (floor_i in dic_b):
                dic_b[floor_i] = []

            dic_b[floor_i].append(robot_i)

            return dic_a, dic_b

        if 0 == len(self.options_copy):
            raise ValueError(f'Before starting fill the options')

        min_delay, max_delay, max_count, available_robots, retry_time = self.get_individual_data(5)

        i = 0
        active_robots = {}
        max_steps = 5

        movement = random.choice(self.options_copy[field_movement_type])

        while self.read_executing() and i < max_steps:
            if self.novelty_pop is None:
                add = 0.5 > random.random()
            else:
                _, _, add = self.novelty_pop.transform_genome_into_usable_data(None, sequence=5,
                                                                               store_next_genome=True,
                                                                               step=step_novelty)
            add = True
            if len(active_robots):
                if add:
                    if len(available_robots):

                        available_robots, active_robots = choose_one_from_a_place_in_b(available_robots, active_robots)
                else:
                    active_robots, available_robots = choose_one_from_a_place_in_b(active_robots, available_robots)

            if not len(active_robots):
                available_robots, active_robots = choose_one_from_a_place_in_b(available_robots, active_robots)

            # send the signal and wait until all of them has finished.
            print(active_robots)
            print(available_robots)
            print(f"total robots: {len(active_robots)}")
            print(f"available: {len(available_robots)}")
            for floor in active_robots:
                for robot in active_robots[floor]:
                    self.master["Lock"].acquire()
                    self.master["object"].send_move_packet_process(
                        movement,
                        robot,
                        floor,
                        pending_flag=True,
                        retry_time=retry_time['fifth'],
                        maxRetries=999
                    )
                    self.master["Lock"].release()

                    self.delay_no_blocking(0.1)

            all_received = False
            while not all_received and self.read_executing():
                self.master["Lock"].acquire()
                all_received = not self.master["object"].there_are_pending_messages()
                self.master["Lock"].release()

                self.delay_no_blocking(3)

            all_busy = True
            beginning = 0
            count_retries = 0
            print("self.read_executing()")
            print(self.read_executing())
            while all_busy and self.read_executing():

                if beginning == 0:
                    beginning = time.time()

                elapsed = time.time() - beginning

                if elapsed > (MINUTES_AFTER_CHECKING_PLATFORMS * 60):
                    beginning = time.time()
                    count_retries += 1
                    self.check_available_platforms(count_retries)

                for floor in active_robots:
                    for robot in active_robots[floor]:
                        self.master["Lock"].acquire()
                        busy_device = self.master["object"].get_busy(robot, floor)[0]
                        self.master["Lock"].release()

                        all_busy = busy_device["busy"]

                if all_busy:
                    self.delay_no_blocking(2)
                else:
                    i += 1
                    print(f"iteration nº {i}")

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

        if self.stopped:
            self.stopped = False

            self.threadingSafe["Lock"].acquire()
            self.threadingSafe["value"] = 254
            self.threadingSafe["Lock"].release()

            self.master["Lock"].acquire()
            self.master["object"].send_move_packet_process(
                self.stop_mov,
                0xFF,
                0xFF,
                pending_flag=True,
                retry_time=self.options_copy[field_retry_time]['stop'],
                maxRetries=4
            )
            self.master["Lock"].release()

            if tools_BF.USE_THREAD:
                all_received = False
                while not all_received:
                    self.master["Lock"].acquire()
                    all_received = not self.master["object"].there_are_pending_messages()
                    self.master["Lock"].release()

                    self.delay_no_blocking(1)

                all_busy = True
                while all_busy:
                    self.master["Lock"].acquire()
                    busy = self.master["object"].get_busy(0xFF, self.master["object"].broadcast_address)
                    self.master["Lock"].release()

                    for b in busy:
                        all_busy = b["busy"]

                        if all_busy:
                            self.delay_no_blocking(2)
                            break

            self.threadingSafe["Lock"].acquire()
            self.threadingSafe["value"] = 0
            self.threadingSafe["Lock"].release()

    def run_continue_sequences(self):
        while self.read_sequences_executing():
            selectedSequence = self.functions[field_choose_sequence]()
            self.set_executing(selectedSequence)
            self.options_copy[field_movement_type] = self.options_copy[field_full_movement_types][selectedSequence]
            self.run_sequence_print_it(selectedSequence)
            self.options_copy = copy.deepcopy(self.options)

    def run_sequence(self, options, functions, homeThreadingSafe, selectedSequence=None):
        if not (None is self.threading):
            if self.threading.is_alive():
                print(f'Before starting another sequence close the opened one.')
                raise ValueError(f'Before starting another sequence close the opened one.')

        if not (selectedSequence is None):
            if 1 > selectedSequence or MAX_SEQUENCES < selectedSequence:
                print(f'The sequence must be between 1 and {MAX_SEQUENCES}. Please define sequence nº '
                      f'{selectedSequence}')
                raise ValueError(f'The sequence must be between 1 and {MAX_SEQUENCES}. Please define sequence nº '
                                 f'{selectedSequence}')
        self.options = options
        if field_novelty_population in self.options:
            self.novelty_pop = self.options[field_novelty_population]

        self.functions = functions
        self.threadingSafe = homeThreadingSafe

        self.options_copy = copy.deepcopy(self.options)

        if not (selectedSequence is None):
            self.threading = Thread(target=self.run_sequence_print_it, args=(selectedSequence,))
            self.set_executing(selectedSequence)
            self.threading.start()
        else:
            self.set_sequences_executing(1)
            self.threading = Thread(target=self.run_continue_sequences)
            self.threading.start()

    def stop_sequence(self, stop_mov, send_stop):
        self.set_sequences_executing(0)
        self.master["Lock"].acquire()
        self.master["object"].reset_list_pending_mess()
        self.master["Lock"].release()

        if self.threading is not None:
            print("Not closed")
            self.stopped = send_stop
            self.stop_mov = stop_mov
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

    def get_individual_data(self, sequence):
        max_delay = self.options_copy[field_all_delays][str(sequence)]["max_delay"]
        min_delay = self.options_copy[field_all_delays][str(sequence)]["min_delay"]
        max_count = self.options_copy[field_max_full_rep]
        available_robots = self.options_copy[field_available_robots]
        print(f"available_robots, {available_robots}")
        timeout_retry = self.options_copy[field_retry_time]

        return min_delay, max_delay, max_count, available_robots, timeout_retry

    def __select_delay__(self, min_delay, max_delay, store_next=False, step=False, smax=False):
        if self.novelty_pop is None:
            delay = round(random.uniform(min_delay, max_delay), 2)
        else:
            delay = self.novelty_pop.transform_delta_value_delay(max_delay, min_delay, store_next, step=step,
                                                                 selectMax=smax)
        # Redundant but just as a security measure
        if delay > max_delay:
            delay = max_delay
        elif delay < min_delay:
            delay = min_delay

        return delay

    def __random_novelty_selection_robot_selection__(self, available, sequence):

        if self.novelty_pop is None:
            floor = random.choice(list(available))
            robot = random.choice(available[floor])

        else:
            print(sequence)
            _, _, selected_fl = self.novelty_pop.transform_genome_into_usable_data(len(list(available)),
                                                                                   sequence=sequence,
                                                                                   store_next_genome=False,
                                                                                   step=False)
            floor = list(available)[selected_fl]
            print(f"first move, floor selected {floor}")

            _, _, selected_rob = self.novelty_pop.transform_genome_into_usable_data(len(list(available[floor])),
                                                                                    sequence=sequence,
                                                                                    store_next_genome=False,
                                                                                    step=True)
            robot = list(available[floor])[selected_rob]

        return floor, robot

    @staticmethod
    def __check_two_levels_in_dictionary__(dic, firstLevel, secondLevel):
        ret_val = False

        if firstLevel in dic:
            if secondLevel in dic[firstLevel]:
                ret_val = True

        return ret_val

    def __del__(self):
        if self.threading is not None:
            self.stop_sequence(254, False)


if __name__ == '__main__':

    def write_ongoing_sequence(sequence_ongoing):
        print(f"Start sequence nº {sequence_ongoing}")


    def erase_ongoing_label(sequence_ongoing):
        print(f"Stop sequence nº {sequence_ongoing}")


    def __chose_sequence__():
        value = {
            1: [1, 2, 3],
            2: [1, 2, 3],
            3: [1, 2, 3],
            4: [1, 2, 3],
            5: [1, 2, 3],
        }
        return random.choice(list(value))


    retry_times = {
        'first': 2,
        'second': 2,
        'third': 2,
        'fourth': 2,
        'fifth': 2,
        'stop': 0.2,
    }

    # charge_excels()
    data_aux = {
        field_available_robots: {1: [1, 2], 2: [1, 2], 3: [1, 2, 3]},
        field_all_delays: {
            "1": {
                "max_delay": 12.0,
                "min_delay": 6.0
            },
            "2": {
                "max_delay": 14.0,
                "min_delay": 3.0
            },
            "3": {
                "max_delay": 19.0,
                "min_delay": 2.0
            },
            "4": {
                "max_delay": 10.0,
                "min_delay": 3.0
            },
            "5": {
                "max_delay": 18.0,
                "min_delay": 6.0
            }
        },
        field_movement_type: [1, 2, 3],
        field_max_full_rep: 1,
        field_retry_time: retry_times,
        field_full_movement_types: {
            1: [1, 2, 3],
            2: [1, 2, 3],
            3: [1, 2, 3],
            4: [1, 2, 3],
            5: [1, 2, 3],
        }
    }

    functions_aux = {
        field_print_label_sequence: write_ongoing_sequence,
        field_erase_label_sequence: erase_ongoing_label,
        field_choose_sequence: __chose_sequence__
    }

    master = {
        "object": bruteForceMaster.BruteForceMaster(data_aux, tools_BF.baud_arduino, 'COM7'),
        "Lock": Lock()
    }

    modify_home_frame = {
        "value": 0,
        "last_value": 0,
        "printed": False,
        "Lock": Lock()
    }
    # print(master["object"].get_active_devices())

    sequence = SequenceGenerator(master)

    sequence.run_sequence(data_aux, functions_aux, modify_home_frame, 4)
    try:
        while sequence.executing:
            master["object"].run()
            time.sleep(10)
    except KeyboardInterrupt:
        print("+++++++++++++++++++++++++++++++")
        sequence.stop_sequence(254, False)
    except Exception as e:
        print("--------------------------------")
        print(e)
        print("--------------------------------")
        sequence.stop_sequence(254, False)
