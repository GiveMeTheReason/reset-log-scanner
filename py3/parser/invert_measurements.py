import typing as tp


def invert(
    scan: tp.List,
    radius: float,
    limits: tp.List
) -> tp.List:
    inverted = [radius - measurement if
                (limits[0] <= radius - measurement <= limits[1])
                else None for measurement in scan]
    for item in inverted:
        if item is not None:
            return inverted
    return []
