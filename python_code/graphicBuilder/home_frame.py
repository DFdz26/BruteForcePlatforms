import threading
import tkinter as tk
import random

from graphicBuilder.parameters_frame import load_parameters_file, get_transformed_data
from graphicBuilder.movements_frame import transform_data_to_dict, load_movements_file, check_available_devices, check_unavailable_devices

from sequenceGenerator.sequenceGenerator import field_available_robots, field_delays, field_max_full_rep, field_movement_type
from sequenceGenerator.sequenceGenerator import SequenceGenerator, field_choose_sequence
from sequenceGenerator.sequenceGenerator import field_print_label_sequence, field_erase_label_sequence, field_novelty_population
from sequenceGenerator.sequenceGenerator import field_retry_time, field_full_movement_types, field_all_delays

import tools.tools_BF as tools_BF


class HomeFrame(tk.Frame):
    def __init__(self, root, show_debug_fn, con, bg_colour, fonts, sizes, master, modify_home_threading,
                 novelty_population=None, retry_timeouts=None):
        super().__init__(con)
        self.max_delay = None
        self.min_delay = None
        self.novelty_population = novelty_population
        self.threadSafe = modify_home_threading
        self.var_send_deflation = tk.IntVar()
        self.running_sequence = False

        self.show_debug_fn = show_debug_fn
        self.retry_timeouts = retry_timeouts

        self.last_selected = 0

        if self.retry_timeouts is None:
            self.retry_timeouts = {
                'first': 0.3,
                'second': 0.3,
                'third': 0.3,
                'fourth': 0.3,
                'fifth': 0.3,
                'stop': 0.3
            }

        self.floor_data = {}
        self.fg_platforms = {
            0: "black",
            1: "green",
            2: "#AB8613",
            3: "red"
        }
        self.text_platforms = {
            0: "X",
            1: "O",
            2: "B",
            3: "E"
        }

        self.sequence_generator = SequenceGenerator(master)

        self.configure(bg=bg_colour)
        self.floor_data_aux, self.delay_dic = load_parameters_file()
        self.floor_data = get_transformed_data(self.floor_data_aux)
        mov, seq = load_movements_file()
        self.movements_available = transform_data_to_dict(mov, seq)

        self.master = master
        self.bg_colour = bg_colour
        self.fonts = fonts
        self.size = sizes
        self.sequence_started = False
        self.label_devices = []

        self.register_frame = None
        self.parameters_frame = None
        self.movements_frame = None

        self.bottom_frame = tk.Frame(self, bg=bg_colour)
        self.label_ongoing_frame = tk.Frame(self, bg=bg_colour)
        self.top_frame = tk.Frame(self, bg=bg_colour)

        self.top_frame.pack(side=tk.TOP, fill="both", expand=True)
        self.bottom_frame.pack(side=tk.BOTTOM, fill="x")
        self.label_ongoing_frame.pack(side=tk.BOTTOM, fill="x")

        self.register_frame_button = tk.Button(self, text="Register/Modify platform", command=self.show_register_frame)
        self.movements_frame_button = tk.Button(self, text="Modify movements", command=self.show_movement_frame)
        self.parameters_frame_button = tk.Button(self, text="Modify parameters", command=self.show_parameters_frame)

        self.show_devices_frame = tk.Frame(self, bg=bg_colour)
        self.show_devices_frame_left = tk.Frame(self, bg=bg_colour)
        self.show_devices_frame_right = tk.Frame(self, bg=bg_colour)

        self.full_devices_data()

        self.label_ongoing = tk.Label(self, text=f"Ongoing", padx=3, pady=4,
                                     font=f"{fonts} {sizes}",
                                     bg=bg_colour)

        start_sequence_button = tk.Button(self, text="Start one sequence", command=self.start_one_sequence)
        start_multiple_sequence_button = tk.Button(self, text="Start multiple sequence", command=self.start_multiple_sequence)
        stop_sequence_button = tk.Button(self, text="Stop sequence", command=self.stop_sequence)
        show_debug = tk.Button(self, text="Logging", command=self.show_debug_fn)

        self.register_frame_button.pack(in_=self.top_frame, pady=4, anchor=tk.CENTER)
        self.movements_frame_button.pack(in_=self.top_frame, pady=4, anchor=tk.CENTER)
        self.parameters_frame_button.pack(in_=self.top_frame, pady=4, anchor=tk.CENTER)
        self.show_devices_frame.pack(in_=self.top_frame, pady=4, fill="both", expand=True)
        self.show_devices_frame_left.pack(in_=self.show_devices_frame, pady=4, fill="y", anchor="nw", side=tk.LEFT)
        self.show_devices_frame_right.pack(in_=self.show_devices_frame, pady=4, fill="both", expand=True, anchor="n",
                                           side=tk.RIGHT)

        start_sequence_button.pack(in_=self.bottom_frame, side=tk.LEFT, pady=30, padx=8)
        start_multiple_sequence_button.pack(in_=self.bottom_frame, side=tk.LEFT, pady=30, padx=8)
        # show_debug.pack(in_=self.bottom_frame, side=tk.LEFT, pady=30, padx=8)
        stop_sequence_button.pack(in_=self.bottom_frame, side=tk.RIGHT, pady=30, padx=8)
        self.check_def = tk.Checkbutton(self, text='Send deflation', variable=self.var_send_deflation, onvalue=1,
                                        offvalue=0)
        self.check_def.pack(in_=self.bottom_frame, side=tk.RIGHT)

    def clear_devices_frame(self):
        for labels in self.label_devices:
            labels.destroy()

        self.label_devices = []

    def full_devices_data(self):
        keys_aux = list(self.floor_data.keys())
        keys_aux.reverse()
        banned_platforms = {}

        for i in keys_aux:
            if len(self.floor_data[i]):
                label_d = tk.Label(self, text=f"Floor {i}", padx=15, pady=4, font=f"{self.fonts} {int(self.size) + 1}",
                                   bg=self.bg_colour)
                label_d.pack(in_=self.show_devices_frame_left)
                self.label_devices.append(label_d)

                show_devices_line = tk.Frame(self, bg=self.bg_colour)

                for j in range(len(self.floor_data[i])):
                    p = self.floor_data[i][j]

                    if p == 3:
                        if not(int(i) in banned_platforms):
                            banned_platforms[int(i)] = []

                        banned_platforms[int(i)].append(int(j))

                    fg = self.fg_platforms[p]
                    aux_text = self.text_platforms[p]
                    label_d = tk.Label(self, text=aux_text, padx=15, pady=4, font=f"{self.fonts} {int(self.size) + 1}",
                                       bg=self.bg_colour, fg=fg)
                    label_d.pack(in_=show_devices_line, anchor="n", side=tk.LEFT)
                    self.label_devices.append(label_d)

                show_devices_line.pack(in_=self.show_devices_frame_right, fill="x", anchor="n")
                self.label_devices.append(show_devices_line)

        if self.running_sequence:
            unavailable = check_unavailable_devices(self.floor_data)
            print(unavailable)
            self.sequence_generator.modify_unavailable_robots_online(unavailable)

    def load_floor_data_from_bfm(self, bfm_active_devices):
        for floor in bfm_active_devices.keys():
            for platform in bfm_active_devices[floor].keys():
                self.floor_data[floor][int(platform) - 1] = 3 if bfm_active_devices[floor][platform]['error'] else 2 if bfm_active_devices[floor][platform]['busy'] else 1

    def refresh_table_from_bfm_data(self, bfm_active_devices):
        self.load_floor_data_from_bfm(bfm_active_devices)
        self.clear_devices_frame()
        self.full_devices_data()

    def forget(self):
        self.pack_forget()

    def show(self, options, floor_data=None, sequence_data=None, dic_delays=None, max_delay=None, min_delay=None, retry_timeouts=None):
        if not(retry_timeouts is None):
            self.retry_timeouts = retry_timeouts

        if floor_data is not None:
            # if floor_data != self.floor_data:
            #     print("changed")
            self.floor_data = floor_data
            self.clear_devices_frame()
            self.full_devices_data()

        if sequence_data is not None:
            self.movements_available = sequence_data

        if max_delay is not None:
            self.max_delay = max_delay
        if min_delay is not None:
            self.min_delay = min_delay

        if dic_delays is not None:
            self.delay_dic = dic_delays

        self.pack(fill="both", expand=True)

    def load_frames(self, register_frame, movement_frame, parameter_frame):
        self.register_frame = register_frame
        self.movements_frame = movement_frame
        self.parameters_frame = parameter_frame

    def show_register_frame(self):
        if self.register_frame is not None:
            self.register_frame.show()

    def show_movement_frame(self):
        if self.movements_frame is not None:
            self.movements_frame.show(None, self.floor_data)

    def show_parameters_frame(self):
        if self.parameters_frame is not None:
            self.parameters_frame.show(None, self.floor_data)

    def __internal_start_sequence__(self, sequence, data_aux):
        if len(self.movements_available):
            # print(self.min_delay)
            if self.sequence_started:
                self.sequence_generator.stop_sequence()

            functions_aux = {
                field_print_label_sequence: self.write_ongoing_sequence,
                field_erase_label_sequence: self.erase_ongoing_label,
                field_choose_sequence: self.__chose_sequence__
            }

            if not(self.novelty_population is None):
                data_aux[field_novelty_population] = self.novelty_population
            if len(data_aux[field_available_robots]):
                self.sequence_generator.run_sequence(data_aux, functions_aux, self.threadSafe, selectedSequence=sequence)

                self.running_sequence = True
        else:
            print("No available movements")

    def start_one_sequence(self):
        available = check_available_devices(self.floor_data)
        sequence = self.__chose_sequence__()

        # if len(available):
        print(self.movements_available[sequence])
        data_aux = {
            field_available_robots: available,
            field_all_delays: self.delay_dic,
            field_movement_type: self.movements_available[sequence],
            field_max_full_rep: 1,
            field_retry_time: self.retry_timeouts
        }

        self.__internal_start_sequence__(sequence, data_aux)

    def start_multiple_sequence(self):
        available = check_available_devices(self.floor_data)

        # if len(available):
        data_aux = {
            field_available_robots: available,
            field_all_delays: self.delay_dic,
            field_full_movement_types: self.movements_available,
            field_max_full_rep: 1,
            field_retry_time: self.retry_timeouts
        }

        self.__internal_start_sequence__(None, data_aux)

    def stop_sequence(self):
        deflation = self.var_send_deflation.get() == 1

        if tools_BF.USE_THREAD:
            if deflation:
                processThread = threading.Thread(target=self.__int_stop_sequence__, args=(1,))
                processThread.start()
            else:
                self.__int_stop_sequence__(0)
        else:
            self.__int_stop_sequence__(deflation)

        # self.erase_ongoing_label()

    def __int_stop_sequence__(self, deflation):
        self.sequence_generator.stop_sequence(254, deflation)

        self.running_sequence = False

    def write_ongoing_sequence(self, sequence):
        self.sequence_started = True
        aux_text = f'sequence nº {sequence}.' if not(sequence in [254, 255]) else 'deflation process.'
        self.label_ongoing.config(text=f"On going {aux_text}")
        self.label_ongoing.pack(in_=self.label_ongoing_frame)

    def erase_ongoing_label(self):
        self.sequence_started = False
        self.label_ongoing.pack_forget()

        self.running_sequence = False

    def get_floor_data(self):
        return self.floor_data

    def __chose_sequence__(self):

        if self.novelty_population is None:
            sequence = self.__chose_random_sequence__(self.movements_available)
        else:
            sequence, _, _ = self.novelty_population.transform_genome_into_usable_data(self.movements_available)

        if len(self.movements_available) > 1:
            while self.last_selected == sequence:
                sequence = self.__chose_random_sequence__(self.movements_available)

        self.last_selected = sequence

        print(f'Selected sequence: {sequence}')

        return sequence

    @staticmethod
    def __chose_mov_in_sequence__(value, sequence, novelty):
        aux = list(value[sequence])
        movement = random.choice(aux)

        return movement

    @staticmethod
    def __chose_random_sequence__(value):
        sequence = random.choice(list(value))

        return sequence

