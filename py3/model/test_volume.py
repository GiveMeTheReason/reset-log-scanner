import os
from volume import calculate_volume


DATA_FOLDER = os.path.join(
    'data',
    'wood',
)

FILENAMES = (
    'data.txt',
    'groundtruth.txt',
    'generated.txt',
)

sensors = 12
alpha = 360 / sensors


for filename in FILENAMES:
    path_to_file = os.path.join(
        DATA_FOLDER,
        filename
    )

    with open(path_to_file, 'r') as file:
        speed = float(file.readline().strip())
        period = float(file.readline().strip())
        scans = int(file.readline().strip())

        length = speed * period

        points_scans = [[0.] * sensors for _ in range(scans)]

        for i in range(scans):
            scan = list(map(float, file.readline().strip().split()))
            points_scans[i] = scan

    volume = calculate_volume(points_scans, length, alpha, is_radians=False)

    print(filename, volume)
