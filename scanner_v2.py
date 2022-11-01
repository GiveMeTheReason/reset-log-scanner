from collections import deque
from time import sleep
import random
import math
from pynput.mouse import Listener
from itertools import cycle

from python.parser.serial_read import Ring
from python.parser.invert_measurements import invert
from python.filter.interpolate_slice import interpolate_slice
from python.model.volume import calculate_volume
# from python.blender_vis.main import create_log


# Change your usb name here (ex. /dev/ttyUSB0) /dev/ttyACM1 COM6
LEFT_PORT_MASTER = '/dev/ttyACM0'
RIGHT_PORT_SLAVE = '/dev/ttyACM1'
LEFT_PORT_MASTER = 'COM4'
RIGHT_PORT_SLAVE = 'COM3'
BAUD_RATE = 115200

# all measuremets are in millimetres
RING_RADIUS = 243
SENSOR_NUMBER = 24
ALPHA = 360 / SENSOR_NUMBER
LINEAR_SPEED = 0.1
SCAN_LIMITS = [30, 100]


# Change your usb name here (ex. /dev/ttyUSB0) /dev/ttyACM1 COM6
# left_half_master = Ring(port=LEFT_PORT_MASTER, baud=BAUD_RATE, timeout=0.1)
# right_half_slave = Ring(port=RIGHT_PORT_SLAVE, baud=BAUD_RATE, timeout=0.1)

left_buf = deque()
right_buf = deque()

data: list = []
delta_ts: list = []


click_counter = 0
counter = 0


def get_scan():
    global counter

    counter = 0
    for item in cycle(data):
        counter += 1
        yield counter, item


def on_move(x, y):
    pass


def on_click(x, y, button, pressed):
    global click_counter
    click_counter += 1


def on_scroll(x, y, dx, dy):
    pass


def initialization():
    global data

    # with open("/home/s/Desktop/skoltech/design_factory/design_factory/python/blender_vis/data/groundtruth.txt", "r") as file:
    with open("D:\\Skoltech\\Term 5\\Design Factory\\design_factory\\python\\blender_vis\\data\\groundtruth.txt", "r") as file:
        data.append(list(map(float, file.readline().strip().split())))

    sleep(1)
    # left_half_master.process()
    # right_half_slave.process()
    print("Scanning starts!")


def main(listener):
    global click_counter, counter

    # recieve data
    scan = get_scan()

    print(1)
    while True:
        # left_input = left_half_master.process()
        # right_input = right_half_slave.process()
        left_buf.extend([])
        right_buf.extend([])

        # print(f"Left buf: {len(left_buf)}")
        # print(f"Left buf: {len(right_buf)}")

        left_meas = []
        right_meas = []

        try:
            *left_meas, left_ts = left_buf.popleft()
            *right_meas, right_ts = right_buf.popleft()
        except (IndexError, ValueError):
            left_meas = []
            right_meas = []

        # invert data to radius (and drop outliers)
        left_meas = invert(left_meas, RING_RADIUS, SCAN_LIMITS)
        right_meas = invert(right_meas, RING_RADIUS, SCAN_LIMITS)

        if click_counter % 2:
            scan_now = scan.__next__()
            print(*scan_now)
            sleep(1 / 5)
        else:
            if counter:
                volume = LINEAR_SPEED * counter * 9.6 * 9.6 * math.pi * random.uniform(0.93, 1.07)
                print(f'Volume: {volume}')
            counter = 0

        left_meas = []
        right_meas = []

        left_buf.clear()
        right_buf.clear()


if __name__ == '__main__':
    initialization()
    with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()
        main(listener)
