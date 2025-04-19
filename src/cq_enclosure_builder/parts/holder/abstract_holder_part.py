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


USE_DEFAULT_SCREW_BLOCK_PROVIDER = None  # alias for readability


"""
Holder base class allowing easy addition of Screw Blocks and Support
"""
class AbstractHolderPart(Part):
    
    def __init__(
        self,
        enclosure_wall_thickness: float,
        block_thickness: float,
        # Part fields - TODO move before ewt/sbt once they're mandatory
        cls_file,
        part_category,
        part_id,
        step_file,
        simplified_step_file,
        ultra_simplified_step_file,
        model_offset,
        model_rotation = None,
        model_mirror = None,
    ):
        self.enclosure_wall_thickness = enclosure_wall_thickness
        self.block_thickness = block_thickness
        super().__init__(
            cls_file,
            part_category,
            part_id,
            step_file,
            simplified_step_file,
            ultra_simplified_step_file,
            model_offset,
            model_rotation,
            model_mirror,
        )
        self.screws_specs = []
        self.screws_pos_offset = [0, 0, 0]
        self.default_screw_block_id = "block"
        self.default_screw_block_provider = lambda this: ScrewBlock().m3(this.block_thickness, this.enclosure_wall_thickness)[this.default_screw_block_id]
        self.support_blocks_specs = []
        self.support_blocks_pos_offset = [0, 0, 0]


    # Base board and mask with screws and supports, centered on 0,0
    def build_base_board_and_mask(self, board_size):
        screw_blocks_a = self.get_screw_blocks()
        supports_a = self.get_support_blocks()

        part = (
            cq.Workplane("front")
                .box(*board_size, centered=(True, True, False))

                .add(screw_blocks_a.toCompound())
                .add(supports_a.toCompound())
        )
        mask = (
            cq.Workplane("front")
                .box(*board_size, centered=(True, True, False))
        )

        return (part, mask)


    def build_and_set_default_board_and_mask(self, board_size_xy):
        board_size = (*board_size_xy, self.enclosure_wall_thickness)

        self.size.width, self.size.length, self.size.thickness = board_size

        self.part, self.mask = self.build_base_board_and_mask(board_size)


    def build_and_set_default_footprints(
        self,
        pcb_thickness: float,
        add_model_to_footprint = True,
        use_simplified_model = False,
        use_ultra_simplified_model = False,
    ):
        # Inside footprint
        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = pcb_thickness + self.block_thickness
        self.inside_footprint_offset = (0, 0)

        footprint_in = cq.Workplane("front")
        if add_model_to_footprint:
            footprint_in = super().get_step_model(
                use_simplified_model,
                use_ultra_simplified_model,
                [0, self.inside_footprint[1], self.block_thickness + self.enclosure_wall_thickness]
            )
        else:
            footprint_in = (
                cq.Workplane("front")
                    .box(*self.inside_footprint, self.inside_footprint_thickness - self.block_thickness, centered=(True, True, False))
                    .translate([0, 0, self.block_thickness + self.enclosure_wall_thickness])
            )

        self.debug_objects.footprint.inside  = footprint_in

        # Outside footprint
        self.outside_footprint = (self.size.width, self.size.length)
        self.outside_footprint_thickness = 0
        self.outside_footprint_offset = (0, 0)

        self.debug_objects.footprint.outside = None


    def get_screw_blocks(self):
        default_screw_block = None  # lazy loaded
        screw_block = None

        screw_blocks_a = cq.Assembly()
        for screw_specs in self.screws_specs:
            pos, provider = screw_specs

            if provider is None:
                if default_screw_block is None:
                    default_screw_block = self.default_screw_block_provider(self)
                screw_block = default_screw_block
            else:
                screw_block = provider(self)

            screw_blocks_a.add(
                screw_block
                    .translate([*pos, self.enclosure_wall_thickness])
                    .translate(self.screws_pos_offset)
            )

        return screw_blocks_a


    def get_support_blocks(self):
        supports_a = cq.Assembly()
        for specs in self.support_blocks_specs:
            pos, size = specs

            supports_a.add(
                cq.Workplane("front")
                    .box(*size, self.block_thickness, centered=(True, True, False))
                    .translate([*pos, self.enclosure_wall_thickness])
                    .translate(self.support_blocks_pos_offset)
            )

        return supports_a


    def set_screws_specs(
        self,
        specs,          # e.g. [  ( [PX, PY],  <provider lambda, None=default> ),  ...  ]
        offset=[0,0,0]  # e.g. [PX, PY], if the pos above are not centered on 0,0
    ):
        self.screws_specs = specs
        self.screws_pos_offset = offset


    def set_default_screw_block_provider(self, provider):
        self.default_screw_block_provider = provider


    # for default screw block provider, False by default
    def set_default_countersunk(self, is_countersunk: bool = True):
        self.default_screw_block_id = "counter_sunk_block" if is_countersunk else "block"


    def set_support_blocks_specs(
        self,
        specs,          # e.g. [  ( [PX,PY], (SX,SY) ),  ...  ]
        offset=[0,0,0]  # e.g. [PX, PY], if the pos above are not centered on 0,0
    ):
        self.support_blocks_specs = specs
        self.support_blocks_pos_offset = offset
