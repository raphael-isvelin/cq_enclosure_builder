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
import cadquery as cq

from cq_enclosure_builder.part import Part
from cq_enclosure_builder.parts.common.screw_block import ScrewBlock
from cq_enclosure_builder.parts_factory import register_part

# TODO use AbstractHolderPart
@register_part("holder", "RPi_4B")
class Pi4HolderPart(Part):
    """
    4-screw holder for Raspberry Pi 4B (should be compatible with other Pis, check screw distance)
    """
    def __init__(
        self,
        enclosure_wall_thickness,
        screw_block_thickness = 4,
        add_model_to_footprint = True,
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

        screws_a = cq.Assembly()
        for screw_pos in screws_pos:
            screws_a.add(screw.translate(screw_pos))

        board = (
            cq.Workplane("front")
                .box(board_width, board_length, enclosure_wall_thickness, centered=(True, True, False))
                .add(screws_a.toCompound())
        )
        mask = (
            cq.Workplane("front")
                .box(board_width, board_length, enclosure_wall_thickness, centered=(True, True, False))
        )

        self.part = board
        self.mask = mask

        self.size.width     = board_width
        self.size.length    = board_length
        self.size.thickness = enclosure_wall_thickness

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = screw_block_thickness
        self.inside_footprint_offset = (0, 0)

        self.outside_footprint = (self.size.width, self.size.length)
        self.outside_footprint_thickness = 0

        footprint_in = screws_a.toCompound()
        if add_model_to_footprint:
            step_dir = "../src/cq_enclosure_builder/parts/holder"
            try: step_dir = os.path.dirname(__file__)   # regular launch
            except NameError: pass                      # when launched from Jupyter

            model_path = os.path.join(step_dir, "step/rpi_4b_light.stp")
            model = cq.importers.importStep(model_path)
            pi_footprint = (
                model
                    .translate([-(board_width/2), -(board_length/2), enclosure_wall_thickness + screw_block_thickness])
                    .translate([screw_size[0]/2, screw_size[1]/2, 0])
            )
            footprint_in = pi_footprint.add(screws_a.toCompound())
            self.inside_footprint_thickness = screw_block_thickness + 20.1 - 1.8

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = None