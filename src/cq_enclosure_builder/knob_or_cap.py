class KnobOrCap:
    """
    Knobs and Caps

    The distance_from_enclosure_wall is simply an easy way to position the knob/cap;
        the values provided are mostly arbitrary: ideally, we should be able to find it
        dynamically using the inner_depth and whichever pot/button/encoder/etc. we're using.
    """
    def __init__(self, diameter, thickness, inner_depth, distance_from_enclosure_wall, fillet=0):
        self.diameter = diameter
        self.thickness = thickness
        self.inner_depth = inner_depth
        self.distance_from_enclosure_wall = distance_from_enclosure_wall
        self.fillet = fillet