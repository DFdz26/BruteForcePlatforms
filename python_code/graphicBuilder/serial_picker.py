import tkinter as tk
from tkinter import ttk
from serialReceiver import lists_available_ports


class SerialListFrame(tk.Frame):
    def __init__(self, root, home_frame, con, bg_colour, fonts, sizes, master):
        super().__init__(con)
        self.configure(bg=bg_colour)
        self.home_frame = home_frame
        self.master = master
        self.picked_usb = ""

        self.available_serials = lists_available_ports()
        self.bottom_frame = tk.Frame(self, bg=bg_colour)
        self.top_frame = tk.Frame(self, bg=bg_colour)

        self.top_frame.pack(side=tk.TOP, fill="both", expand=True)
        self.bottom_frame.pack(side=tk.BOTTOM, fill="x")

        self.labels_frame = tk.Frame(self, bg=bg_colour)
        self.labels_frame.pack(in_=self.top_frame, side=tk.TOP)

        self.devices_frame = tk.Frame(self, bg=bg_colour)

        self.info_device = tk.Frame(self, bg=bg_colour)

        self.label_no_valid_ports = tk.Label(self, text=f"No valid port detected!. \nPossibly, device not "
                                                        f"plugged/detected. \nConnect a device and refresh the list.",
                                             padx=3, pady=4,
                                             font=f"{fonts} {int(sizes) + 2}",
                                             bg=bg_colour)
        self.label_select_info = tk.Label(self, text=f"Select the device for seeing its information.", padx=3, pady=4,
                                          font=f"{fonts} {int(sizes)}",
                                          bg=bg_colour)

        self.label_port_name = tk.Label(self, text=f"Port name: ", padx=3, pady=4,
                                        font=f"{fonts} {int(sizes)}",
                                        bg=bg_colour)

        self.combobox_usb = ttk.Combobox(root, width=10, value=list(self.available_serials), state="readonly")
        self.combobox_usb.set('')
        self.combobox_usb.bind("<<ComboboxSelected>>", self.show_info_usb)

        if not (len(self.available_serials)):
            self.label_no_valid_ports.pack(in_=self.labels_frame, side=tk.TOP)
        else:
            self.label_select_info.pack(in_=self.labels_frame, side=tk.TOP)
            self.devices_frame.pack(in_=self.top_frame, side=tk.TOP)
            self.info_device.pack(in_=self.top_frame, side=tk.TOP)

        self.label_port_name.pack(in_=self.devices_frame, side=tk.LEFT)
        self.combobox_usb.pack(in_=self.devices_frame, side=tk.LEFT)

        self.label_info_usb = tk.Label(self, text=f"", padx=3, pady=4,
                                       font=f"{fonts} {int(sizes) - 2}",
                                       bg=bg_colour)

        self.button_use = ttk.Button(self, text="Use", command=self.show_home)
        self.button_use.pack(in_=self.bottom_frame, side=tk.LEFT, pady=30, padx=30)

        self.button_refresh = ttk.Button(self, text="Refresh", command=self.update_combobox_usb)
        self.button_refresh.pack(in_=self.bottom_frame, side=tk.RIGHT, pady=30, padx=30)

    def show_info_usb(self, _):
        if len(self.available_serials):
            self.picked_usb = self.combobox_usb.get()
            self.label_info_usb["text"] = self.available_serials[self.picked_usb]
            self.label_info_usb.pack(in_=self.info_device, side=tk.TOP)

    def forget(self):
        self.pack_forget()

    def update_combobox_usb(self):
        self.available_serials = lists_available_ports()
        self.combobox_usb["value"] = list(self.available_serials)

        if not (len(self.available_serials)):
            self.label_select_info.pack_forget()
            self.label_no_valid_ports.pack(in_=self.labels_frame, side=tk.TOP)
            self.devices_frame.forget()
            self.info_device.forget()
            self.picked_usb = ""

        else:
            self.label_no_valid_ports.pack_forget()
            self.label_select_info.pack(in_=self.labels_frame, side=tk.TOP)
            self.devices_frame.pack(in_=self.top_frame, side=tk.TOP)
            self.info_device.pack(in_=self.top_frame, side=tk.TOP)

    def show(self):
        self.pack(fill="both", expand=True)

    def show_home(self):
        if len(self.picked_usb):
            self.master["object"].set_serial_configuration(self.picked_usb)
            self.forget()
            self.home_frame.show(None)
