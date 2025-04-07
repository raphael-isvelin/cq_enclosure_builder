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
        # Part fields
        cls_file,
        part_category,
        part_id,
        step_file,
        simplified_step_file,
        ultra_simplified_step_file,
        model_offset,
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
            model_offset
        )
        self.screws_specs = []
        self.screws_pos_offset = [0, 0, 0]
        self.default_screw_block_id = "block"
        self.default_screw_block_provider = lambda this: ScrewBlock().m3(this.block_thickness, this.enclosure_wall_thickness)[this.default_screw_block_id]
        self.support_blocks_specs = []
        self.support_blocks_pos_offset = [0, 0, 0]


    # Base board and mask with screws and supports, centered on 0,0
    def get_base_board_and_mask(self, board_size):
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
