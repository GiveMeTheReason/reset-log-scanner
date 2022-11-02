def invert(
    scan: list,
    radius: float,
    limits: list
) -> list:
    inverted = [radius - measurement if
                (limits[0] <= radius - measurement <= limits[1])
                else None for measurement in scan]
    for item in inverted:
        if item is not None:
            return inverted
    return []
