
"""
   Copyright 2025 Raphaël Isvelin

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

import os
import math
from typing import Tuple

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


PART_CATEGORY = "screen"
PART_ID = "DSI_5inch_800x480_Waveshare"

"""
Waveshare DSI 5" touchscreen, 800x480

TODO description

TODO waveshare link
"""
@register_part(PART_CATEGORY, PART_ID)
class Dsi5Inch800x480WavesharePart(Part):
    """ TODO cleanup this absolute mess of a class """

    BOARD_SIZE_XY = (180, 180)

    RAMP_SLOPE_THICKNESS = 2

    # STEP model
    STEP_FILE = "step/waveshare-5inch-dsi-800x480.stp"
    SIMPLIFIED_STEP_FILE = None
    ULTRA_SIMPLIFIED_STEP_FILE = None

    MODEL_OFFSET = [0, 3.12, 5.4 + RAMP_SLOPE_THICKNESS]
    # MODEL_OFFSET = [5, -3.12, 5.4]
    MODEL_ROTATION = [ ((0, 0, 0), (1, 0, 0), 180),    ((0, 0, 0), (0, 0, 1), 180) ]


    DISTANCE_BETWEEN_SCREWS_X = 110.8 - 1.0
    DISTANCE_BETWEEN_OUTER_SCREWS_Y = 67.6 + 24
    DISTANCE_BETWEEN_INNER_SCREWS_Y = 67.6

    # TODO check dimensions with my screen
    DEFAULT_PI_OFFSET = (
        -(DISTANCE_BETWEEN_SCREWS_X/2) + 15,
        -(DISTANCE_BETWEEN_INNER_SCREWS_Y/2) + 2.43,
    )

    def __init__(
        self,
        enclosure_wall_thickness: float,
        bracket_extra_thickness: float = 1.4,  # brackets are pressing the screen in place
        ramp_width_l_plus_r: float = 2.8,      # X/2mm on the left + X/2mm on the right, careful with slopes >35 degrees
        ratio_bevel_lr_to_bt: float = 1.5,     # N times less than ^ for top and bottom, careful with slopes >35 degrees
        add_model_to_footprint: bool = True,
        use_simplified_model: bool = False,
        use_ultra_simplified_model: bool = False,
    ):
        try: cls_file = __file__            # regular launch
        except NameError: cls_file = None   # when launched from Jupyter
        super().__init__(
            cls_file,
            PART_CATEGORY,
            PART_ID,
            Dsi5Inch800x480WavesharePart.STEP_FILE,
            Dsi5Inch800x480WavesharePart.SIMPLIFIED_STEP_FILE,
            Dsi5Inch800x480WavesharePart.ULTRA_SIMPLIFIED_STEP_FILE,
            Dsi5Inch800x480WavesharePart.MODEL_OFFSET,
            Dsi5Inch800x480WavesharePart.MODEL_ROTATION,
        )


        screen_module_thickness = 14.68 - 0.88
        screen_viewing_area_clearance = 0.4*2
        screen_viewing_area_size = (109 - screen_viewing_area_clearance, 65.8 - screen_viewing_area_clearance)
        screen_bevel_size = (3.1, 8.3, 5.85, 5.85)  # top, bottom, left, right
        viewing_area_offset = (0.0, 0)
        # viewing_area_offset = (0.4, -2.2)
        print("off s " + str(viewing_area_offset))

        screw_block_thickness = screen_module_thickness - enclosure_wall_thickness

        ramp_base_thickness = 1.6
        ramp_slope_thickness = Dsi5Inch800x480WavesharePart.RAMP_SLOPE_THICKNESS
        part_thickness = ramp_base_thickness + ramp_slope_thickness

        screw_block_thickness = screen_module_thickness - ramp_slope_thickness
        
        screen_w_bevel_size = (
            screen_viewing_area_size[0] + screen_bevel_size[2] + screen_bevel_size[3],
            screen_viewing_area_size[1] + screen_bevel_size[0] + screen_bevel_size[1]
        )
        screen_board_size = (
            screen_w_bevel_size[0] +  4, # magic number, TODO calculate margin from screw size
            screen_w_bevel_size[1] + 32  # space for screws TODO unhardcode for HDMI v. DSI
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
        self.debug_objects.others["viewing_area_hole"] = viewing_area_hole

        insert_thickness = 4.5
        insert_block_size = 8

        screen_panel = (
            cq.Workplane("front")
                .box(*screen_board_size, part_thickness, centered=(True, True, False))
                .cut(screen_w_ramps_hole)
                .cut(viewing_area_hole)
                .translate([0, 0, -(part_thickness - enclosure_wall_thickness)])

                .faces("<Z").workplane()
                .pushPoints([
                    # TODO cleanup, update base coords instead of hardcode
                    (  +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2)-31.8,   +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)-2+insert_block_size/2 ),  # TMl
                    (  +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2)-31.8,   -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)-2+insert_block_size/2 ),  # BMl
                    (  -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2)+20,     +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)-2+insert_block_size/2 ),  # TMr
                    (  -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2)+20,     -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)-2+insert_block_size/2 ),  # BMr
                ])
                .rect(insert_block_size, insert_block_size, centered=True)
                .extrude(2.5)

                .faces("<Z").workplane()
                .pushPoints([
                    # TODO cleanup, update base coords instead of hardcode
                    (  +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2)-31.8,   +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)-2+insert_block_size/2 ),  # TMl
                    (  +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2)-31.8,   -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)-2+insert_block_size/2 ),  # BMl
                    (  -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2)+20,     +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)-2+insert_block_size/2 ),  # TMr
                    (  -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2)+20,     -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)-2+insert_block_size/2 ),  # BMr
                ])
                .hole(4, insert_thickness)
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

        mirror_and_translate = lambda obj: obj.mirror("XY").translate([0, 0, part_thickness])
        screws = list(map(mirror_and_translate, screws))

        debug_screen_block = (  # screw blocks shouldn't collide with that
            cq.Workplane("front")
                .box(*screen_w_bevel_size, part_thickness, centered=(True, True, False))
        )

        bracket, bracket_alt, bracket_split, bracket_footprint, bracket_size = self.build_brackets(enclosure_wall_thickness, bracket_extra_thickness, viewing_area_offset)

        self.size.width     = screen_board_size[0]
        self.size.length    = screen_board_size[1]
        self.size.thickness = part_thickness

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = part_thickness + screw_block_thickness - enclosure_wall_thickness
        self.inside_footprint_offset = (-viewing_area_offset[0], -viewing_area_offset[1])

        self.outside_footprint = (screen_w_ramp_width, screen_w_ramp_length)
        self.outside_footprint_thickness = 3

        footprint_in = (
            cq.Workplane("front")
        )
        footprint_out = (
            cq.Workplane("front")
                .rect(*self.outside_footprint)
                .extrude(self.outside_footprint_thickness)
                .translate([*viewing_area_offset, -self.outside_footprint_thickness])
        )


        assembly_parts = [AssemblyPart(screen_panel, "Screen", cq.Color(*DEFAULT_PART_COLOR))]
        for idx, screw in enumerate(screws):
            assembly_parts.append(AssemblyPart(screw, f"Screw {idx}", cq.Color(0.7, 0.3, 0.8)))

            

        footprint_in.add(footprint_in
            .add(bracket_footprint.rotate((0, 0, 0), (0, 1, 0), 180).translate([56.5, 0, 16.6 + 2]))
            .add(bracket_footprint.rotate((0, 0, 0), (0, 1, 0), 180).translate([-56.5, 0, 16.6 + 2]))
            .add(bracket_alt.rotate((0, 0, 0), (0, 1, 0), 180).translate([+(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2)-31.8, 0, 16.6 + 2]))
            .add(bracket_alt.rotate((0, 0, 0), (0, 1, 0), 180).translate([-(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2)+20, 0, 16.6 + 2]))
        )

        # Inside footprint
        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = 20
        self.inside_footprint_offset = (0, -2.6-0.52)#-(2.6-1.504))

        # footprint_in = cq.Workplane("front")
        if add_model_to_footprint:
            footprint_in.add(super().get_step_model(
                use_simplified_model,
                use_ultra_simplified_model,
                [*self.inside_footprint_offset, 0]
            ))
        else:
            footprint_in.add(
                cq.Workplane("front")
                    .box(*self.inside_footprint, self.inside_footprint_thickness, centered=(True, True, False))
                    .translate([0, 0, enclosure_wall_thickness])
            )

        self.debug_objects.footprint.inside  = footprint_in

        # Outside footprint
        self.outside_footprint = (self.size.width, self.size.length)
        self.outside_footprint_thickness = 0
        self.outside_footprint_offset = (0, 0)

                             
        self.additional_printables = [
            ("screen-bracket-1", bracket_size, bracket),
            ("screen-bracket-2", bracket_size, bracket),
            ("screen-bracket-3", bracket_size, bracket_alt),
            ("screen-bracket-4", bracket_size, bracket_alt),
        ]

                             
        self.debug_objects.footprint.outside = None

        self.assembly_parts = assembly_parts
        self.part = self.assembly_parts_to_cq_assembly().toCompound()
        self.mask = mask

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out

        self.debug_objects.hole = None #viewing_area_hole

    def build_screws_assembly(self, screw_thickness, enclosure_wall_thickness, screen_ramp_thickness, screen_w_ramp_size):
        screw_block_thickness = screen_ramp_thickness - enclosure_wall_thickness + screw_thickness
        m4 = ScrewBlock().m3(screw_block_thickness, enclosure_wall_thickness)

        screws_pos = [
            # TODO cleanup, update base coords instead of hardcode
            (  -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2) - 1.6,  +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2) - 2 ),  # TL
            (  -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2) - 1.6,  -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2) - 2 ),  # BL
            (  +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2) + 1.6,  +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2) - 2 ),  # TR
            (  +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_SCREWS_X/2) + 1.6,  -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2) - 2 ),  # BR
        ]

        screws = []
        screws_mask = cq.Workplane("front")

        for screw_pos in screws_pos:
            m4_block = m4["block"].translate([*screw_pos, 0]).mirror("XY")
            m4_mask = m4["mask"].translate([*screw_pos, 0]).mirror("XY")
            screws_mask = screws_mask.add(m4_mask)
            screws.append(m4_block)

        return (screws, screws_mask)

    def build_brackets(
        self,
        enclosure_wall_thickness: float,
        bracket_extra_thickness: float,
        viewing_area_offset: float
    ):
        # TODO cleanup this mess
        outer_screws_pos = [
            (0, -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)-2),
            (0, +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_OUTER_SCREWS_Y/2)-2),
        ]
        inner_pi_screws_pos = [
            (0, -26.38),
            (0, 22.65),
        ]
        inner_screws_pos = [
            (0, -(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_INNER_SCREWS_Y/2)-2),
            (0, +(Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_INNER_SCREWS_Y/2)-2),
        ]
        bracket_size = (10, 110)

        bracket_thickness = 4
        bracket = (
            cq.Workplane("front")
                .rect(*bracket_size)
                .extrude(bracket_thickness)
                .faces(">Z").workplane()
                .pushPoints(outer_screws_pos)
                .hole(4.3)
                .pushPoints(inner_screws_pos)
                .hole(3)
        )
        bracket_alt = (
            cq.Workplane("front")
                .rect(*bracket_size)
                .extrude(bracket_thickness)
                .faces(">Z").workplane()
                .pushPoints(outer_screws_pos)
                .hole(4.3)
                .pushPoints(inner_pi_screws_pos)
                .hole(2.7)
        )

        bracket_split = bracket.cut(
            cq.Workplane("front")
                .rect(10, Dsi5Inch800x480WavesharePart.DISTANCE_BETWEEN_INNER_SCREWS_Y - 12)
                .extrude(enclosure_wall_thickness + bracket_extra_thickness)
        )

        bracket_footprint = bracket.translate([0,0,0])  # copied pre-transofmration, as we don't want to rotate/translate it--legacy

        # Makes them nicer to display in Enclosure#all_printables_assembly (aligned with the)
        bracket = bracket.rotate((0, 0, 0), (0, 0, 1), 90)
        bracket_split = bracket_split.rotate((0, 0, 0), (0, 0, 1), 90)
        bracket_size = (bracket_size[1], bracket_size[0])

        # Center to 0,0
        bracket = bracket.translate([*viewing_area_offset, 0])
        bracket_split = bracket_split.translate([*viewing_area_offset, 0])

        return (bracket, bracket_alt, bracket_split, bracket_footprint, bracket_size)