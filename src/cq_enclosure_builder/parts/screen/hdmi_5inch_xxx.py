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
import math
from cq_enclosure_builder.part import Part, AssemblyPart
from cq_enclosure_builder.parts_factory import register_part
from cq_enclosure_builder.parts.common.default_screw_block import DefaultScrewBlock
from cq_enclosure_builder.utils.workplane_utils import scale

def required_taper_for_x(x, x_resulting, h):
    delta_x = (x_resulting - x) / 2
    alpha_x = math.degrees(math.atan(delta_x / h))
    return alpha_x

def tapered_dimensions(x, y, h, alpha):
    alpha_rad = math.radians(alpha)
    delta_y = h * math.tan(alpha_rad)
    return y + 2 * delta_y

@register_part("screen", "HDMI 5 inch XXX")
class Hdmi5InchXxxPart(Part):
    """
    HDMI 5 inch screen

    LINK_HERE
    """

    def __init__(self, enclosure_wall_thickness, center_is_outward_facing_hole=True):
        super().__init__()

        screen_viewing_area_size = (109.2-1, 65.6-1.4)
        screen_bevel_size = (3.2, 7.6, 6.4, 6.4)  # top, bottom, left, right

        viewing_area_offset = (0, -1.6)

        ramp_base_thickness = 1.2
        ramp_slope_thickness = 2
        part_thickness = ramp_base_thickness + ramp_slope_thickness
        screw_block_thickness = 6

        ramp_width_l_plus_r = 8     # 1mm on the left + 1mm on the right
        ratio_bevel_lr_to_bt = 1.5  # N times less than ^ for top and bottom

        screen_w_bevel_size = (
            screen_viewing_area_size[0] + screen_bevel_size[2] + screen_bevel_size[3],
            screen_viewing_area_size[1] + screen_bevel_size[0] + screen_bevel_size[1]
        )
        screen_board_size = (
            # TODO calculate margin from screw size
            screen_w_bevel_size[0] + 2.8,
            screen_w_bevel_size[1] + 24  # space for screws
        )

        screen_w_ramp_width = screen_viewing_area_size[0] + ramp_width_l_plus_r

        ratioed_screen_width = screen_viewing_area_size[0] / ratio_bevel_lr_to_bt
        ratioed_screen_w_ramp_width = screen_w_ramp_width / ratio_bevel_lr_to_bt

        alpha = required_taper_for_x(ratioed_screen_width, ratioed_screen_w_ramp_width, ramp_slope_thickness)

        screen_w_ramp_length = tapered_dimensions(ratioed_screen_width, screen_viewing_area_size[1], ramp_slope_thickness, alpha)

        # otherwise, the tapered extrusion won't actually be `ramp_slope_thickness`
        tapered_thickness = ramp_slope_thickness / math.cos(math.radians(alpha))

        screen_w_ramps_hole = (
            cq.Workplane("front")
                .rect(ratioed_screen_w_ramp_width, screen_w_ramp_length)
                .extrude(tapered_thickness, taper=alpha)
        )

        screen_w_ramps_hole = scale(screen_w_ramps_hole, ratio_bevel_lr_to_bt, 1, 1)
        screen_w_ramps_hole = (
            screen_w_ramps_hole
                .mirror("XY")
                .translate([*viewing_area_offset, part_thickness])
        )

        viewing_area_hole = (
            cq.Workplane("front")
                .box(*screen_viewing_area_size, part_thickness, centered=(True, True, False))
                .translate([*viewing_area_offset, 0])
        )

        screen_panel = (
            cq.Workplane("front")
                .box(*screen_board_size, part_thickness, centered=(True, True, False))
                .cut(screen_w_ramps_hole)
                .cut(viewing_area_hole)
                .translate([0, 0, -(part_thickness - enclosure_wall_thickness)])
        )
        screen_w_ramps_hole = screen_w_ramps_hole.translate([0, 0, -(part_thickness - enclosure_wall_thickness)])

        screws, screws_mask = self.build_screws_assembly(screw_block_thickness, enclosure_wall_thickness, part_thickness, (screen_w_ramp_width, screen_w_ramp_length))
        screen_panel = screen_panel.cut(screws_mask)

        mask = (
            cq.Workplane("front")
                .box(*screen_board_size, enclosure_wall_thickness, centered=(True, True, False))
        )

        mirror_and_translate = lambda obj: obj.mirror("XY").translate([0, 0, enclosure_wall_thickness])

        screen_panel, mask, screws_mask, screen_w_ramps_hole = list(map(mirror_and_translate,
                [screen_panel, mask, screws_mask, screen_w_ramps_hole]))

        screws = list(map(mirror_and_translate, screws))

        assembly_parts = [AssemblyPart(screen_panel, "Screen", cq.Color(*Part.DEFAULT_COLOR))]
        for idx, screw in enumerate(screws):
            assembly_parts.append(AssemblyPart(screw, f"Screw {idx}", cq.Color(0.7, 0.3, 0.8)))

        debug_screen_block = (  # screw blocks shouldn't collide with that
            cq.Workplane("front")
                .box(*screen_w_bevel_size, part_thickness, centered=(True, True, False))
        )

        if center_is_outward_facing_hole:
            print("TODO Need to move all workplanes so the hole's center is at 0,0")

        self.assembly_parts = assembly_parts
        self.part = self.assembly_parts_to_cq_assembly().toCompound()
        self.mask = mask

        self.size.width     = screen_board_size[0]
        self.size.length    = screen_board_size[1]
        self.size.thickness = part_thickness

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_offset = (0, 0)
        self.outside_footprint = (screen_w_ramp_width, screen_w_ramp_length)
        footprint_in = (
            cq.Workplane("front")
                .rect(self.size.width, self.size.length)
                .extrude(10)
                .translate([0, 0, enclosure_wall_thickness])
        )
        outside_footprint_thickness = 3
        footprint_out = (
            cq.Workplane("front")
                .rect(screen_w_ramp_width, screen_w_ramp_length)
                .extrude(outside_footprint_thickness)
                .translate([*viewing_area_offset, -outside_footprint_thickness])
        )
        self.debug_objects.footprint.inside  =  footprint_in
        self.debug_objects.footprint.outside = footprint_out

        self.debug_objects.hole = viewing_area_hole
        self.debug_objects.others["screen_block"] = debug_screen_block
        self.debug_objects.others["screws_mask"] = screws_mask
        self.debug_objects.others["screen_with_ramps_hole"] = screen_w_ramps_hole

    def build_screws_assembly(self, screw_thickness, enclosure_wall_thickness, screen_ramp_thickness, screen_w_ramp_size):
        screw_block_thickness = screen_ramp_thickness - enclosure_wall_thickness + screw_thickness
        m4 = DefaultScrewBlock.m4(screw_block_thickness)

        distance_between_screws_x = 108.3  #-0.8
        distance_between_screws_y = 84  #-0.6
        screws_pos = [
            (  -((distance_between_screws_x/2)+(4.1/2)),  +((distance_between_screws_y/2)+(4.1/2))  ),  # TL
            (  +((distance_between_screws_x/2)+(4.1/2)),  +((distance_between_screws_y/2)+(4.1/2))  ),  # TR
            (  -((distance_between_screws_x/2)+(4.1/2)),  -((distance_between_screws_y/2)+(4.1/2))  ),  # BL
            (  +((distance_between_screws_x/2)+(4.1/2)),  -((distance_between_screws_y/2)+(4.1/2))  ),  # BR
        ]

        screws = []
        screws_mask = cq.Workplane("front")

        for screw_pos in screws_pos:
            m4_block = m4["block"].translate([*screw_pos, 0]).mirror("XY")
            m4_mask = m4["mask"].translate([*screw_pos, 0]).mirror("XY")
            screws_mask = screws_mask.add(m4_mask)
            screws.append(m4_block)

        return (screws, screws_mask)