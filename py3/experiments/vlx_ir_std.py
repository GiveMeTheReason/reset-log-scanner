import os

from utils.stats import Data, Sample_statistics

import matplotlib.pyplot as plt


EXPERIMENTS_FILENAME = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'data',
    'experiments',
    os.path.splitext(os.path.basename(__file__))[0] + '.txt',
)
RESULTS_FILENAME = os.path.join(
    os.path.dirname(__file__),
    'results',
    os.path.splitext(os.path.basename(__file__))[0]
)


sensors = []
data = Data()
points_set = []

with open(EXPERIMENTS_FILENAME, 'r') as file:
    first_line = file.readline().strip().split()
    for sensor in first_line[::2]:
        sensors.append(sensor)
    for point in first_line[1::2]:
        points_set.append(Sample_statistics())
        points_set[-1].add(float(point))

    for line in file:
        line = line.strip().split()

        if line:
            for i, point in enumerate(line[1::2]):
                points_set[i].add(float(point))

    for point_set in points_set:
        data.mean_points.append(point_set.mean)
        data.var_points.append(point_set.var)
        data.std_points.append(point_set.std)


print('Done!\n')
print(data)


plt.errorbar(range(len(sensors)), data.mean_points, data.std_points,
             linestyle='None', marker='o')
plt.title(
    'STD measurement experiment\n' +
    '\n'.join([
        f'{sensor} | Mean: {data.mean_points[i]:.3f}; STD: {data.std_points[i]:.3f}' for i, sensor in enumerate(sensors)
    ])
)
plt.xlabel('Sensors')
plt.ylabel('Measurements, mm')
plt.xticks(range(len(sensors)), sensors)
plt.grid()
plt.savefig(RESULTS_FILENAME, dpi=300)
plt.show()


points = [[0]*1000 for _ in range(2)]
with open(EXPERIMENTS_FILENAME, 'r') as file:
    for l, line in enumerate(file):
        line = line.strip().split()
        if line:
            for i, point in enumerate(line[1::2]):
                points[i][l] = float(point)

plt.boxplot(points)
plt.title(
    'BoxPlot measurement experiment\n' +
    '\n'.join([
        f'{sensor} | Mean: {data.mean_points[i]:.3f}; STD: {data.std_points[i]:.3f}' for i, sensor in enumerate(sensors)
    ])
)
plt.xlabel('Sensors')
plt.ylabel('Measurements, mm')
plt.xticks(range(1, 1 + len(sensors)), sensors)
plt.grid()
plt.savefig(RESULTS_FILENAME + '_boxplot', dpi=300)
plt.show()
