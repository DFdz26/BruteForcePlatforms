import time
import tools.tools_BF as tools_BF
import bruteForceMaster

if __name__ == '__main__':
    floor_data = [
        "2",
        "2",
        "3",
        "4",
        "0"
    ]

    master = bruteForceMaster.BruteForceMaster(tools_BF.baud_arduino, 'COM7', floor_data)
    test_floor_1 = 1
    test_platform_1 = 1
    test_mov_1 = 3

    test_floor_2 = 1
    test_platform_2 = 2
    test_mov_2 = 2
    one = True
    one2 = True
    once = test_floor_2

    try:
        while 1:
            master.run()

            if master.check_change_flag():
                master.unset_change_flag()
                aux = master.get_last_connection(test_platform_1, test_floor_1)
                aux2 = master.get_last_connection(test_platform_2, test_floor_1)
                devices = master.get_active_devices()

                if len(devices):
                    once = False
                    print("active_devices:")
                    print(devices)

                if (len(aux) != 0) and one:
                    print(aux)
                    if (time.time() - aux[0]["last_time"]) < 30:
                        master.send_move_packet_process(test_mov_1, test_platform_1, test_floor_1)
                        one = False

                if (len(aux2) != 0) and one2:
                    if (time.time() - aux[0]["last_time"]) < 30:
                        master.send_move_packet_process(test_mov_2, test_platform_2, test_floor_2)
                        one2 = False

            time.sleep(.1)
    except KeyboardInterrupt:
        master.terminate()
    finally:
        pass
