import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import tools_BF


field_save_movements_data = "mov_data"
field_save_seq_data = "seq_data"
MOVEMENT_FILENAME = tools_BF.FILENAME_STORED_AVAILABLE_MOVEMENTS + tools_BF.EXTENSION_AVAILABLE_MOVEMENTS
MOVEMENT_FOLDER = tools_BF.FOLDER_STORED_DATA


def check_available_devices(data):
    ret = {}

    for key in data.keys():
        for i in range(len(data[key])):
            if data[key][i] == 1:
                if not int(key) in ret:
                    ret[int(key)] = []

                ret[int(key)].append(i + 1)

    return ret


def load_movements_file():
    tools_BF.check_create_folder(MOVEMENT_FOLDER)

    if tools_BF.check_file_exists(MOVEMENT_FILENAME, MOVEMENT_FOLDER):
        aux = tools_BF.file_reader(MOVEMENT_FILENAME, MOVEMENT_FOLDER, False)
        mov_ret = aux[field_save_movements_data]
        seq_ret = aux[field_save_seq_data]
    else:
        seq_ret = [1] * tools_BF.SEQUENCE_TYPES
        mov_ret = [[1] * tools_BF.MOVEMENT_TYPES] * tools_BF.SEQUENCE_TYPES

    return mov_ret, seq_ret


def transform_data_to_dict(mov_act, seq_act):
    data = {}
    for i in range(tools_BF.SEQUENCE_TYPES):
        if seq_act[i]:
            aux = []
            for j in range(tools_BF.MOVEMENT_TYPES):
                if mov_act[i][j]:
                    aux.append(j + 1)

            if len(aux):
                data[i + 1] = aux.copy()

    return data


