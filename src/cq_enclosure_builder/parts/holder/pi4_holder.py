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

@register_part("holder", "RPi 4B")
class Pi4HolderPart(Part):
    """
    4-screw holder for Raspberry Pi 4B (should be compatible with other Pis, check screw distance)
    """
    def __init__(
        self,
        enclosure_wall_thickness,
        screw_block_thickness = 4
    ):
        super().__init__()

        distance_between_screws_x = 58
        distance_between_screws_y = 49
        half_dist_x = distance_between_screws_x/2
        half_dist_y = distance_between_screws_y/2

        screws_pos = [
            (half_dist_x, half_dist_y, 0),    # TR
            (-half_dist_x, half_dist_y, 0),   # TL
            (half_dist_x, -half_dist_y, 0),   # BR
            (-half_dist_x, -half_dist_y, 0),  # BL
        ]

        screw_part: Part = ScrewBlock().m2_5(screw_block_thickness, enclosure_wall_thickness)
        screw = screw_part["block"].translate([0, 0, enclosure_wall_thickness])
        screw_size = screw_part["size"]

        board_width = distance_between_screws_x + screw_size[0]
        board_length = distance_between_screws_y + screw_size[1]

        board = (
            cq.Workplane("front")
                .box(board_width, board_length, enclosure_wall_thickness, centered=(True, True, False))
        )
        mask = board
        for screw_pos in screws_pos:
            board = board.add(
                screw.translate(screw_pos)
            )

        self.part = board
        self.mask = mask

        self.size.width     = board_width
        self.size.length    = board_length
        self.size.thickness = enclosure_wall_thickness

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_offset = (0, 0)
        footprint_in = (
            cq.Workplane("front")
                .rect(self.size.width, self.size.length)
                .extrude(screw_block_thickness)
                .translate([0, 0, enclosure_wall_thickness])
        )

        self.outside_footprint = (self.size.width, self.size.length)

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = None