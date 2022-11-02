import os
import math


DATA_FOLDER = os.path.join(
    'data',
    'wood',
)

FILENAME = 'generated.txt'

SPEED = 1
PERIOD = 0.1
SCANS = 61
RADIUS = 0.5
SENSORS = 12

SHIFT_X = 0
SHIFT_Y = 0.5

shift_r = pow(SHIFT_X ** 2 + SHIFT_Y ** 2, 1/2)
shift_alpha = math.atan2(SHIFT_Y, SHIFT_X)

alpha_rad = 360 / SENSORS * math.pi / 180

volume_true = math.pi * RADIUS ** 2 * (SPEED * (SCANS - 1) * PERIOD)

path = os.path.join(DATA_FOLDER, FILENAME)
with open(path, 'w') as file:
    file.writelines(''.join(f'{line}\n' for line in (SPEED, PERIOD, SCANS)))

    radius = [0] * SENSORS
    for scan in range(SCANS):
        for i in range(SENSORS):
            angle_i = alpha_rad * i
            radius[i] = shift_r * math.cos(angle_i - shift_alpha) + pow(RADIUS ** 2 - shift_r ** 2 * math.sin(angle_i - shift_alpha) ** 2, 1/2)
        file.write(' '.join(str(r) for r in radius))
        file.write('\n')

print(volume_true)
