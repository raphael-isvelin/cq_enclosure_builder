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
import cq_warehouse.extensions
from cq_warehouse.fastener import PanHeadScrew

from cq_enclosure_builder.part import Part
from cq_enclosure_builder.parts_factory import register_part

M2_SIZE = 2


@register_part("usb_c", "ChengHaoRan E")
class UsbCChengHaoRanEPart(Part):
    """
    USB C female connector ChengHaoRan E

    https://www.aliexpress.com/item/1005002320414960.html
    """

    # TODO refactor or rewrite!
    def __init__(
        self,
        enclosure_wall_thickness: float,
        orientation_vertical: bool = False,
        center_is_outward_facing_hole: bool = True,
        rotate_180: bool = True,
    ):
        if not center_is_outward_facing_hole:
            print("WARNING: use of center_is_outward_facing_hole=False in USB C is deprecated; the layout builder assumes True, it can cause alignment issues")

        super().__init__()

        width = 18
        length = 18

        slope_size = 4

        half_width = width / 2
        half_length = length / 2
        half_slope_size = slope_size / 2

        usb_c_depth = 10.2
        usb_c_pos = (0, 1.4)
        usb_c_tilt = 0
        usb_c_error_margin = 0.4

        wall_thickness = usb_c_depth - enclosure_wall_thickness

        screws_pos = [
            (-6.6, -1.5),  # Top-Left (from the outside; after rotation; horizontal)
            (-6.6, 6.4),   # Bottom-Left
            (6.4, 6.6),    # Bottom-Right
            (6.4, -1.5)    # Top-Right
        ]
        screw = PanHeadScrew(size="M2-0.4", fastener_type="iso1580", length=6)
        screw_hole_depth = wall_thickness - 1.4

        # Board
        board = cq.Workplane("front").box(width, length, enclosure_wall_thickness, centered=(True, True, False))

        # Walls
        board = (
            board
                .faces(">Z")
                .workplane()
                .moveTo(0, 2.5)
                .rect(width, length - 5)
                .extrude(wall_thickness)
        )

        # Screws
        board = (
            board
                .faces(">Z")
                .workplane()
                .pushPoints(screws_pos)
                .threadedHole(fastener=screw, depth=screw_hole_depth, counterSunk=False)
        )

        # USB C hole
        usb_c_w = 9.0 + usb_c_error_margin
        usb_c_l = 3.2 + usb_c_error_margin
        usb_c_ellipse_size = 1.8
        usb_c_middle_size = usb_c_w - (usb_c_ellipse_size*2)
        usb_c_l_half = usb_c_l / 2
        usb_c_hole = (
            cq.Workplane("front")
                .workplane()

                .moveTo(usb_c_middle_size / 2, 0)
                .ellipse(usb_c_ellipse_size, usb_c_l_half)
                .moveTo(-(usb_c_middle_size / 2), 0)
                .ellipse(usb_c_ellipse_size, usb_c_l_half)
                .extrude(enclosure_wall_thickness)

                .moveTo(0, 0)
                .rect(usb_c_middle_size, usb_c_l)
                .extrude(enclosure_wall_thickness)

                .translate([*usb_c_pos, 0])
        )

        # USB C cavity
        cavity_w = usb_c_w + 0.4
        cavity_l = 4.2 + 0.4
        ubs_c_cavity = (
            cq.Workplane("front")
                .workplane()
                .box(cavity_w, cavity_l, wall_thickness, centered=(True, True, False))

                .translate([*usb_c_pos, enclosure_wall_thickness])
        )


        # USB C hole & cavity
        board = (
            board
                .faces(">Z")
                .workplane()
                .cut(usb_c_hole)
                .cut(ubs_c_cavity)
        )

        # Mask & footprint
        mask = (
            cq.Workplane("front")
                .box(width, length, enclosure_wall_thickness, centered=(True, True, False))
        )

        # Re-centering
        if center_is_outward_facing_hole:  # TODO refactor - deal with centering at the end
            board = board.translate([-usb_c_pos[0], -usb_c_pos[1], 0])
            mask = mask.translate([-usb_c_pos[0], -usb_c_pos[1], 0])
            usb_c_hole = usb_c_hole.translate([-usb_c_pos[0], -usb_c_pos[1], 0])
            ubs_c_cavity = ubs_c_cavity.translate([-usb_c_pos[0], -usb_c_pos[1], 0])

        # Slope
        if orientation_vertical:
            wedge = (
                cq.Workplane("XZ")
                    .polyline([ (half_width, enclosure_wall_thickness), (half_width + slope_size, enclosure_wall_thickness), (half_width, usb_c_depth) ])
                    .close()
                    .extrude(length - 5)
                    .translate([0, half_length, 0])
            )
            board_extension = (
                cq.Workplane("front")
                    .box(slope_size, length - 5, enclosure_wall_thickness, centered=(True, False, False))
                    .translate([half_width + slope_size/2, -4, 0])
            )
            if center_is_outward_facing_hole:
                wedge = wedge.translate([-usb_c_pos[0], -usb_c_pos[1], 0])
                board_extension = board_extension.translate([-usb_c_pos[0], -usb_c_pos[1], 0])
            board = board.union(wedge).union(board_extension)
            mask = mask.union(board_extension)
            if not center_is_outward_facing_hole:
                board = board.translate([-half_slope_size, 0, 0])
                mask = mask.translate([-half_slope_size, 0, 0])
                usb_c_hole = usb_c_hole.translate([-half_slope_size, 0, 0])
                ubs_c_cavity = ubs_c_cavity.translate([-half_slope_size, 0, 0])
        else: # horizontal
            wedge = (
                cq.Workplane("YZ")
                    .polyline([ (half_length, enclosure_wall_thickness), (half_length + slope_size, enclosure_wall_thickness), (half_length, usb_c_depth) ])
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
                wedge = wedge.translate([-usb_c_pos[0], -usb_c_pos[1], 0])
                board_extension = board_extension.translate([-usb_c_pos[0], -usb_c_pos[1], 0])
            board = board.union(wedge).union(board_extension)
            mask = mask.union(board_extension)
            if not center_is_outward_facing_hole:
                board = board.translate([0, -half_slope_size, 0])
                mask = mask.translate([0, -half_slope_size, 0])
                usb_c_hole = usb_c_hole.translate([0, -half_slope_size, 0])
                ubs_c_cavity = ubs_c_cavity.translate([0, -half_slope_size, 0])

        rotate_by = -90 if orientation_vertical else 180
        board = board.rotate((0, 0, 0), (0, 0, 1), rotate_by)
        mask = mask.rotate((0, 0, 0), (0, 0, 1), rotate_by)
        usb_c_hole = usb_c_hole.rotate((0, 0, 0), (0, 0, 1), rotate_by)
        ubs_c_cavity = ubs_c_cavity.rotate((0, 0, 0), (0, 0, 1), rotate_by)

        # Huh, I really need to cleanup this class
        reverse = -1 if rotate_180 else 1
        if rotate_180:
            # board = board.mirror("XZ")
            # mask = board.mirror("XZ")
            # usb_hole = board.mirror("XZ")
            board = board.rotate((0, 0, 0), (0, 0, 1), 180)
            mask = mask.rotate((0, 0, 0), (0, 0, 1), 180)
            usb_c_hole = usb_c_hole.rotate((0, 0, 0), (0, 0, 1), 180)
        # else:
            ubs_c_cavity = ubs_c_cavity.rotate((0, 0, 0), (0, 0, 1), 180)

        self.part = board
        self.mask = mask

        self.size.width     = 18  # TODO unhardcode when rewriting
        self.size.length    = 22
        self.size.thickness = enclosure_wall_thickness + wall_thickness

        pcb_thickness = 2
        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = usb_c_depth - enclosure_wall_thickness + pcb_thickness
        self.inside_footprint_offset = (0, reverse * -0.6) if not orientation_vertical else (reverse * -1.4, reverse * -2)

        self.outside_footprint = (usb_c_w if not orientation_vertical else usb_c_l, usb_c_l if not orientation_vertical else usb_c_w)
        self.outside_footprint_thickness = 3

        footprint_in = (
            cq.Workplane("front")
                .rect(self.size.width, self.size.length)
                .extrude(self.inside_footprint_thickness)
                .translate([0, 0, enclosure_wall_thickness])
        )
        footprint_in = footprint_in.translate([*self.inside_footprint_offset, 0])

        footprint_out = (
            cq.Workplane("front")
                .rect(*self.outside_footprint)
                .extrude(self.outside_footprint_thickness)
                .translate([0, 0, -self.outside_footprint_thickness])
        )

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out
        
        self.debug_objects.hole = usb_c_hole.add(ubs_c_cavity)