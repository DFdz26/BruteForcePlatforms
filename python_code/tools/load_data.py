import random

print_data_debug = True

MIN_INFLATION_TIME = 5000
MAX_INFLATION_TIME = 25000

DATE_POSITION = 0
ANIMAL_BPM_POSITION = 1
HUMAN_BPM_POSITION = 2
DELTA_BPM_POSITION = 3
CLASS_POSITION = 4
MOVING_4_POSITION = 5

data_arduino = [[803, 68.10, 87.07, 18.97, 2, 1.50],
                [803, 90.22, 88.06, 2.16, 0, 1.50],
                [803, 139.21, 86.06, 53.15, 4, 1.50],
                [804, 99.20, 81.66, 17.54, 2, 2.00],
                [804, 100.61, 89.79, 10.82, 2, 2.25],
                [804, 88.00, 83.79, 4.21, 0, 2.25],
                [804, 163.56, 87.03, 76.53, 4, 2.25],
                [804, 113.60, 88.80, 24.80, 3, 2.25],
                [806, 101.51, 91.33, 10.18, 2, 2.25],
                [806, 72.50, 90.41, 17.91, 2, 2.50],
                [806, 103.08, 86.02, 17.05, 2, 2.50],
                [806, 111.80, 80.41, 31.39, 3, 2.50],
                [806, 107.91, 81.58, 26.33, 3, 1.75],
                [807, 94.34, 95.85, 1.51, 0, 2.00],
                [807, 138.63, 94.60, 44.02, 4, 2.50],
                [818, 158.73, 84.22, 74.51, 4, 2.50],
                [819, 67.41, 94.14, 26.73, 3, 1.00],
                [819, 79.33, 86.36, 7.02, 1, 1.25],
                [819, 91.99, 94.35, 2.36, 0, 1.00],
                [819, 93.40, 89.98, 3.42, 0, 2.00],
                [820, 78.40, 91.11, 12.70, 2, 1.75],
                [820, 79.45, 89.85, 10.40, 2, 1.50],
                [820, 96.60, 95.50, 1.10, 0, 1.00],
                [821, 79.29, 103.54, 24.25, 3, 2.50],
                [821, 67.35, 109.48, 42.12, 4, 2.25],
                [821, 104.00, 104.40, 0.40, 0, 1.75],
                [821, 72.64, 105.65, 33.00, 3, 1.75],
                [831, 104.37, 94.50, 9.87, 1, 2.00],
                [831, 79.33, 95.21, 15.88, 2, 2.75],
                [831, 84.00, 97.73, 13.73, 2, 2.25],
                [903, 101.98, 84.80, 17.18, 2, 1.25],
                [903, 91.89, 87.34, 4.55, 0, 1.25],
                [903, 106.00, 92.36, 13.64, 2, 1.75],
                [908, 119.77, 89.04, 30.73, 3, 2.50],
                [908, 130.90, 86.45, 44.45, 4, 2.25],
                [908, 77.53, 91.10, 13.57, 2, 1.25],
                [908, 76.85, 86.27, 9.42, 1, 1.25],
                [909, 111.50, 90.53, 20.97, 3, 2.25],
                [909, 94.50, 87.26, 7.24, 1, 2.25],
                [909, 104.83, 89.85, 14.99, 2, 3.00],
                [909, 135.79, 99.63, 36.16, 3, 3.00],
                [910, 81.00, 87.61, 6.61, 1, 1.50],
                [910, 78.06, 85.20, 7.14, 1, 2.00],
                [910, 141.50, 90.91, 50.59, 4, 2.00],
                [910, 92.92, 93.88, 0.96, 0, 1.50],
                [911, 194.57, 100.88, 93.70, 4, 2.25],
                [911, 81.70, 108.39, 26.69, 3, 2.25],
                [912, 120.00, 85.33, 34.67, 3, 2.75],
                [912, 73.89, 85.08, 11.19, 2, 2.75],
                [912, 109.14, 96.79, 12.35, 2, 2.50]]


def transform_data_movement_6(segment1, segment2, segment3):
    # Bear in mind that inside the arduino code, the received data
    # will be used as:
    # inflationTime = ((segment1 + 1) * 44 + 1000) % 25000
    # chamber = (segment2 + 1) % 3
    # The third segment is not used
    # The mentioned lines should be in arduino_code.ino lines 843 and 844
    # The first returned value can be among 65535 to 0 (int).
    # The second and third returned value can be among 255 to 0 (int).
    returned_segment1 = segment1
    returned_segment2 = segment2
    returned_segment3 = segment3

    return int(returned_segment1), int(returned_segment2), int(returned_segment3)


