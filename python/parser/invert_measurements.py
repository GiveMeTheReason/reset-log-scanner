def invert(
    scan: list[float],
    radius: float,
    limits: list[float]
) -> list[float | None]:
    inverted = [radius - measurement if
                (limits[0] <= radius - measurement <= limits[1])
                else None for measurement in scan]
    for item in inverted:
        if item is not None:
            return inverted
    return []
