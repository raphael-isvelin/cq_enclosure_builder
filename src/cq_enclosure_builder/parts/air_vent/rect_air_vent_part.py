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

from typing import Union

import cadquery as cq

from cq_enclosure_builder.part import Part
from cq_enclosure_builder.parts_factory import register_part
from cq_enclosure_builder.parts.common.screw_block import ScrewBlock, TaperOptions
from cq_enclosure_builder.parts.common.screws_providers import TinyBlockFlatHeadScrewProvider
from cq_enclosure_builder.parts.air_vent.fan_size import FanSize


@register_part("air_vent", "basic rectangular")
class RectAirVentPart(Part):
    """
    Class to make basic rectangular vents, with optional screws for fan.

    Needs refactoring.
    Hasn't been tested much besides the default parameters.
    """

    def __init__(
        self,
        enclosure_wall_thickness: float,
        width: float = 30,
        length: float = 25,
        thickness: float = 6,
        margin: float = 0.5,
        hole_angle: float = 25,
        hole_width: float = 1.6,
        distance_between_holes: float = 4,
        taper: bool = True,
        taper_margin: float = 3,
        taper_angle: float = 35,
        with_fan_screws: Union[FanSize, None] = FanSize._30_MM,
        fan_screws_size: str = "m3",
        fan_screws_taper_mode: TaperOptions = TaperOptions.XY_TAPER,
        fan_screws_taper_rotation: float = 0,
        fan_screws_taper_incline: float = 0.75,
        fan_screws_taper_on: str = "1100"  # TODO cleanup one day; sorry future self, just want to be done with it :shrug:
    ):
        super().__init__()

        # Board
        board = (
            cq.Workplane("front")
                .box(width, length, thickness, centered=(True, True, False))
        )

        # Add holes
        single_hole = (
            cq.Workplane("front")
                .box(hole_width, length, thickness*6, centered=(True, True, False))
                .translate([0, 0, -(thickness*3)])
                .rotate((0, 0, 0), (0, 1, 0), hole_angle)
        )

        all_holes = cq.Assembly()
        hole_x = 0
        while hole_x < width/2:
            all_holes.add(single_hole.translate([hole_x, 0, 0]))
            all_holes.add(single_hole.translate([-hole_x, 0, 0]))
            hole_x = hole_x + distance_between_holes

        board = board.cut(all_holes.toCompound())

        # Add frame
        board = (
            cq.Workplane("front")
                .box(width + margin*2, length + margin*2, thickness - enclosure_wall_thickness, centered=(True, True, False))
                .translate([0, 0, enclosure_wall_thickness])
                .cut(cq.Workplane("front").box(width, length, thickness, centered=(True, True, False)))
                .add(board)
        )

        self.size.width     = width + margin*2 + taper_margin*2
        self.size.length    = length + margin*2 + taper_margin*2
        self.size.thickness = thickness

        self.inside_footprint = (self.size.width, self.size.length)  # TODO should account for the screw blocks (incl. taper)
        self.inside_footprint_thickness = thickness - enclosure_wall_thickness
        self.inside_footprint_offset = (0, 0)

        self.outside_footprint = (self.size.width, self.size.length)
        self.outside_footprint_thickness = 2

        footprint_in = (
            cq.Workplane("front")
                .rect(width, length)
                .extrude(self.inside_footprint_thickness)
                .translate([0, 0, enclosure_wall_thickness])
        )

        # Pyramid
        if taper:
            pyramid = (
                cq.Workplane("front")
                    .rect(width + margin*2 + taper_margin*2, length + margin*2 + taper_margin*2)
                    .extrude(30, taper=taper_angle)
                    .cut(cq.Workplane("front").rect(width + 4, length + 4).extrude(40).translate([0, 0, thickness - enclosure_wall_thickness]))
                    .cut(cq.Workplane("front").rect(width, length).extrude(thickness - enclosure_wall_thickness).translate([0, 0, 0]))
                    .translate([0, 0, enclosure_wall_thickness])
            )
            board = board.add(pyramid)

        # Mask & footprint
        mask = (
            cq.Workplane("front")
                .box(width, length, enclosure_wall_thickness, centered=(True, True, False))
        )

        # Fan screws
        if with_fan_screws is not None:
            fan_screws_a = RectAirVentPart._get_fan_screws_blocks(
                enclosure_wall_thickness,
                with_fan_screws,
                block_thickness=thickness,  # - enclosure_wall_thickness,
                screw_size=fan_screws_size,
                screw_block_taper_option=fan_screws_taper_mode,
                screw_block_taper_rotation=fan_screws_taper_rotation,
                screw_block_taper_incline=fan_screws_taper_incline,
                screw_block_taper_on=fan_screws_taper_on
            )
            fan_screws = fan_screws_a["screws"]  #.translate([0, 0, enclosure_wall_thickness])
            fan_masks = fan_screws_a["masks"]  #.translate([0, 0, enclosure_wall_thickness])
            footprint_in = footprint_in.add(fan_screws_a["footprint_in"])
            fan_footprint = fan_screws_a["footprint_size"]
            self.inside_footprint = (
                self.inside_footprint[0] if self.inside_footprint[0] > fan_footprint[0] else fan_footprint[0],
                self.inside_footprint[1] if self.inside_footprint[1] > fan_footprint[1] else fan_footprint[1],
            )
            self.inside_footprint_thickness = self.inside_footprint_thickness + fan_screws_a["footprint_thickness"]

            board = board.cut(fan_masks).add(fan_screws)
            mask = mask.add(fan_masks)

        self.part = board
        self.mask = mask

        footprint_in = footprint_in.add(board).cut(
            cq.Workplane("front")
                .box(*self.inside_footprint, enclosure_wall_thickness, centered=(True, True, False))
        )
        footprint_out = (
            cq.Workplane("front")
                .rect(*self.outside_footprint)
                .extrude(self.outside_footprint_thickness)
                .translate([-0, 0, -self.outside_footprint_thickness])
        )
        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out
        
        self.debug_objects.hole = None

    @staticmethod
    def _get_fan_screws_blocks(
        enclosure_wall_thickness,
        fan_size: FanSize,
        block_thickness: float,
        screw_size: str = "m2",
        screw_block_taper_option: TaperOptions = TaperOptions.XY_TAPER,
        screw_block_taper_rotation: float = 0,
        screw_block_taper_incline: float = 0.75,
        screw_block_taper_on: str = "1111",  # should taper that specific screw block? same order as screws_pos
        screw_block_hole_distance_to_wall: float = 0.8
    ):
        screw = ScrewBlock(screw_provider=TinyBlockFlatHeadScrewProvider).build(
            screw_size, block_thickness, enclosure_wall_thickness, screw_hole_depth=block_thickness-screw_block_hole_distance_to_wall, fill_pointy_bit=True,
            taper=screw_block_taper_option, taper_rotation=screw_block_taper_rotation, xy_taper_incline=screw_block_taper_incline, xy_taper_from=enclosure_wall_thickness)
        screw_no_taper = ScrewBlock(screw_provider=TinyBlockFlatHeadScrewProvider).build(
            screw_size, block_thickness, enclosure_wall_thickness, screw_hole_depth=block_thickness-screw_block_hole_distance_to_wall, fill_pointy_bit=True)

        distance_between_screws = None  # center to center
        footprint_size = None
        footprint_thickness = None
        # TODO Refactor when needed
        if fan_size == FanSize._25_MM:
            distance_between_screws = 16.9 + 2.9
            footprint_size = 25
            footprint_thickness = 7
        elif fan_size == FanSize._30_MM:
            distance_between_screws = 20.8 + 3.2
            footprint_size = 30
            footprint_thickness = 8
        elif fan_size == FanSize._40_MM:
            distance_between_screws = 28.9 + 3.2
            footprint_size = 40
            footprint_thickness = 10.8
        else:
            raise ValueError("Unknown FanSize")

        if screw_block_taper_option == TaperOptions.XY_TAPER:
            # TODO UNHARDCODE (based on block_thickness and taper_include)
            # hacky way to include the screw block taper in the inside_footprint
            taper_ramp_size = block_thickness / 2
            footprint_size = footprint_size + taper_ramp_size*2
        # TODO might need to do something for Z_TAPERs as well

        hdbs = distance_between_screws/2

        screws_pos = [
            (-hdbs,  hdbs),  # TR
            ( hdbs,  hdbs),  # TL
            ( hdbs, -hdbs),  # BL
            (-hdbs, -hdbs),  # BR
        ]

        screws = cq.Assembly()
        masks = cq.Assembly()
        for idx, sp in enumerate(screws_pos):
            current_screw = screw if screw_block_taper_on[idx] == "1" else screw_no_taper  # see apologies in constructor :D
            screws.add(current_screw["block"].translate([*sp, 0]))
            masks.add(current_screw["mask"].translate([*sp, 0]))

        footprint_in = (
            cq.Workplane("front")
                .rect(footprint_size, footprint_size)
                .extrude(footprint_thickness)
                .translate([0, 0, block_thickness])
        )

        return {
            "screws": screws.toCompound(),
            "masks": masks.toCompound(),
            "footprint_in": footprint_in,
            "footprint_size": (footprint_size, footprint_size),
            "footprint_thickness": footprint_thickness,
            #"base_plate": base_plate.translate([0, 0, -enclosure_wall_thickness])
        }