class MovementsFrame(tk.Frame):
    def __init__(self, root, home_frame, con, bg_colour, fonts, sizes, master):
        super().__init__(con)
        self.configure(bg=bg_colour)

        self.master = master
        self.available = None
        self.bottom_frame = tk.Frame(self, bg=bg_colour)
        self.top_frame = tk.Frame(self, bg=bg_colour)

        self.top_frame.pack(side=tk.TOP, fill="both", expand=True)
        self.bottom_frame.pack(side=tk.BOTTOM, fill="x")

        self.table_frame = tk.Frame(self, bg=bg_colour)
        self.table_frame.pack(in_=self.top_frame, side=tk.TOP, fill="both", expand=True)

        self.test_movement_frame = tk.Frame(self, bg=bg_colour)
        self.test_movement_frame.pack(in_=self.top_frame, side=tk.TOP, fill="both", expand=True)

        self.label_send_move = tk.Label(self, text=f"Send move ", padx=3, pady=4,
                                        font=f"{fonts} {int(sizes) - 2}",
                                        bg=bg_colour)

        self.label_send_move.pack(in_=self.test_movement_frame, side=tk.LEFT)

        self.combobox_mov_types = ttk.Combobox(self, width=3, state="readonly",
                                               value=tools_BF.IMPLEMENTED_TYPES)
        self.combobox_mov_types.set('1')
        self.combobox_mov_types.pack(in_=self.test_movement_frame, side=tk.LEFT)

        self.label_to_rob = tk.Label(self, text=f" to the robot in the floor ", padx=3, pady=4,
                                     font=f"{fonts} {int(sizes) - 2}",
                                     bg=bg_colour)

        self.label_to_rob.pack(in_=self.test_movement_frame, side=tk.LEFT)
        self.combobox_floors = ttk.Combobox(root, width=3, state="readonly",
                                            value=[])
        self.combobox_floors.set('')
        self.combobox_floors.pack(in_=self.test_movement_frame, side=tk.LEFT)
        self.combobox_floors.bind("<<ComboboxSelected>>", self.update_combobox_robots)

        self.label_to_rob_in = tk.Label(self, text=f" nº ", padx=3, pady=4,
                                        font=f"{fonts} {int(sizes) - 2}",
                                        bg=bg_colour)

        self.label_to_rob_in.pack(in_=self.test_movement_frame, side=tk.LEFT)

        self.combobox_platforms = ttk.Combobox(root, width=3, state="readonly",
                                               value=[])
        self.combobox_platforms.set('')
        self.combobox_platforms.pack(in_=self.test_movement_frame, side=tk.LEFT)
        self.send_button_test = tk.Button(self, text="Send", command=self.send_test)
        self.send_button_test.pack(in_=self.top_frame, side=tk.TOP)

        self.table = []
        self.movements_data_intVar = {}
        self.actives_sequences_aux = {}
        self.movements_data, self.actives_sequences = load_movements_file()
        self.boxes = []
        for i_p in range(tools_BF.SEQUENCE_TYPES):
            self.movements_data_intVar[str(i_p + 1)] = []
            self.actives_sequences_aux[str(i_p + 1)] = tk.IntVar(root, value=self.actives_sequences[i_p])

            for j_p in range(tools_BF.MOVEMENT_TYPES):
                self.movements_data_intVar[str(i_p + 1)].append(tk.IntVar(root, value=self.movements_data[i_p][j_p]))

        for i in range(tools_BF.SEQUENCE_TYPES + 1):
            entrance = tk.Frame(self, bg=bg_colour)
            entrance.pack(in_=self.table_frame, side=tk.TOP, fill="x")

            left_entrance = tk.Frame(self, bg=bg_colour)
            right_entrance = tk.Frame(self, bg=bg_colour)

            left_entrance.pack(in_=entrance, side=tk.LEFT, fill="y")
            right_entrance.pack(in_=entrance, side=tk.RIGHT, fill="y", expand=True)

            if i == 0:
                label = tk.Label(self, text=f"Sequence 0", padx=15, pady=4, font=f"{fonts} {sizes}",
                                 bg=bg_colour, fg=bg_colour)
                label.pack(in_=left_entrance)

                label = tk.Label(self, text=f"Act.", padx=7, pady=4, font=f"{fonts} {sizes}",
                                 bg=bg_colour)
                label.pack(in_=right_entrance, side=tk.LEFT)

                for i_p in range(tools_BF.MOVEMENT_TYPES):
                    label = tk.Label(self, text=f"Mov {i_p + 1}", padx=7, pady=4, font=f"{fonts} {sizes}",
                                     bg=bg_colour)
                    label.pack(in_=right_entrance, side=tk.LEFT)
            else:
                label = tk.Label(self, text=f"Squence {i}", padx=15, pady=4, font=f"{fonts} {sizes}",
                                 bg=bg_colour)
                label.pack(in_=left_entrance)

                type_move_line = tk.Frame(self, bg=bg_colour)

                c = tk.Checkbutton(self, padx=15, pady=4, bg=bg_colour, variable=self.actives_sequences_aux[str(i)])

                if self.actives_sequences[i - 1]:
                    c.select()
                else:
                    c.deselect()

                c.pack(in_=type_move_line, anchor="n", side=tk.LEFT)
                b = []

                for j_p in range(tools_BF.MOVEMENT_TYPES):

                    d_aux = tk.Checkbutton(self, padx=15, pady=4, bg=bg_colour,
                                           variable=self.movements_data_intVar[str(i)][j_p])

                    if self.movements_data[i - 1][j_p]:
                        d_aux.select()
                    else:
                        d_aux.deselect()

                    d_aux.pack(in_=type_move_line, anchor="n", side=tk.LEFT)
                    b.append(d_aux)

                type_move_line.pack(in_=right_entrance, fill="x", anchor="n")
                self.boxes.append(b)

        self.home_b = tools_BF.HomeButton(home_frame, self, self.bottom_frame, "black", None, command=self.show_home)
        self.home_frame = home_frame

        self.save_b = tools_BF.SaveButton(self, self.save_data, self.bottom_frame)

    def send_test(self):
        mov = int(self.combobox_mov_types.get())
        platform = int(self.combobox_platforms.get())
        floor = int(self.combobox_floors.get())

        self.master["Lock"].acquire()
        self.master["object"].send_move_packet_process(mov, platform, floor, pending_flag=True)
        self.master["Lock"].release()

        tk.messagebox.showinfo(title='Sent', message="The movement has been sent.")

    def save_data(self):
        self.refresh_auxs()

        data = {
            field_save_movements_data: self.movements_data,
            field_save_seq_data: self.actives_sequences
        }
        tools_BF.save_file(data, MOVEMENT_FILENAME, MOVEMENT_FOLDER, False)
        tk.messagebox.showinfo(title='Saved', message="The data has been saved.")

    def get_data(self):
        self.refresh_auxs()

        data = {}
        for i in range(tools_BF.SEQUENCE_TYPES):
            if self.actives_sequences[i]:
                aux = []
                for j in range(tools_BF.MOVEMENT_TYPES):
                    if self.movements_data[i][j]:
                        aux.append(j + 1)

                if len(aux):
                    data[i + 1] = aux.copy()

        return data

    def get_movements_sequences_active(self):
        active = {}

        for i in range(tools_BF.SEQUENCE_TYPES):
            if self.actives_sequences_aux[str(i + 1)].get() == 1:
                active[i + 1] = []

                for j in range(tools_BF.MOVEMENT_TYPES):
                    if self.movements_data_intVar[str(i + 1)][j].get() == 1:
                        active[i + 1].append(j)

                if len(active[i + 1]) == 0:
                    _ = active.pop(i + 1)

        return active

    def refresh_auxs(self):
        for i_p in range(tools_BF.SEQUENCE_TYPES):
            self.actives_sequences[i_p] = self.actives_sequences_aux[str(i_p + 1)].get()

            for j_p in range(tools_BF.MOVEMENT_TYPES):
                self.movements_data[i_p][j_p] = self.movements_data_intVar[str(i_p + 1)][j_p].get()

    def forget(self):
        self.pack_forget()

    def update_combobox_robots(self, event):
        values = []
        set_value = ''
        selected_floor = int(self.combobox_floors.get())
        if selected_floor in self.available:
            values = self.available[selected_floor]
            set_value = str(values[0])

        self.combobox_platforms.set(set_value)
        self.combobox_platforms['values'] = values

    def update_combobox_floors(self):
        values = []
        set_value = ''
        if len(self.available):
            values = [k for k in self.available.keys()]
            set_value = str(values[0])

        self.combobox_floors.set(set_value)
        self.combobox_floors['values'] = values

    def show(self, options, floor_data):
        self.available = check_available_devices(floor_data)
        print(self.available)
        self.update_combobox_floors()

        self.home_frame.forget()
        self.pack(fill="both", expand=True)

    def show_home(self):
        sequence_data = self.get_data()
        self.combobox_platforms.set('')
        self.forget()
        self.home_frame.show(None, sequence_data=sequence_data)


