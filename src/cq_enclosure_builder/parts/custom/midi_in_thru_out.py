import cadquery as cq

from cq_enclosure_builder.part import Part
from cq_enclosure_builder.parts_factory import register_part


PART_CATEGORY = "custom"
PART_ID = "MIDI_In-Thru-Out"

"""
Part combined two MIDI connectors for In and Out, and one TRS 3.5mm for Thru
"""
@register_part(PART_CATEGORY, PART_ID)
class MidiInThruOutPart(Part):
    # TODO can improve by calculating some values, as most are hardcoded based on other values

    def __init__(
        self,
        enclosure_wall_thickness: float
    ):
        super().__init__()

        connector_size = (28.4, 19.2)

        connector_screws_pos = [
            (-10.8, -13.4), (10.8, -13.4),
            (-10.8, 13.4), (10.8, 13.4),
        ]
        midi_hole_pos = [ (0, -13.4), (0, 13.4) ]

        board_size = (28.2, 46, enclosure_wall_thickness)

        midi_hole_diameter = 15.1 + 0.5
        screw_holes_diameter = 2.9 + 0.3
        midi_depth = 18.6  # behind/in wall
        midi_diameter = 15.2
        midi_depth_margin = 2

        trs_pos = (10.053, 0)
        wall_thickness_for_trs = 1
        trs_thread_depth = 4.6
        trs_nut_depth = 2
        trs_nut_diameter = 7.9
        trs_thread_diameter = 5.85 + 0.6
        trs_body_diameter = 8 + 1
        trs_body_depth_excluding_thread = 18
        trs_body_depth_margin = 2

        # Board
        self.part = (
            cq.Workplane("front")
                .box(*board_size, centered=(True, True, False))

                # Main MIDI holes
                .faces(">Z").workplane()
                .pushPoints(midi_hole_pos)
                .hole(midi_hole_diameter)

                # Screw holes
                .faces(">Z").workplane()
                .pushPoints(connector_screws_pos)
                .hole(screw_holes_diameter)

                # TRS 3.5mm recess
                .faces(">Z").workplane()
                .pushPoints([trs_pos])
                .circle(trs_body_diameter/2)
                .extrude(-(enclosure_wall_thickness - wall_thickness_for_trs), combine="cut")

                # TRS 3.5mm hole
                .faces("<Z").workplane()
                .pushPoints([trs_pos])
                .circle(trs_thread_diameter/2)
                .extrude(-5, combine="cut")
        )

        # Mask
        self.mask = (
            cq.Workplane("front")
                .box(*board_size, centered=(True, True, False))
        )

        self.size.width, self.size.length, self.size.thickness = board_size

        # Inside footprint
        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = 21
        self.inside_footprint_offset = (0, 0)

        footprint_in = (
            cq.Workplane("front")
                .rect(*self.inside_footprint)
                .extrude(self.inside_footprint_thickness - enclosure_wall_thickness)
                .translate([0, 0, enclosure_wall_thickness])
        )
        footprint_in.add(
            cq.Workplane("front")
                .pushPoints([trs_pos])
                .circle(trs_body_diameter/2)
                .extrude(trs_body_depth_excluding_thread+trs_body_depth_margin)
                .translate([0, 0, wall_thickness_for_trs])
        )
        for pos in midi_hole_pos:
            footprint_in.add(
                cq.Workplane("front")
                    .pushPoints([pos])
                    .circle(midi_diameter/2)
                    .extrude(midi_depth-enclosure_wall_thickness+midi_depth_margin)
                    .translate([0, 0, enclosure_wall_thickness])
            )
        footprint_in.add(
            cq.Workplane("front")
                .pushPoints(connector_screws_pos)
                .circle(3.2/2)
                .extrude(-10)
                .translate([0, 0, 10 + enclosure_wall_thickness])
        )
        self.debug_objects.footprint.inside  = footprint_in

        # Outside footprint
        self.outside_footprint = (self.size.width, self.size.length)
        self.outside_footprint_thickness = 3
        self.outside_footprint_offset = (0, 0)

        diamond = self.build_diamond(connector_size)
        footprint_out = cq.Workplane("front")
        for pos in midi_hole_pos:
            footprint_out.add(diamond.translate([*pos, 0]))
        footprint_out.add(
            cq.Workplane("front")
                .pushPoints([trs_pos])
                .circle(trs_nut_diameter/2)
                .extrude(trs_nut_depth)
                .faces("<Z").workplane()
                .pushPoints([trs_pos])
                .circle(5.7/2)
                .extrude(1)
                .translate([0, 0, -trs_nut_depth])
        )

        self.debug_objects.footprint.outside = footprint_out


    def build_diamond(self, connector_size):
        midi_outside_footprint_depth = 1.8
        # Front panel (very rough estimation--should normally follow the curves of the holes)
        # length and width voluntarily swapped out
        hwx = (connector_size[1] / 2) + 0.2
        hlx = (connector_size[0] / 2) + 1.6
        points = [ (-hwx, 0), (0, -hlx), (hwx, 0), (0, hlx) ]
        return (
            cq.Workplane("XY")
                .moveTo(*points[0]).lineTo(*points[1]).lineTo(*points[2]).lineTo(*points[3])
                .close()
                .extrude(midi_outside_footprint_depth)
                .edges("|Z")
                .fillet(2.0)
                .rotate((0, 0, 0), (0, 0, 1), 90)
                .translate([0, 0, -midi_outside_footprint_depth])
        )