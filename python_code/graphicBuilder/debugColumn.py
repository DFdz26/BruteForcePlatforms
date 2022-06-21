import tkinter as tk
from tkinter import ttk


class DebugColumn:
    def __init__(self, frame, available):
        self.text_frame = tk.Text(frame, height=5, width=52)
        self.available = available
        self.text_frame.pack()

    def write_data(self, data):
        self.text_frame.insert(tk.END, data + '\n')

        if not self.available:
            print(data)
