from itertools import chain


def interpolate(first: float, last: float, length: int) -> list:
    """Interpolates values from start to end over length

    Args:
        first (float): first value
        last (float): last value
        length (int): number of values to interpolate

    Returns:
        list: interpolated values in between
    """
    interpolated = [0.] * length
    for i in range(length):
        interpolated[i] = (last - first) / (length + 1) * (i + 1) + first
    return interpolated


def interpolate_slice(scan: list) -> list:
    """Filters None values by linearinterpolation in one round scan

    Args:
        scan (list): scan values

    Returns:
        list: filtered values
    """
    n = len(scan)
    filtered = [0.] * n
    first_index = -1
    first_measurement = -1
    for i, measurement in enumerate(chain(scan, scan)):
        if measurement is None:
            continue
        if first_index > -1:
            interpolated = interpolate(
                first_measurement,
                measurement,
                i - 1 - first_index
            )
            for j, value in enumerate(interpolated):
                filtered[(j + first_index + 1) % n] = value
        filtered[i % n] = measurement
        first_index = i
        first_measurement = measurement
    return filtered
