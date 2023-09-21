import cadquery as cq
from cq_enclosure_builder.part import Part
from cq_enclosure_builder.parts_factory import register_part

@register_part("support", "pyramid")
class PyramidSupportPart(Part):
    def __init__(
        self,
        enclosure_wall_thickness,
        support_height,
        base_size = 8,
        top_size = 5,
        pyramid_taper = 20
    ):
        super().__init__()

        # Board
        board = (
            cq.Workplane("front")
                .rect(base_size, base_size)
                .extrude(support_height, taper=pyramid_taper)
        )
        board = board.add(
            cq.Workplane("front")
                .rect(top_size, top_size)
                .extrude(support_height)
        )

        self.part = board
        self.mask = (
            cq.Workplane("front")
                .box(base_size, base_size, enclosure_wall_thickness, centered=(True, True, False))
        )

        self.size.width     = base_size
        self.size.length    = base_size
        self.size.thickness = support_height

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_offset = (0, 0)
        self.outside_footprint = (0, 0)
        self.debug_objects.footprint.inside  = board
        self.debug_objects.footprint.outside = None
        self.debug_objects.hole = None