def transform_data_movement_5(segment1, segment2, segment3):
    # Bear in mind that inside the arduino code, the received data
    # will be used as:
    # inflationTime = data + 1
    # These lines can be found inside the defined function "dataMove1" (line 937) in arduino_code.ino
    # The first returned value can be among 65535 to 0 (int).
    # The second and third returned value can be among 255 to 0 (int).
    returned_segment1 = segment1
    returned_segment2 = segment2
    returned_segment3 = segment3

    return int(returned_segment1), int(returned_segment2), int(returned_segment3)


def transform_data_movement_4(segment1, segment2, segment3):
    # Bear in mind that inside the arduino code, the received data
    # will be used as:
    # inflationTime = (data + 1) * 100
    # These lines can be found inside the defined function "dataMove2" (line 896) in arduino_code.ino
    # The first returned value can be among 65535 to 0 (int).
    # The second and third returned value can be among 255 to 0 (int).
    returned_segment1 = segment1
    returned_segment2 = segment2
    returned_segment3 = segment3

    return int(returned_segment1), int(returned_segment2), int(returned_segment3)


transformed_data_functions = {
    4: transform_data_movement_4,
    5: transform_data_movement_5,
    6: transform_data_movement_6,
}


def random_generate_data(required_items, data=None, serial_debug=None, raw_data=False, sequence=0):
    if data is None:
        data = data_arduino
    ret = []

    for _ in range(required_items):
        aux = random.choice(data)

        segment1 = aux[ANIMAL_BPM_POSITION]
        segment2 = aux[HUMAN_BPM_POSITION]
        segment3 = aux[DELTA_BPM_POSITION]

        # segment2 = 2
        # print(f"For debugging, I'm forcing the value segment2 to be {segment2}. ")
        # print(f"Please in case of not being in debug mode, erase lines 60ish of the file load_data.py")
        if not raw_data:
            inflation_time = int(segment1 * 44 + 1000)
            chamber = int(segment2 % 3)
            iterations = int(segment3 % 3) + 1

            inflation_time_filtered = inflation_time

            if MAX_INFLATION_TIME < inflation_time:
                inflation_time_filtered = MAX_INFLATION_TIME
            elif MIN_INFLATION_TIME > inflation_time:
                inflation_time_filtered = MIN_INFLATION_TIME

            if print_data_debug:
                if serial_debug is None:
                    print(f"Chosen: {segment1}, \tInflation time (ms): {inflation_time}",
                          "" if inflation_time_filtered == inflation_time else f"Filtered value: {inflation_time_filtered}")
                    print(f"Chosen: {segment2}, \tChamber: {chamber}")
                    print(f"Chosen: {segment3}, \tIterations: {iterations}")
                    print("------------")
                else:
                    serial_debug.write_data(f"Chosen: {segment1}, \tInflation time (ms): {inflation_time}",
                                            "" if inflation_time_filtered == inflation_time else f"Filtered value: {inflation_time_filtered}")
                    serial_debug.write_data(f"Chosen: {segment2}, \tChamber: {chamber}")
                    serial_debug.write_data(f"Chosen: {segment3}, \tIterations: {iterations}")
                    serial_debug.write_data("------------")

        else:
            if sequence in transformed_data_functions:
                inflation_time, chamber, iterations = transformed_data_functions[sequence](segment1, segment2, segment3)
            else:
                inflation_time = int(segment1)
                chamber = int(segment2)
                iterations = int(segment3)

            inflation_time_filtered = inflation_time

            if print_data_debug:
                if serial_debug is None:
                    print(f"Chosen: {inflation_time}")
                    print(f"Chosen: {chamber}")
                    print(f"Chosen: {iterations}")
                    print("------------")
                else:
                    serial_debug.write_data(f"Chosen: {inflation_time}")
                    serial_debug.write_data(f"Chosen: {chamber}")
                    serial_debug.write_data(f"Chosen: {iterations}")
                    serial_debug.write_data("------------")

        aux_ret = {
            "time": inflation_time_filtered,
            "chamber": chamber,
            "iterations": iterations
        }
        ret.append(aux_ret)

    return ret


if __name__ == '__main__':
    # charge_excels()
    print_data_debug = True
    random_generate_data(3)
