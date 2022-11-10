import pandas as pd
import json
import os

import seaborn as sns

# Plot default settings
sns.set(
    rc={
        'figure.figsize': (12, 12),
        'figure.dpi': 300,
        'axes.grid': True,
        'font.size': 14,
        'legend.loc': 'upper right',
        'legend.borderaxespad': -1,
    },
)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.getcwd()))
LOGS_RELATIVE_DIR = os.path.join('data', 'log_tests')


class AllowedReads:
    MEASUREMENTS = 'Measurements'
    RADIUS_SCAN = 'CUR_SCAN'


def str_to_list(str_list: str) -> list:
    return [float(item) for item in str_list[1:-1].split(', ')]


def read_log(log_filename: str, to_read: str) -> pd.DataFrame:
    result = {}

    with open(log_filename, 'r') as log_data:
        idx = 0
        for line in log_data:
            line_split = line.split(' | ')
            if not line_split[-1].startswith(to_read):
                continue

            timestamp = line_split[0]
            sensors_data = str_to_list(line_split[-1].split(': ')[-1].strip())

            data = {
                str(sensor): sensor_data
                for sensor, sensor_data in enumerate(sensors_data)
            }
            data['timestamp'] = timestamp

            result[idx] = data
            idx += 1

    df = pd.read_json(json.dumps(result), orient='index', convert_dates=True)
    return df


def get_volumes_from_log(log_filename: str) -> list:
    volumes = []

    with open(log_filename, 'r') as log_data:
        for line in log_data:
            line_split = line.split(' | ')
            if not line_split[-1].startswith('Volume'):
                continue

            volumes.append(float(line_split[-1].split(': ')[-1].strip()))

    return volumes
