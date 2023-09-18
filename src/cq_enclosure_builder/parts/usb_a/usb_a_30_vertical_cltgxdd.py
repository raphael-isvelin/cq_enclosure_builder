"""
   Copyright 2023 Raphaël Isvelin

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import cadquery as cq
from cq_warehouse.fastener import PanHeadScrew
from cq_enclosure_builder.part import Part
from cq_enclosure_builder.parts_factory import register_part

@register_part("usb_a", "3.0 vertical cltgxdd")
class UsbA30VerticalCltgxddPart(Part):
    """
    USB A female connector 3.0 vertical cltgxdd

    https://www.aliexpress.com/item/1005003329405836.html
    """

    def __init__(self, enclosure_wall_thickness, orientation_vertical=False, center_is_outward_facing_hole=True):
        super().__init__()

        width = 25.2
        length = 22.8

        slope_size = 4

        half_width = width / 2
        half_length = length / 2
        half_slope_size = slope_size / 2

        usb_hole_error_margin = 0.6
        usb_depth_error_margin = 0.2

        usb_size = (14.6 + usb_hole_error_margin, 7.0 + usb_hole_error_margin)
        usb_depth = 15 - usb_depth_error_margin

        usb_pos = (0, 6.6)
        screws_pos = [
            (-10.15, -0.2),
            (+10.15, -0.2)
        ]

        wall_thickness = usb_depth - enclosure_wall_thickness

        screw = PanHeadScrew(size="M2-0.4", fastener_type="iso1580", length=6)
        screw_hole_depth = wall_thickness - 1.4

        # Board
        board = cq.Workplane("front").box(width, length, enclosure_wall_thickness, centered=(True, True, False))

        # Walls
        board = (
            board
                .faces(">Z")
                .workplane()
                .moveTo(0, 4)
                .rect(width, length - 8)
                .extrude(wall_thickness)
        )

        # USB hole
        usb_hole = (
            cq.Workplane("front")
                .workplane()
                .rect(*usb_size)
                .extrude(usb_depth)
                .translate([*usb_pos, 0])
        )
        board = (
            board
                .faces(">Z")
                .workplane()
                .cut(usb_hole)
        )

        # Screws
        board = (
            board
                .faces(">Z")
                .workplane()
                .pushPoints(screws_pos)
                .threadedHole(fastener=screw, depth=screw_hole_depth, counterSunk=False)
        )

        # Mask & footprint
        mask = (
            cq.Workplane("front")
                .box(width, length, enclosure_wall_thickness, centered=(True, True, False))
        )

        # Re-centering
        if center_is_outward_facing_hole:
            board = board.translate([-usb_pos[0], -usb_pos[1], 0])
            mask = mask.translate([-usb_pos[0], -usb_pos[1], 0])
            usb_hole = usb_hole.translate([-usb_pos[0], -usb_pos[1], 0])

        # Slope
        if orientation_vertical:
            wedge = (
                cq.Workplane("XZ")
                    .polyline([ (half_width, enclosure_wall_thickness), (half_width + slope_size, enclosure_wall_thickness), (half_width, usb_depth) ])
                    .close()
                    .extrude(length - 8)
                    .translate([0, half_length, 0])
            )
            board_extension = (
                cq.Workplane("front")
                    .box(slope_size, length - 8, enclosure_wall_thickness, centered=(True, True, False))
                    .translate([half_width + slope_size/2, 4, 0])
            )
            if center_is_outward_facing_hole:
                wedge = wedge.translate([-usb_pos[0], -usb_pos[1], 0])
                board_extension = board_extension.translate([-usb_pos[0], -usb_pos[1], 0])
            board = board.union(wedge).union(board_extension)
            mask = mask.union(board_extension)
            if not center_is_outward_facing_hole:
                board = board.translate([-half_slope_size, 0, 0])
                mask = mask.translate([-half_slope_size, 0, 0])
                usb_hole = usb_hole.translate([-half_slope_size, 0, 0])
        else: # horizontal
            wedge = (
                cq.Workplane("YZ")
                    .polyline([(half_length, enclosure_wall_thickness), (half_length + slope_size, enclosure_wall_thickness), (half_length, usb_depth)])
                    .close()
                    .extrude(width)
                    .translate([-half_width, 0, 0])
            )
            board_extension = (
                cq.Workplane("front")
                    .box(width, slope_size, enclosure_wall_thickness, centered=(True, False, False))
                    .translate([0, half_length, 0])
            )
            if center_is_outward_facing_hole:
                wedge = wedge.translate([-usb_pos[0], -usb_pos[1], 0])
                board_extension = board_extension.translate([-usb_pos[0], -usb_pos[1], 0])
            board = board.union(wedge).union(board_extension)
            mask = mask.union(board_extension)
            if not center_is_outward_facing_hole:
                board = board.translate([0, -half_slope_size, 0])
                mask = mask.translate([0, -half_slope_size, 0])
                usb_hole = usb_hole.translate([0, -half_slope_size, 0])

        rotate_by = -90 if orientation_vertical else 180
        board = board.rotate((0, 0, 0), (0, 0, 1), rotate_by)
        mask = mask.rotate((0, 0, 0), (0, 0, 1), rotate_by)
        usb_hole = usb_hole.rotate((0, 0, 0), (0, 0, 1), rotate_by)

        self.part = board
        self.mask = mask

        self.size.width     = 22.8 if orientation_vertical else 25.2  # TODO unhardcode
        self.size.length    = 29.2 if orientation_vertical else 26.8
        self.size.thickness = enclosure_wall_thickness + wall_thickness

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_offset = (0, 4.6) if not orientation_vertical else (-6.6, -2, 0)
        self.outside_footprint = (usb_size[0] if not orientation_vertical else usb_size[1], usb_size[1] if not orientation_vertical else usb_size[0])
        footprint_in = (
            cq.Workplane("front")
                .rect(self.size.width, self.size.length)
                .extrude(usb_depth - enclosure_wall_thickness)
                .translate([0, 0, enclosure_wall_thickness])
        )
        if orientation_vertical:
            footprint_in = footprint_in.translate([-6.6, -2, 0])  # TODO unhardcode
        else:
            footprint_in = footprint_in.translate([0, 4.6, 0])
        outside_footprint_thickness = 3
        footprint_out = (
            cq.Workplane("front")
                .rect(*self.outside_footprint)
                .extrude(outside_footprint_thickness)
                .translate([-0, 0, -outside_footprint_thickness])
        )
        self.outside_footprint = usb_size  # TODO check why override??

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out
        
        self.debug_objects.hole = usb_hole