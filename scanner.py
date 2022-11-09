import glob
import logging
import logging.config
import typing as tp
from collections import deque
from datetime import datetime
from time import sleep

from py3.parser.serial_read import Ring
from py3.parser.invert_measurements import invert
from py3.filter.interpolate_slice import interpolate_slice
from py3.model.volume import calculate_volume
# from py3.blender_vis.main import create_log

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
SCAN_LIMITS = [-10000000, 10000000]
SCAN_LIMITS = [30, 80]


# logger
log_files = sorted(glob.glob('logs/*_*.log'))
log_file_num = '000'
if log_files:
    log_file_num = str(int(log_files[-1][5:8]) + 1).zfill(3)
log_filename = f'logs/{log_file_num}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
# logging.basicConfig(filename=log_filename, encoding='utf-8', level=logging.INFO)
conf = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {'custom': {'format': '%(asctime)s | %(levelname)-8s | %(message)s'}},
    'handlers': {'to_file': {'class': 'logging.FileHandler',
                             'filename': log_filename,
                             'formatter': 'custom',
                             'level': 'INFO',
                             'mode': 'a'},
                # 'to_stdout': {'class': 'logging.StreamHandler',
                #               'formatter': 'custom',
                #               'level': 'INFO',
                #               'stream': 'ext://sys.stdout'},
                },
    'root': {'handlers': [
        # 'to_stdout',
        'to_file'
    ], 'level': 'INFO'},
}
logging.config.dictConfig(conf)


# Change your usb name here (ex. /dev/ttyUSB0) /dev/ttyACM1 COM6
left_half_master = Ring(port=LEFT_PORT_MASTER, baud=BAUD_RATE, timeout=0.1)
right_half_slave = Ring(port=RIGHT_PORT_SLAVE, baud=BAUD_RATE, timeout=0.1)

left_buf = deque()
right_buf = deque()

data: tp.List = []
delta_ts: tp.List = []
prev_ts: int = 0
left_ts: int = 0

scan_num = len(glob.glob('data/scans/scan_*.txt')) // 2


def initialization():
    sleep(1)
    left_half_master.process()
    right_half_slave.process()
    logging.info('Scanning starts!')


def main():
    global prev_ts, left_ts, scan_num

    # recieve data
    while not left_buf or not right_buf:
        left_input = left_half_master.process()
        right_input = right_half_slave.process()
        if left_input == [[]] or right_input == [[]]:
            sleep(0.1)
            continue
        left_buf.extend(left_input)
        right_buf.extend(right_input)

    # logging.info(f'Left buf: {len(left_buf)}')
    # logging.info(f'Right buf: {len(right_buf)}')

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

            # record scan
            logging.info(f'Measurements: {left_meas[:-1] + right_meas + left_meas[-1:]}')

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
            if volume > 1:
                logging.info(f'Volume: {volume:.6f}')
                print(volume)
                with open(f'data/scans/scan_{str(scan_num).zfill(3)}.txt', 'w') as file:
                    for item in data:
                        file.write(' '.join(str(k) for k in item))
                        file.write('\n')
                with open(f'data/scans/scan_len_{str(scan_num).zfill(3)}.txt', 'w') as file:
                    file.write(' '.join(str(k) for k in lenght))
                scan_num += 1

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
            if counter > 3:
                current_scan = interpolate_slice(current_scan)
                logging.info(f'CUR_SCAN: {current_scan}')
                data.append(current_scan)
                delta_ts.append(left_ts - prev_ts)
                prev_ts = left_ts

        # if left_meas or right_meas:
        #     logging.info(f'Left: {left_meas})
        #     logging.info(f'Right: {right_meas})
        left_meas = []
        right_meas = []

    left_buf.clear()
    right_buf.clear()


if __name__ == '__main__':
    initialization()
    while True:
        main()
