from collections import deque
from time import sleep

from python.parser.serial_read import Ring
from python.parser.invert_measurements import invert
from python.filter.interpolate_slice import interpolate_slice
from python.model.volume import calculate_volume
from python.blender_vis.main import create_log


# Change your usb name here (ex. /dev/ttyUSB0) /dev/ttyACM1 COM6
LEFT_PORT = 'COM6'
RIGHT_PORT = 'COM7'
BAUD_RATE = 115200

# all measuremets are in millimetres
RING_RADIUS = 243
SENSOR_NUMBER = 24
ALPHA = 360 / SENSOR_NUMBER
LINEAR_SPEED = 0.1
SCAN_LIMITS = [50, 0.9 * RING_RADIUS]


# Change your usb name here (ex. /dev/ttyUSB0) /dev/ttyACM1 COM6
left_half_master = Ring(port=LEFT_PORT, baud=BAUD_RATE, timeout=0.1)
right_half_slave = Ring(port=RIGHT_PORT, baud=BAUD_RATE, timeout=0.1)

left_buf = deque()
right_buf = deque()

data: list[list[float]] = []
delta_ts: list[float] = []
prev_ts = 0
left_ts = 0


def initialization():
    sleep(5)
    left_half_master.process()
    right_half_slave.process()
    print("Scanning starts!")


def main():
    # recieve data
    left_buf.extend(left_half_master.process())
    right_buf.extend(right_half_slave.process())

    left_meas = []
    right_meas = []

    while left_buf and right_buf:
        while not left_meas and not right_meas:
            try:
                *left_meas, left_ts = left_buf.popleft()
                *right_meas, right_ts = right_buf.popleft()
            except IndexError:
                break

            # invert data to radius (and drop outliers)
            left_meas = invert(left_meas, RING_RADIUS, SCAN_LIMITS)
            right_meas = invert(right_meas, RING_RADIUS, SCAN_LIMITS)
            if not left_meas or not right_meas:
                continue

            # interpolate values
            left_meas = interpolate_slice(left_meas)
            right_meas = interpolate_slice(right_meas)

        # check if no log
        if not left_meas or not right_meas:
            lenght = [ts * LINEAR_SPEED for ts in delta_ts]
            # calculate volume
            volume = calculate_volume(
                data,
                lenght,
                ALPHA,
                is_radians=False)
            if volume:
                print(f'Volume: {volume}')
            data: list[list[float]] = []
            delta_ts: list[float] = []
            prev_ts = left_ts

            # draw vizualization
            create_log(
                data,
                SENSOR_NUMBER,
                lenght
            )

        # check if new data
        if left_ts > prev_ts:
            current_scan = left_meas[:-1] + right_meas + left_meas[-1]
            data.append(current_scan)
            delta_ts.append(left_ts - prev_ts)
            prev_ts = left_ts


if __name__ == '__main__':
    initialization()
    while True:
        main()
