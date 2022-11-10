import importlib.util
import sys
import os
import math

from itertools import accumulate


PROJECT_DIR = os.path.dirname(os.path.dirname(os.getcwd()))
SCANS_RELATIVE_DIR = os.path.join('data', 'scans')


# block is same as: import model.volume as model_volume
spec = importlib.util.spec_from_file_location(
    'model.volume',
    os.path.join(PROJECT_DIR, 'py3', 'model', 'volume.py')
)
model_volume = importlib.util.module_from_spec(spec)
sys.modules['model.volume'] = model_volume
spec.loader.exec_module(model_volume)


def create_log(data, lenght, num_of_sensors):
    lenght = [*accumulate(lenght)]

    verts = []
    for layer_num, item in enumerate(data):
        for i, dist in enumerate(item):
            x = lenght[layer_num]
            y = dist * math.sin(math.radians(15 + 15 * i))
            z = dist * math.cos(math.radians(15 + 15 * i))
            verts.append([x, y, z])

    faces = []
    for i in range(len(verts) - 1):
        current_point_id = i
        next_point_id = current_point_id + 1
        if next_point_id % num_of_sensors == 0:
            next_point_id -= num_of_sensors

        next_layer_point_id = current_point_id + num_of_sensors
        next_layer_next_point_id = next_layer_point_id + 1
        if next_layer_next_point_id % num_of_sensors == 0:
            next_layer_next_point_id -= num_of_sensors

        if next_layer_point_id < len(verts):
            faces.append([
                current_point_id,
                next_point_id,
                next_layer_point_id,
            ])
            faces.append([
                next_point_id,
                next_layer_next_point_id,
                next_layer_point_id,
            ])

    return verts, faces