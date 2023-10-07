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

import math

import cadquery as cq
from cq_enclosure_builder.constants import DEFAULT_PART_COLOR
from cq_enclosure_builder.part import Part, AssemblyPart
from cq_enclosure_builder.parts_factory import register_part
from cq_enclosure_builder.parts.common.screw_block import ScrewBlock
from cq_enclosure_builder.utils.workplane_utils import scale

def required_taper_for_x(x, x_resulting, h):
    delta_x = (x_resulting - x) / 2
    alpha_x = math.degrees(math.atan(delta_x / h))
    return alpha_x

def tapered_dimensions(x, y, h, alpha):
    alpha_rad = math.radians(alpha)
    delta_y = h * math.tan(alpha_rad)
    return y + 2 * delta_y

@register_part("screen", "DSI 5 inch XXX")
class Dsi5InchXxxPart(Part):
    """
    DSI 5 inch screen XXX

    Screen doesn't have screw holes sticking out of the PCB, so we're also printing some strips to press it in place.
    screw_block_thickness should the same height as the screw on the PCB, or can be made taller, if strip_extra_thickness
    is set to the difference; in which case, the strip won't be flat, but have a part sticking out, to press on the screen [screws].

    TODO link
    """

    DISTANCE_BETWEEN_SCREWS_X = 110.8 - 1.0
    DISTANCE_BETWEEN_OUTER_SCREWS_Y = 67.6 + 24
    DISTANCE_BETWEEN_INNER_SCREWS_Y = 67.6

    def __init__(
        self,
        enclosure_wall_thickness: float,
        screw_block_thickness: float = 11.6 + 1.4,
        strip_extra_thickness: float = 1.4,  # strips are pressing the screen in place
        center_is_outward_facing_hole: bool = True,
        ramp_width_l_plus_r = 2.8,   # X/2mm on the left + X/2mm on the right, careful with slopes >35 degrees
        ratio_bevel_lr_to_bt = 1.5,  # N times less than ^ for top and bottom, careful with slopes >35 degrees
    ):
        # TODO refactor, it's copy/pasted from HDMI will little modifications:
        # - default screw_block_thickness
        # - DISTANCE_BETWEEN_SCREWS_X/y
        # - additional prints

        super().__init__()

        screen_viewing_area_size = (108.8-0.8, 65.6-0.8)
        screen_bevel_size = (3.2, 7.6, 6.4, 6.4)  # top, bottom, left, right

        viewing_area_offset = (0.4, -2.2)

        ramp_base_thickness = 1.6
        ramp_slope_thickness = 2
        part_thickness = ramp_base_thickness + ramp_slope_thickness

        screen_w_bevel_size = (
            screen_viewing_area_size[0] + screen_bevel_size[2] + screen_bevel_size[3],
            screen_viewing_area_size[1] + screen_bevel_size[0] + screen_bevel_size[1]
        )
        screen_board_size = (
            screen_w_bevel_size[0] +  4, # magic number, TODO calculate margin from screw size
            screen_w_bevel_size[1] + 28  # space for screws TODO unhardcode for HDMI v. DSI
        )

        screen_w_ramp_width = screen_viewing_area_size[0] + ramp_width_l_plus_r

        ratioed_screen_width = screen_viewing_area_size[0] / ratio_bevel_lr_to_bt
        ratioed_screen_w_ramp_width = screen_w_ramp_width / ratio_bevel_lr_to_bt

        alpha = required_taper_for_x(ratioed_screen_width, ratioed_screen_w_ramp_width, ramp_slope_thickness)

        screen_w_ramp_length = tapered_dimensions(ratioed_screen_width, screen_viewing_area_size[1], ramp_slope_thickness, alpha)
        #print(f"TAPER ANGLE: {str(alpha)} for ramp {str(ramp_width_l_plus_r)} ratio {str(ratio_bevel_lr_to_bt)}")

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

        debug_screen_block = (  # screw blocks shouldn't collide with that
            cq.Workplane("front")
                .box(*screen_w_bevel_size, part_thickness, centered=(True, True, False))
        )

        strip, strip_split = self.build_strips(enclosure_wall_thickness, strip_extra_thickness)

        self.size.width     = screen_board_size[0]
        self.size.length    = screen_board_size[1]
        self.size.thickness = part_thickness

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_offset = (0, 0)
        footprint_in = (
            cq.Workplane("front")
                .rect(*self.inside_footprint)
                .extrude(10)
                .translate([0, 0, enclosure_wall_thickness])
        )

        self.outside_footprint = (screen_w_ramp_width, screen_w_ramp_length)
        outside_footprint_thickness = 3
        footprint_out = (
            cq.Workplane("front")
                .rect(*self.outside_footprint)
                .extrude(outside_footprint_thickness)
                .translate([*viewing_area_offset, -outside_footprint_thickness])
        )

        if center_is_outward_facing_hole:
            translate_by_viewing_area_offset = lambda obj: obj.translate([-viewing_area_offset[0], -viewing_area_offset[1], 0])

            strip, strip_split, screen_panel, mask, footprint_in, footprint_out, viewing_area_hole, debug_screen_block, screws_mask, screen_w_ramps_hole = list(map(translate_by_viewing_area_offset,
                    [strip, strip_split, screen_panel, mask, footprint_in, footprint_out, viewing_area_hole, debug_screen_block, screws_mask, screen_w_ramps_hole]))

            screws = list(map(translate_by_viewing_area_offset, screws))

        assembly_parts = [AssemblyPart(screen_panel, "Screen", cq.Color(*DEFAULT_PART_COLOR))]
        for idx, screw in enumerate(screws):
            assembly_parts.append(AssemblyPart(screw, f"Screw {idx}", cq.Color(0.7, 0.3, 0.8)))

        footprint_in = (footprint_in
            .add(strip.rotate((0, 0, 0), (0, 1, 0), 180).translate([54.1, 0, 16.6 + 2]))
            .add(strip_split.rotate((0, 0, 0), (0, 1, 0), 180).translate([-55.7, 0, 16.6 + 2]))
        )

        self.assembly_parts = assembly_parts
        self.part = self.assembly_parts_to_cq_assembly().toCompound()
        self.mask = mask

        self.additional_printables = [
            ("screen-strip-1", strip),
            ("screen-strip-2", strip_split),
        ]

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out

        self.debug_objects.hole = None #viewing_area_hole
        self.debug_objects.others["screen_block"] = debug_screen_block
        self.debug_objects.others["screws_mask"] = screws_mask
        self.debug_objects.others["screen_with_ramps_hole"] = screen_w_ramps_hole

    def build_screws_assembly(self, screw_thickness, enclosure_wall_thickness, screen_ramp_thickness, screen_w_ramp_size):
        screw_block_thickness = screen_ramp_thickness - enclosure_wall_thickness + screw_thickness
        m4 = ScrewBlock().m4(screw_block_thickness, enclosure_wall_thickness)

        screws_pos = [
            (  -(Dsi5InchXxxPart.DISTANCE_BETWEEN_SCREWS_X/2),  +(Dsi5InchXxxPart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)  ),  # TL
            (  +(Dsi5InchXxxPart.DISTANCE_BETWEEN_SCREWS_X/2),  +(Dsi5InchXxxPart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)  ),  # TR
            (  -(Dsi5InchXxxPart.DISTANCE_BETWEEN_SCREWS_X/2),  -(Dsi5InchXxxPart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)  ),  # BL
            (  +(Dsi5InchXxxPart.DISTANCE_BETWEEN_SCREWS_X/2),  -(Dsi5InchXxxPart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)  ),  # BR
        ]

        screws = []
        screws_mask = cq.Workplane("front")

        for screw_pos in screws_pos:
            m4_block = m4["block"].translate([*screw_pos, 0]).mirror("XY")
            m4_mask = m4["mask"].translate([*screw_pos, 0]).mirror("XY")
            screws_mask = screws_mask.add(m4_mask)
            screws.append(m4_block)

        return (screws, screws_mask)

    def build_strips(self, enclosure_wall_thickness, strip_extra_thickness):
        outer_screws_pos = [
            (0, -(Dsi5InchXxxPart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)),
            (0, +(Dsi5InchXxxPart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)),
        ]
        inner_screws_pos = [
            (0, -(Dsi5InchXxxPart.DISTANCE_BETWEEN_INNER_SCREWS_Y/2)),
            (0, +(Dsi5InchXxxPart.DISTANCE_BETWEEN_INNER_SCREWS_Y/2)),
        ]

        strip = (
            cq.Workplane("front")
                .rect(10, 103.6)
                .extrude(enclosure_wall_thickness)
                .add(
                    cq.Workplane("front")
                        .rect(10, Dsi5InchXxxPart.DISTANCE_BETWEEN_INNER_SCREWS_Y + 10)
                        .extrude(enclosure_wall_thickness + strip_extra_thickness)
                )
                .faces(">Z").workplane()
                .pushPoints(outer_screws_pos)
                .hole(4.3)
                .pushPoints(inner_screws_pos)
                .hole(2.7)
        )

        strip_split = strip.cut(
            cq.Workplane("front")
                .rect(10, Dsi5InchXxxPart.DISTANCE_BETWEEN_INNER_SCREWS_Y - 12)
                .extrude(enclosure_wall_thickness + strip_extra_thickness)
        )

        return (strip, strip_split)