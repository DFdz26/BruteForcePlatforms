import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import tools_BF

field_save_max_delay = "max_delay"
field_save_floor_data = "floor_data"
field_save_min_delay = "min_delay"

PARAMETERS_FILENAME = tools_BF.FILENAME_STORED_PARAMETERS + tools_BF.EXTENSION_STORED_PARAMETERS
PARAMETERS_FOLDER = tools_BF.FOLDER_STORED_DATA


def load_parameters_file():
    tools_BF.check_create_folder(PARAMETERS_FOLDER)

    if tools_BF.check_file_exists(PARAMETERS_FILENAME, PARAMETERS_FOLDER):
        aux = tools_BF.file_reader(PARAMETERS_FILENAME, PARAMETERS_FOLDER, False)
        floor_data = aux[field_save_floor_data]
        min_delay = aux[field_save_min_delay]
        max_delay = aux[field_save_max_delay]
    else:
        max_delay = 10
        min_delay = 0.1
        floor_data = [2, 2, 3, 2, 0]

    return floor_data, max_delay, min_delay


def get_transformed_data(entries):
    floor_data = {
        "1": [],
        "2": [],
        "3": [],
        "4": [],
        "5": [0, 0, 0]
    }
    for i_l in range(5):
        if len(floor_data[str(i_l + 1)]) != int(entries[i_l]):
            floor_data[str(i_l + 1)] = [0] * int(entries[i_l])

    return floor_data


class ParametersFrame(tk.Frame):
    def __init__(self, home_frame, con, bg_colour, fonts, sizes, master):
        super().__init__(con)
        self.configure(bg=bg_colour)
        self.floor_data, self.max_delay, self.min_delay = load_parameters_file()
        self.floor_data_aux = {}

        self.master = master

        self.bottom_frame = tk.Frame(self, bg=bg_colour)
        self.top_frame = tk.Frame(self, bg=bg_colour)

        self.top_frame.pack(side=tk.TOP, fill="both", expand=True)
        self.bottom_frame.pack(side=tk.BOTTOM, fill="x")

        self.entries = []
        for i in range(tools_BF.SEQUENCE_TYPES):
            top_parameters_below = tk.Frame(self, bg=bg_colour)

            self.label = tk.Label(self, text=f"Robots in floor nº{i + 1}: ", padx=15, pady=4,
                                  font=f"{fonts} {sizes}",
                                  bg=bg_colour)
            self.label.pack(in_=top_parameters_below, side=tk.LEFT)

            self.entries.append(ttk.Entry(self, width=3))
            self.entries[i].pack(in_=top_parameters_below, side=tk.LEFT)
            self.entries[i].insert(0, str(self.floor_data[i]))

            top_parameters_below.pack(in_=self.top_frame, side=tk.TOP, fill="x", expand=False, padx=90, pady=3)

        self.frame_max_delay = tk.Frame(self, bg=bg_colour)
        self.label_max_delay = tk.Label(self, text=f"Max delay : ", padx=15, pady=4,
                                        font=f"{fonts} {sizes}",
                                        bg=bg_colour)

        self.label_max_delay.pack(in_=self.frame_max_delay, side=tk.LEFT)

        self.entry_max_delay = ttk.Entry(self, width=5)
        self.entry_max_delay.pack(in_=self.frame_max_delay, side=tk.LEFT)
        self.entry_max_delay.insert(0, str(self.max_delay))

        self.frame_max_delay.pack(in_=self.top_frame, side=tk.TOP, fill="x", expand=False, padx=90, pady=3)

        self.frame_min_delay = tk.Frame(self, bg=bg_colour)
        self.label_min_delay = tk.Label(self, text=f"Min delay : ", padx=15, pady=4,
                                        font=f"{fonts} {sizes}",
                                        bg=bg_colour)

        self.label_min_delay.pack(in_=self.frame_min_delay, side=tk.LEFT)

        self.entry_min_delay = ttk.Entry(self, width=5)
        self.entry_min_delay.pack(in_=self.frame_min_delay, side=tk.LEFT)
        self.entry_min_delay.insert(0, str(self.min_delay))

        self.frame_min_delay.pack(in_=self.top_frame, side=tk.TOP, fill="x", expand=False, padx=90, pady=3)

        self.home_b = tools_BF.HomeButton(home_frame, self, self.bottom_frame, "black", None, self.show_home)
        self.home_frame = home_frame

        self.save_b = tools_BF.SaveButton(self, self.save_data, self.bottom_frame)

    def get_entries_value(self):
        self.floor_data = [self.entries[i].get() for i in range(len(self.entries))]
        self.min_delay = float(self.entry_min_delay.get())
        self.max_delay = float(self.entry_max_delay.get())

        return self.floor_data, self.min_delay, self.max_delay

    def selected_floor(self):
        pass

    def save_data(self):
        self.get_entries_value()

        data = {
            field_save_max_delay: self.max_delay,
            field_save_min_delay: self.min_delay,
            field_save_floor_data: self.floor_data,
        }
        tools_BF.save_file(data, PARAMETERS_FILENAME, PARAMETERS_FOLDER, False)
        tk.messagebox.showinfo(title='Result', message="The data has been saved.")

    def get_transformed_data(self, floor_data):

        for i_l in range(5):
            if len(floor_data[str(i_l + 1)]) != int(self.entries[i_l].get()):
                floor_data[str(i_l + 1)] = [0] * int(self.entries[i_l].get())

        return floor_data

    def refresh_data(self, floor_data):

        for i in range(5):
            self.floor_data = len(floor_data[str(i + 1)])
            self.entries[i].delete(0, 'end')
            self.entries[i].insert(0, str(self.floor_data))

    def forget(self):
        self.pack_forget()

    def show(self, options, floor_data_aux):
        self.floor_data_aux = floor_data_aux
        self.home_frame.forget()
        self.pack(fill="both", expand=True)

    def show_home(self):
        floor_data = self.get_transformed_data(self.floor_data_aux)
        self.forget()
        self.home_frame.show(None, floor_data=floor_data)
