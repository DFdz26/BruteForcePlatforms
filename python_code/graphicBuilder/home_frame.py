import tkinter as tk
import random

from graphicBuilder.parameters_frame import load_parameters_file, get_transformed_data
from graphicBuilder.movements_frame import transform_data_to_dict, load_movements_file, check_available_devices

from sequenceGenerator.sequenceGenerator import field_available_robots, field_delays, field_max_full_rep, field_movement_type
from sequenceGenerator.sequenceGenerator import SequenceGenerator, field_choose_sequence
from sequenceGenerator.sequenceGenerator import field_print_label_sequence, field_erase_label_sequence, field_novelty_population


class HomeFrame(tk.Frame):
    def __init__(self, con, bg_colour, fonts, sizes, master, modify_home_threading, novelty_population=None):
        super().__init__(con)
        self.novelty_population = novelty_population
        self.threadSafe = modify_home_threading

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
        self.floor_data_aux, self.max_delay, self.min_delay = load_parameters_file()
        self.floor_data = get_transformed_data(self.floor_data_aux)
        mov, seq = load_movements_file()
        self.movements_available = transform_data_to_dict(mov, seq)
        print(self.movements_available)

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


        start_sequence_button = tk.Button(self, text="Start sequence", command=self.start_sequence)
        stop_sequence_button = tk.Button(self, text="Stop sequence", command=self.stop_sequence)

        self.register_frame_button.pack(in_=self.top_frame, pady=4, anchor=tk.CENTER)
        self.movements_frame_button.pack(in_=self.top_frame, pady=4, anchor=tk.CENTER)
        self.parameters_frame_button.pack(in_=self.top_frame, pady=4, anchor=tk.CENTER)
        self.show_devices_frame.pack(in_=self.top_frame, pady=4, fill="both", expand=True)
        self.show_devices_frame_left.pack(in_=self.show_devices_frame, pady=4, fill="y", anchor="nw", side=tk.LEFT)
        self.show_devices_frame_right.pack(in_=self.show_devices_frame, pady=4, fill="both", expand=True, anchor="n",
                                           side=tk.RIGHT)

        start_sequence_button.pack(in_=self.bottom_frame, side=tk.LEFT, pady=30, padx=8)
        stop_sequence_button.pack(in_=self.bottom_frame, side=tk.RIGHT, pady=30, padx=8)

    def clear_devices_frame(self):
        for labels in self.label_devices:
            labels.destroy()

        self.label_devices = []

    def full_devices_data(self):
        for i in self.floor_data.keys():
            if len(self.floor_data[i]):
                label_d = tk.Label(self, text=f"Floor {i}", padx=15, pady=4, font=f"{self.fonts} {int(self.size) + 1}",
                                   bg=self.bg_colour)
                label_d.pack(in_=self.show_devices_frame_left)
                self.label_devices.append(label_d)

                show_devices_line = tk.Frame(self, bg=self.bg_colour)

                for j in range(len(self.floor_data[i])):
                    p = self.floor_data[i][j]
                    fg = self.fg_platforms[p]
                    aux_text = self.text_platforms[p]
                    label_d = tk.Label(self, text=aux_text, padx=15, pady=4, font=f"{self.fonts} {int(self.size) + 1}",
                                       bg=self.bg_colour, fg=fg)
                    label_d.pack(in_=show_devices_line, anchor="n", side=tk.LEFT)
                    self.label_devices.append(label_d)

                show_devices_line.pack(in_=self.show_devices_frame_right, fill="x", anchor="n")
                self.label_devices.append(show_devices_line)

    def load_floor_data_from_bfm(self, bfm_active_devices):
        for floor in bfm_active_devices.keys():
            for platform in bfm_active_devices[floor].keys():
                self.floor_data[floor][int(platform) - 1] = 2 if bfm_active_devices[floor][platform]['busy'] else 1

    def refresh_table_from_bfm_data(self, bfm_active_devices):
        self.load_floor_data_from_bfm(bfm_active_devices)
        self.clear_devices_frame()
        self.full_devices_data()

    def forget(self):
        self.pack_forget()

    def show(self, options, floor_data=None, sequence_data=None, max_delay=None, min_delay=None):
        if floor_data is not None:
            self.floor_data = floor_data
            self.clear_devices_frame()
            self.full_devices_data()

        if sequence_data is not None:
            self.movements_available = sequence_data
            print(sequence_data)

        if max_delay is not None:
            self.max_delay = max_delay
        if min_delay is not None:
            self.min_delay = min_delay

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

    def start_sequence(self):
        if len(self.movements_available):
            print(self.min_delay)
            if self.sequence_started:
                self.sequence_generator.stop_sequence()
            print(self.movements_available)
            sequence = self.__chose_sequence__()
            print(f"Sequence: {sequence}")
            available = check_available_devices(self.floor_data)
            if len(available):

                print(self.movements_available[sequence])
                data_aux = {
                    field_available_robots: available,
                    field_delays: [self.min_delay, self.max_delay],
                    field_movement_type: self.movements_available[sequence],
                    field_max_full_rep: 1,

                }
                functions_aux = {
                    field_print_label_sequence: self.write_ongoing_sequence,
                    field_erase_label_sequence: self.erase_ongoing_label,
                    field_choose_sequence: self.__chose_sequence__
                }

                if not(self.novelty_population is None):
                    data_aux[field_novelty_population] = self.novelty_population

                self.sequence_generator.run_sequence(data_aux, functions_aux, self.threadSafe, selectedSequence=sequence)
        else:
            print("No available movements")

    def stop_sequence(self):
        self.sequence_generator.stop_sequence()
        self.erase_ongoing_label()

    def write_ongoing_sequence(self, sequence):
        self.sequence_started = True
        self.label_ongoing.config(text=f"On going sequence nº {sequence}")
        self.label_ongoing.pack(in_=self.label_ongoing_frame)

    def erase_ongoing_label(self):
        self.sequence_started = False
        self.label_ongoing.pack_forget()

    def get_floor_data(self):
        return self.floor_data

    def __chose_sequence__(self):

        if self.novelty_population is None:
            sequence = self.__chose_random_sequence__(self.movements_available)
        else:
            sequence, _, _ = self.novelty_population.transform_genome_into_usable_data(self.movements_available)

            print(sequence)

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

