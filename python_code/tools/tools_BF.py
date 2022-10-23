# In this file there are some common declaration as well as some tools
import pandas as pd
import os
import pickle
import json
import tkinter as ttk

FOLDER_STORED_DATA = "stored_data"
USE_THREAD = False

FILENAME_STORED_AVAILABLE_MOVEMENTS = "mov_info"
EXTENSION_AVAILABLE_MOVEMENTS = ".json"

FILENAME_STORED_PARAMETERS = "param_info"
EXTENSION_STORED_PARAMETERS = ".json"

FOLDER_IMAGES = "img"
FILENAME_ARROW = "icons8-back-to-30.png"
FILENAME_SAVE = "icons8-save-30.png"
# EXCEL_FILENAME = "2022-07-08-btf-iterations.xlsx"
EXCEL_FILENAME = "nbf archive data 2020-07-16 - 2020-09-12(1).xlsx"

cwd = os.getcwd()
root_project = os.path.abspath(os.path.join(cwd, os.pardir))

# Communication defines
baud_arduino = 9600

MOVEMENT_TYPES = 6
IMPLEMENTED_TYPES = [1, 2, 3, 4, 5, 6, "long def.", "short def."]

CONVERT_STR_TO_MOV = {
    "long def.": 254,
    "short def.": 255
}

SEQUENCE_TYPES = 5


def generate_delays(max_delay, min_delay):
    pass


def get_full_path(fileName, folder=None):
    if folder is None:
        full_fileName = os.path.join(cwd, fileName)
    else:
        full_fileName = os.path.join(cwd, folder, fileName)

    return full_fileName


def save_file(data, fileName, folder, isPickle):
    full_fileName = get_full_path(fileName, folder)

    if isPickle:
        with open(full_fileName, 'wb') as opened_file:
            pickle.dump(data, opened_file, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        with open(full_fileName, 'w') as opened_file:
            json.dump(data, opened_file, indent=4)


def check_file_exists(fileName, folder):
    full_fileName = get_full_path(fileName, folder)

    return os.path.exists(full_fileName)


def check_create_folder(folderName, verbose=False):
    full_folder = os.path.join(cwd, folderName)

    if not os.path.isdir(full_folder):
        os.mkdir(full_folder)

        if verbose:
            print(f"The folder {full_folder} has been created.")


def file_reader(fileName, folder, isPickle):
    p_file = get_full_path(fileName, folder)

    if isPickle:
        with open(p_file, 'rb') as opened_file:
            b = pickle.load(opened_file)
    else:
        with open(p_file, 'r') as opened_file:
            b = json.load(opened_file)

    return b


class ExcelLoader:
    def __init__(self):
        self.excel_folder_name = 'excels'

        # self.files = [
        #     "Data Archive - additional parameters(1).xlsx",
        #     "nbf archive data 2020-07-16 - 2020-09-12(1).xlsx",
        #     "file.xlsx"
        # ]

        self.files = [
            EXCEL_FILENAME
        ]
        self.selected = -1

    def loadExcel(self, select, fields=None, verbose=True):
        res = {}
        self.selected = select

        if 0 > select or len(self.files) <= select:
            str_aux = 'The selected option must be 0' if len(self.files) == 1 else \
                f"The selected option must be between 0 and {len(self.files) - 1}"
            raise ValueError(str_aux)

        full_path = os.path.join(self.excel_folder_name, self.files[select])

        if verbose:
            print(f"The file {full_path} has been selected.")

        df = pd.read_excel(full_path)
        aux_dic = df.to_dict()

        if fields is None:
            res = aux_dic
        else:
            for fi in fields:
                res[fi] = aux_dic[fi]

        return res

    def saveCheckout(self):
        pass


class SaveButton:
    def __init__(self, parent, command, in_):
        path = get_full_path(FILENAME_SAVE, FOLDER_IMAGES)
        self.photo = ttk.PhotoImage(file=path)

        self.b = ttk.Button(parent, text="Store", image=self.photo, command=command)
        self.b.pack(in_=in_, side=ttk.RIGHT, pady=30, padx=30)


class HomeButton:
    def __init__(self, home_frame, parent_frame, subparent_frame, colour, options, command=None):
        self.h = home_frame
        self.p = parent_frame

        path = get_full_path(FILENAME_ARROW, FOLDER_IMAGES)
        self.photo = ttk.PhotoImage(file=path)

        self.b = ttk.Button(parent_frame, text="Home", image=self.photo,
                            command=self.show_home if command is None else command)
        self.b.pack(in_=subparent_frame, side=ttk.LEFT, pady=30, padx=30)

    def show_home(self):
        self.p.forget()
        self.h.show(None)


if __name__ == '__main__':
    # fileName_test = FILENAME_STORED_AVAILABLE_MOVEMENTS + EXTENSION_AVAILABLE_MOVEMENTS
    # data_test = {"Hello": "world"}
    #
    # check_create_folder(FOLDER_STORED_DATA)
    # print(check_file_exists(fileName_test, FOLDER_STORED_DATA))
    # save_file(data_test, fileName_test, FOLDER_STORED_DATA, isPickle=True)
    # print(check_file_exists(fileName_test, FOLDER_STORED_DATA))
    # print(file_reader(fileName_test, FOLDER_STORED_DATA, True))
    selected_fields = ["avg BPM animal", "avg BPM human", "delta BPM", "class"]
    selected_excel = 0

    excelLoader = ExcelLoader()
    excelData = excelLoader.loadExcel(selected_excel, selected_fields)

    print(excelData.keys())
