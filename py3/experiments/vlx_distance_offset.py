import os
from sklearn.linear_model import LinearRegression

from utils.stats import Data, Sample_statistics

import matplotlib.pyplot as plt


EXPERIMENTS_FILENAME = os.path.join(
    'data',
    'experiments',
    os.path.splitext(os.path.basename(__file__))[0] + '.txt'
)
RESULTS_FILENAME = os.path.join(
    os.path.dirname(__file__),
    'results',
    os.path.splitext(os.path.basename(__file__))[0]
)


distances = []
data = Data()
points = Sample_statistics()

with open(EXPERIMENTS_FILENAME, 'r') as file:
    for line in file:
        line = line.strip().split()

        if len(line) == 2 and line[0].isnumeric():
            try:
                data.std_points.append(points.std)
                data.var_points.append(points.var)
                data.mean_points.append(points.mean)
            except Sample_statistics.NotEnoughtInstancesError:
                if distances:
                    distances.pop()

            distances.append(float(line[0]))
            points.clear()

        elif len(line) == 1 and line[0].isnumeric():
            points.add(float(*line))

    try:
        data.std_points.append(points.std)
        data.var_points.append(points.var)
        data.mean_points.append(points.mean)
    except Sample_statistics.NotEnoughtInstancesError:
        if distances:
            distances.pop()


print('Done!\n')
print(
    f'{"Distances:" : <11}'
    f'{"".join(str(round(d, 2)).rjust(8) for d in distances)}\n'
)
print(data)

model = LinearRegression()
model.fit([[point] for point in data.mean_points], distances)

print('MODEL_COEFFICIENTS:\n', *model.coef_, model.intercept_)


plt.errorbar(distances, distances,
             linestyle='-')
plt.errorbar(distances, [(dist - model.intercept_) / model.coef_[0] for dist in distances],
             linestyle='-')
plt.errorbar(distances, data.mean_points, data.std_points,
             linestyle='None', marker='o')
plt.title(
    'Distance measurement experiment\n' +
    f'Model: Distance = {model.coef_[0]:.3f} * Measurement + {model.intercept_:.3f}'
)
plt.legend([
    'Ideal measurements',
    'Model',
    'Measurements',
])
plt.xlabel('Real distance, mm')
plt.ylabel('Measurement, mm')
plt.grid()
plt.savefig(RESULTS_FILENAME, dpi=300)
plt.show()
