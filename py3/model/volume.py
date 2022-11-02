import math


def calculate_volume(
    points_scans: list,
    length: float,
    alpha: float = 15,
    is_radians: bool = False
) -> float:
    """
    points: list [plane, scans]
    length: length between planes
    alpha: angle between sensors (default: 15)
    is_radians: if alpha provided in radians (default: False)
    """
    volume = 0.0
    if not is_radians:
        alpha *= math.pi / 180  # to radians
    if isinstance(length, (int, float)):
        length = [length] * len(points_scans)

    plane_num = 0
    while plane_num < len(points_scans) - 1:
        sensor_num = -1
        while sensor_num < len(points_scans[plane_num]) - 1:
            r1_o = points_scans[plane_num][sensor_num]
            r1_d = points_scans[plane_num + 1][sensor_num]
            r2_o = points_scans[plane_num][sensor_num + 1]
            r2_d = points_scans[plane_num + 1][sensor_num + 1]

            volume += (
                length[plane_num] * (
                    2 * r1_o * r1_o +
                    2 * r1_d * r1_d +
                    2 * r2_o * r2_o +
                    2 * r2_d * r2_d +
                    2 * r1_o * r2_o +
                    2 * r1_o * r1_d +
                    2 * r1_d * r2_d +
                    2 * r2_o * r2_d +
                    r1_o * r2_d +
                    r1_d * r2_o
                )
            )

            sensor_num += 1
        plane_num += 1

    volume *= alpha / 36
    return volume
