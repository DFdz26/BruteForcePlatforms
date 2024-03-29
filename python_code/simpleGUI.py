import tkinter as ttk

import tools.tools_BF as tools_BF
import graphicBuilder.movements_frame as mov_frame
import graphicBuilder.home_frame as hom_frame
import graphicBuilder.parameters_frame as par_frame
from threading import Lock
from graphicBuilder.parameters_frame import load_parameters_file
import bruteForceMaster as bfm
import noveltySearch
import graphicBuilder.serial_picker as serial_picker_frame
import graphicBuilder.debugColumn as debug_frame

DEBUGGING = True
if DEBUGGING:
    import debugging_functions as bruteForceMaster
else:
    import bruteForceMaster

FILENAME_MOLECULE_GIF = "molecule3.gif"
fs_gif = 100
USE_GIF = True
communication_port = 'COM6'

width_window = 550
height_window = 520

bg_colour = "#f8f8f8"
bg_colour_home_frame = bg_colour
bg_colour_register_frame = bg_colour
bg_colour_movement_frame = bg_colour
bg_colour_parameters_frame = bg_colour

font_title = "Calibri"
font_size_title = 20

label_devices = []
show_home_button = None

# In order to change the retry time (the elapsed time before the master will try to send a new message) change
# this dictionary. "first" key will change the retry time in the first sequence, "second" in the second and so on.
# They are expressed in seconds. It is recommended to have a minimum of time so the platform (slave) is capable of
# replaying an ACK message and the master is capable to catch this ACK message.
retry_times = {
    'first': 0.3,
    'second': 0.3,
    'third': 0.3,
    'fourth': 0.3,
    'fifth': 0.3,
    'stop': 0.2,
}


def update(ind, label_img, frame_img, frames_img, maxFrames, fs):
    if loop_active:
        frame = frames_img[ind]
        ind += 1

        if ind == maxFrames:
            ind = 0

        label_img.configure(image=frame)
        frame_img.after(fs, update, ind, label_img, frame_img, frames_img, maxFrames, fs)


def onclose(win, finishPrincipalLoop=False):
    global loop_active

    if finishPrincipalLoop:
        loop_active = False

    try:
        win.destroy()
    except AttributeError as e:
        print(f"Closing: {e}")


# ROOT FRAME
root = ttk.Tk()
root.configure(bg=bg_colour)

bottom_root = ttk.Frame(root)
bottom_root_right = ttk.Frame(root)
bottom_root_left = ttk.Frame(root)
bottom_root_real = ttk.Frame(root)
top_root = ttk.Frame(root)

bottom_root.configure(bg=bg_colour)
top_root.configure(bg=bg_colour)
bottom_root_real.configure(bg=bg_colour)

top_root.pack(side=ttk.TOP)
bottom_root.pack(fill="both", expand=True)
bottom_root_left.pack(in_=bottom_root, side=ttk.LEFT, fill="both", expand=True)
debug_visible = False
debug_fr = debug_frame.DebugColumn(bottom_root_right, True)

label = ttk.Label(root, text="!BruteForce", padx=15, font=f"{font_title} {font_size_title}", bg=bg_colour)
label.pack(in_=top_root, side=ttk.LEFT)


def show_debug_window():
    global debug_visible

    if debug_visible:
        debug_visible = False
        bottom_root_right.forget()
        root.geometry(f"{width_window}x{height_window}")
    else:
        debug_visible = True
        root.geometry(f"{width_window + 100}x{height_window}")
        bottom_root_right.pack(in_=bottom_root, side=ttk.RIGHT, fill="both", expand=True)


if USE_GIF:
    molecule_label = ttk.Label(top_root, bg=bg_colour)
    molecule_label.pack(in_=top_root, side=ttk.RIGHT)

root.title("!BruteForce")
root.geometry(f"{width_window}x{height_window}")
root.protocol('WM_DELETE_WINDOW', lambda: onclose(root, True))
f_d, _ = load_parameters_file()
noveltyPop = noveltySearch.NoveltySearchBF()

bFM = bfm.BruteForceMaster(f_d)

master = {
    "object": bruteForceMaster.BruteForceMaster(None, tools_BF.baud_arduino, communication_port, assign_new_address=True),
    "Lock": Lock()
}

bFM_master = {
    "object": bFM,
    "Lock": Lock()
}

# I need this in order to modify the home frame without being in the main loop. It seems that tkinter is not
# thread-safe. There are some alternatives as mTkinter but due to I have the structure already built using Tkinter, I'm
# not gonna implement it.
modify_home_frame = {
    "value": 0,
    "last_value": 0,
    "printed": False,
    "Lock": Lock()
}

home_frame = hom_frame.HomeFrame(
    root,
    show_debug_window,
    bottom_root_left,
    bg_colour_home_frame,
    font_title,
    "12",
    bFM_master,
    modify_home_frame,
    noveltyPop,
    retry_timeouts=retry_times
)

mov_fr = mov_frame.MovementsFrame(
    root,
    home_frame,
    bottom_root_left,
    bg_colour_movement_frame,
    font_title,
    "12",
    bFM_master
)

serial_fr = serial_picker_frame.SerialListFrame(
    root,
    home_frame,
    bottom_root_left,
    bg_colour_movement_frame,
    font_title,
    "12",
    bFM_master
)

parameters_frame = par_frame.ParametersFrame(
    root,
    home_frame,
    bottom_root_left,
    bg_colour_parameters_frame,
    font_title,
    "12",
    bFM_master
)

register_frame = ttk.Frame(bottom_root_left)

home_frame.load_frames(None, mov_fr, parameters_frame)

# Register frame
register_frame.configure(bg=bg_colour_register_frame)

bottom_register = ttk.Frame(register_frame)
top_register = ttk.Frame(register_frame)

bottom_register.configure(bg=bg_colour_register_frame)
top_register.configure(bg=bg_colour_register_frame)

top_register.pack(side=ttk.TOP, fill="both", expand=True)
bottom_register.pack(side=ttk.BOTTOM, fill="x")

loop_active = True
serial_fr.show()

if USE_GIF:
    frameCnt_molecule = 60
    frames_molecule = [ttk.PhotoImage(file=tools_BF.get_full_path(FILENAME_MOLECULE_GIF, tools_BF.FOLDER_IMAGES),
                                      format='gif -index %i' % i) for i in range(frameCnt_molecule)]

    home_frame.after(0, update, 0, molecule_label, home_frame, frames_molecule, frameCnt_molecule, fs_gif)

try:

    while loop_active:
        bFM_master["Lock"].acquire()

        if bFM_master["object"].serialIsSet():
            bFM_master["object"].run()

        modify_home_frame["Lock"].acquire()
        if modify_home_frame["value"] != modify_home_frame["last_value"]:
            modify_home_frame["last_value"] = modify_home_frame["value"]

            if modify_home_frame["value"]:
                home_frame.write_ongoing_sequence(modify_home_frame["value"])
            else:
                home_frame.erase_ongoing_label()
        modify_home_frame["Lock"].release()

        if bFM.check_change_flag():
            bFM.unset_change_flag()
            devices = bFM.get_active_devices()
            home_frame.refresh_table_from_bfm_data(devices)

        bFM_master["Lock"].release()
        root.update()

except KeyboardInterrupt:
    home_frame.stop_sequence()
    bFM.terminate()
finally:
    home_frame.stop_sequence()
    bFM.terminate()
