import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import tools.tools_BF as tools_BF

field_save_max_delay = "max_delay"
field_save_floor_data = "floor_data"
field_save_min_delay = "min_delay"
field_save_delays_dic = "delays"

PARAMETERS_FILENAME = tools_BF.FILENAME_STORED_PARAMETERS + tools_BF.EXTENSION_STORED_PARAMETERS
PARAMETERS_FOLDER = tools_BF.FOLDER_STORED_DATA


def load_parameters_file():
    tools_BF.check_create_folder(PARAMETERS_FOLDER)

    predefined_delays_dic = {
        "1": {
            "max_delay": 6.0,
            "min_delay": 6.0
        },
        "2": {
            "max_delay": 6.0,
            "min_delay": 6.0
        },
        "3": {
            "max_delay": 6.0,
            "min_delay": 6.0
        },
        "4": {
            "max_delay": 6.0,
            "min_delay": 6.0
        },
        "5": {
            "max_delay": 6.0,
            "min_delay": 6.0
        }
    }

    if tools_BF.check_file_exists(PARAMETERS_FILENAME, PARAMETERS_FOLDER):
        aux = tools_BF.file_reader(PARAMETERS_FILENAME, PARAMETERS_FOLDER, False)
        floor_data = aux[field_save_floor_data]
        delays_dic = aux[field_save_delays_dic]

        if len(delays_dic) != tools_BF.SEQUENCE_TYPES:
            delays_dic = predefined_delays_dic

    else:
        floor_data = [2, 2, 3, 2, 0]
        delays_dic = predefined_delays_dic

    return floor_data, delays_dic


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
    def __init__(self, root, home_frame, con, bg_colour, fonts, sizes, master):
        super().__init__(con)
        self.configure(bg=bg_colour)
        self.floor_data, self.delay_dic = load_parameters_file()
        self.floor_data_aux = {}
        self.selected_sequence = 1

        self.master = master
        general_x_pad = 15
        frame_x_pad = 180

        self.bottom_frame = tk.Frame(self, bg=bg_colour)
        self.top_frame = tk.Frame(self, bg=bg_colour)
        self.frame_delays = tk.Frame(self, bg=bg_colour)

        self.top_frame.pack(side=tk.TOP, fill="both", expand=True)
        self.bottom_frame.pack(side=tk.BOTTOM, fill="x")

        self.entries = []
        for i in range(tools_BF.SEQUENCE_TYPES):
            top_parameters_below = tk.Frame(self, bg=bg_colour)

            self.label = tk.Label(self, text=f"Robots in floor nº{i + 1}: ", padx=general_x_pad, pady=4,
                                  font=f"{fonts} {sizes}",
                                  bg=bg_colour)
            self.label.pack(in_=top_parameters_below, side=tk.LEFT)

            self.entries.append(ttk.Entry(self, width=3))
            self.entries[i].pack(in_=top_parameters_below, side=tk.LEFT)
            self.entries[i].insert(0, str(self.floor_data[i]))

            top_parameters_below.pack(in_=self.top_frame, side=tk.TOP, fill="x", expand=False, padx=frame_x_pad, pady=3)

        separator = ttk.Separator(root, orient='horizontal')
        separator.pack(in_=self.top_frame, fill='x')

        self.label_delay_title = tk.Label(self, text=f"Change the delay for the different sequences.",
                                          padx=3, pady=5,
                                          font=f"{fonts} {int(sizes)}",
                                          bg=bg_colour)
        self.label_delay_title.pack(in_=self.frame_delays, side=tk.TOP)

        self.frame_delays.pack(in_=self.top_frame, side=tk.TOP, fill="x", expand=False, pady=3)
        self.frame_selected_sequence = tk.Frame(self, bg=bg_colour)
        self.label_sequence_selected = tk.Label(self, text=f"Sequence nº ", padx=3, pady=4,
                                                font=f"{fonts} {int(sizes)}",
                                                bg=bg_colour)

        self.label_sequence_selected.pack(in_=self.frame_selected_sequence, side=tk.LEFT)

        self.combobox_sequence_selected = ttk.Combobox(root, width=3, state="readonly",
                                                       value=[(i + 1) for i in range(tools_BF.SEQUENCE_TYPES)])
        self.combobox_sequence_selected.bind("<<ComboboxSelected>>", self.update_selected_sequence)
        self.combobox_sequence_selected.set(1)
        self.combobox_sequence_selected.pack(in_=self.frame_selected_sequence, side=tk.LEFT)

        self.frame_selected_sequence.pack(in_=self.frame_delays, side=tk.TOP, fill="x", expand=False, padx=frame_x_pad,
                                          pady=3)

        self.frame_max_delay = tk.Frame(self, bg=bg_colour)
        self.label_max_delay = tk.Label(self, text=f"Max delay : ", padx=general_x_pad, pady=4,
                                        font=f"{fonts} {sizes}",
                                        bg=bg_colour)

        self.label_max_delay.pack(in_=self.frame_max_delay, side=tk.LEFT)

        self.entry_max_delay = ttk.Entry(self, width=5)
        self.entry_max_delay.pack(in_=self.frame_max_delay, side=tk.LEFT)
        self.entry_max_delay.insert(0, str(self.delay_dic[str(self.selected_sequence)]["max_delay"]))

        self.frame_max_delay.pack(in_=self.frame_delays, side=tk.TOP, fill="x", expand=False, padx=frame_x_pad, pady=3)

        self.frame_min_delay = tk.Frame(self, bg=bg_colour)
        self.label_min_delay = tk.Label(self, text=f"Min delay : ", padx=general_x_pad, pady=4,
                                        font=f"{fonts} {sizes}",
                                        bg=bg_colour)

        self.label_min_delay.pack(in_=self.frame_min_delay, side=tk.LEFT)

        self.entry_min_delay = ttk.Entry(self, width=5)
        self.entry_min_delay.pack(in_=self.frame_min_delay, side=tk.LEFT)
        self.entry_min_delay.insert(0, str(self.delay_dic[str(self.selected_sequence)]["min_delay"]))

        self.frame_min_delay.pack(in_=self.frame_delays, side=tk.TOP, fill="x", expand=False, padx=frame_x_pad, pady=3)

        self.home_b = tools_BF.HomeButton(home_frame, self, self.bottom_frame, "black", None, self.show_home)
        self.home_frame = home_frame

        self.save_b = tools_BF.SaveButton(self, self.save_data, self.bottom_frame)

    def get_entries_delay(self):
        self.delay_dic[str(self.selected_sequence)]["min_delay"] = float(self.entry_min_delay.get())
        self.delay_dic[str(self.selected_sequence)]["max_delay"] = float(self.entry_max_delay.get())
        # self.max_delay = float(self.entry_max_delay.get())

    def get_entries_value(self):
        self.floor_data = [self.entries[i].get() for i in range(len(self.entries))]

        return self.floor_data

    def update_selected_sequence(self, event):

        self.get_entries_delay()

        self.selected_sequence = int(self.combobox_sequence_selected.get())
        self.entry_min_delay.delete(0, 'end')
        self.entry_max_delay.delete(0, 'end')

        self.entry_max_delay.insert(0, str(self.delay_dic[str(self.selected_sequence)]["max_delay"]))
        self.entry_min_delay.insert(0, str(self.delay_dic[str(self.selected_sequence)]["min_delay"]))

    def selected_floor(self):
        pass

    def save_data(self):
        self.get_entries_value()

        data = {
            field_save_floor_data: self.floor_data,
            field_save_delays_dic: self.delay_dic
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
        self.get_entries_delay()

        self.forget()
        self.home_frame.show(None, floor_data=floor_data, dic_delays=self.delay_dic)
