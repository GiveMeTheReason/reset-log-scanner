from collections import deque
from time import sleep

from python.parser.serial_read import Ring
from python.parser.invert_measurements import invert
from python.filter.interpolate_slice import interpolate_slice
from python.model.volume import calculate_volume
# from python.blender_vis.main import create_log


# Change your usb name here (ex. /dev/ttyUSB0) /dev/ttyACM1 COM6
LEFT_PORT_MASTER = 'COM4'
RIGHT_PORT_SLAVE = 'COM3'
BAUD_RATE = 115200

# all measuremets are in millimetres
RING_RADIUS = 243
SENSOR_NUMBER = 24
ALPHA = 360 / SENSOR_NUMBER
LIMIT_COUNT = 4
LINEAR_SPEED = 70
SCAN_LIMITS = [30, 60]


# Change your usb name here (ex. /dev/ttyUSB0) /dev/ttyACM1 COM6
left_half_master = Ring(port=LEFT_PORT_MASTER, baud=BAUD_RATE, timeout=0.1)
right_half_slave = Ring(port=RIGHT_PORT_SLAVE, baud=BAUD_RATE, timeout=0.1)

left_buf = deque()
right_buf = deque()

data: list = []
delta_ts: list = []
prev_ts = 0
left_ts = 0
cnt = 8


def initialization():
    sleep(1)
    left_half_master.process()
    right_half_slave.process()
    print("Scanning starts!")


def main():
    global prev_ts, left_ts, cnt

    # recieve data
    while not left_buf or not right_buf:
        left_input = left_half_master.process()
        right_input = right_half_slave.process()
        if left_input == [[]] or right_input == [[]]:
            sleep(0.1)
            continue
        left_buf.extend(left_input)
        right_buf.extend(right_input)

    # print(f"Left buf: {len(left_buf)}")
    # print(f"Left buf: {len(right_buf)}")

    left_meas = []
    right_meas = []

    while left_buf and right_buf:
        while not left_meas and not right_meas:
            try:
                *left_meas, left_ts = left_buf.popleft()
                *right_meas, right_ts = right_buf.popleft()
            except (IndexError, ValueError):
                left_meas = []
                right_meas = []
                break

            # invert data to radius (and drop outliers)
            left_meas = invert(left_meas, RING_RADIUS, SCAN_LIMITS)
            right_meas = invert(right_meas, RING_RADIUS, SCAN_LIMITS)
            if not left_meas or not right_meas:
                continue

        # check if no log
        if not left_meas or not right_meas:
            lenght = [ts * LINEAR_SPEED for ts in delta_ts]
            # calculate volume
            volume = calculate_volume(
                data,
                lenght,
                ALPHA,
                is_radians=False) * 1e-6
            if volume > 50:
                cnt += 1
                print(f'Volume: {volume:.6f} cm^3')
                with open(f'D:\\Skoltech\\Term 5\\Design Factory\\design_factory\\python\\blender_vis\\data\\groundtruth{cnt}.txt', "w") as file:
                    for item in data:
                        file.write(' '.join(str(k) for k in item))
                        file.write('\n')
                with open(f'D:\\Skoltech\\Term 5\\Design Factory\\design_factory\\python\\blender_vis\\data\\groundtruth{cnt}_len.txt', "w") as file:
                    file.write(' '.join(str(0.4 * k / LINEAR_SPEED) for k in lenght))

                # draw vizualization
                # create_log(
                #     data,
                #     SENSOR_NUMBER,
                #     lenght
                # )
                # exit()
            data.clear()
            delta_ts.clear()
            prev_ts = left_ts

        # check if new data
        if left_ts > prev_ts:
            current_scan = left_meas[:-1] + right_meas + left_meas[-1:]
            # interpolate values
            counter = 0
            for item in current_scan:
                if item is not None:
                    counter += 1
            if counter > LIMIT_COUNT:
                current_scan = interpolate_slice(current_scan)
                print(f'CUR_SCAN: {current_scan}')
                data.append(current_scan)
                delta_ts.append(left_ts - prev_ts)
                prev_ts = left_ts

        # if left_meas or right_meas:
        #     print(left_meas)
        #     print(right_meas)
        left_meas = []
        right_meas = []

    left_buf.clear()
    right_buf.clear()


if __name__ == '__main__':
    initialization()
    while True:
        main()
