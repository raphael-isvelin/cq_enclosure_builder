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
from cq_enclosure_builder.parts.common.screw_block import ScrewBlock
from cq_enclosure_builder.parts_factory import register_part
from cq_enclosure_builder.parts.common.screws_providers import TinyBlockFlatHeadScrewProvider

HOLE_DISTANCE = 2.54

@register_part("holder", "Protoboard")
class ProtoboardHolderPart(Part):
    """
    4-screw holder for 2.54mm (0.1 inch) protoboards
    """
    def __init__(
        self,
        enclosure_wall_thickness,
        screw_block_thickness = 4,
        holes_count_x = 10,
        holes_count_y = 8,
        screws_pos = None,  # default: one per corner
        screw_provider = TinyBlockFlatHeadScrewProvider,  # use regular screw blocks for parts with stress
        hole_distance = HOLE_DISTANCE,
    ):
        super().__init__()

        base_board_size = (holes_count_x * hole_distance, holes_count_y * hole_distance)

        if screws_pos is None:
            screws_pos = [
                (0, 0),
                (holes_count_x-1, 0),
                (0, holes_count_y-1),
                (holes_count_x-1, holes_count_y-1)
            ]

        screw_part: Part = ScrewBlock(screw_provider=screw_provider).m2_5(screw_block_thickness, enclosure_wall_thickness)
        screw = screw_part["block"].translate([0, 0, enclosure_wall_thickness])
        screw_size = screw_part["size"]

        screws_a = cq.Assembly()
        min_pos = [9999, 9999]
        max_pos = [-9999, -9999]
        for screw_pos in screws_pos:
            pos_x = screw_pos[0]*hole_distance + hole_distance/2 - base_board_size[0]/2
            pos_y = screw_pos[1]*hole_distance + hole_distance/2 - base_board_size[1]/2

            if pos_x - screw_size[0]/2 < min_pos[0]: min_pos[0] = pos_x - screw_size[0]/2
            elif pos_x + screw_size[0]/2 > max_pos[0]: max_pos[0] = pos_x + screw_size[0]/2
            if pos_y - screw_size[1]/2 < min_pos[1]: min_pos[1] = pos_y - screw_size[1]/2
            elif pos_y + screw_size[1]/2 > max_pos[1]: max_pos[1] = pos_y + screw_size[1]/2

            screws_a.add(screw.translate([pos_x, pos_y, 0]))

        self.size.width     = max(base_board_size[0], abs(min_pos[0]) + abs(max_pos[0]))
        self.size.length    = max(base_board_size[1], abs(min_pos[1]) + abs(max_pos[1]))
        self.size.thickness = enclosure_wall_thickness

        board = (
            cq.Workplane("front")
                .box(self.size.width, self.size.length, self.size.thickness, centered=(True, True, False))
                .add(screws_a.toCompound())
        )
        mask = board

        self.part = board
        self.mask = mask

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_offset = (0, 0)
        footprint_in = (
            cq.Workplane("front")
                .rect(self.inside_footprint[0], self.inside_footprint[1])
                .extrude(screw_block_thickness)
                .translate([0, 0, enclosure_wall_thickness])
                .add(screws_a.toCompound())
        )

        self.outside_footprint = (self.size.width, self.size.length)

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = None