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

import cadquery as cq

from cq_enclosure_builder.parts.holder.abstract_holder_part import AbstractHolderPart, USE_DEFAULT_SCREW_BLOCK_PROVIDER
from cq_enclosure_builder.parts_factory import register_part

PART_CATEGORY = "holder"
PART_ID = "Octopus motherboard"

"""
Octopus motherboard
"""
@register_part(PART_CATEGORY, PART_ID)
class OctopusMotherboardHolderPart(AbstractHolderPart):

    BOARD_SIZE = (255, 166)

    STEP_FILE = None  # full version is too complex for cq
    SIMPLIFIED_STEP_FILE = "octopus_motherboard_simplified.step"
    ULTRA_SIMPLIFIED_STEP_FILE = "octopus_motherboard_footprint.step"  # TODO make the model a bit more 3D (general 'hitboxes')

    MODEL_OFFSET = [-BOARD_SIZE[0]/2, -BOARD_SIZE[1]/2, 0]
    PCB_THICKNESS = 32.417 - 5.167  # excluding everything under the PCB (pins)

    SCREWS_SPECS = [
        ( [ 41.6,   BOARD_SIZE[1] -  67.8],   USE_DEFAULT_SCREW_BLOCK_PROVIDER ),
        ( [  5,     BOARD_SIZE[1] - 161.2],   USE_DEFAULT_SCREW_BLOCK_PROVIDER ),
        ( [249.5,   BOARD_SIZE[1] - 160.9],   USE_DEFAULT_SCREW_BLOCK_PROVIDER ),
        ( [177.8,   BOARD_SIZE[1] -  71.3],   USE_DEFAULT_SCREW_BLOCK_PROVIDER ),
    ]
    SCREWS_POS_OFFSET = [-BOARD_SIZE[0]/2, -BOARD_SIZE[1]/2, 0]
    SUPPORT_BLOCKS_SPECS = [
        ( [3,                   BOARD_SIZE[1] - 3],   (6, 6) ),
        ( [BOARD_SIZE[0] - 3,   BOARD_SIZE[1] - 3],   (6, 6) ),
    ]
    SUPPORT_BLOCKS_POS_OFFSET = [-BOARD_SIZE[0]/2, -BOARD_SIZE[1]/2, 0]


    def __init__(
        self,
        enclosure_wall_thickness,
        screw_block_thickness = 6,
        add_model_to_footprint = True,
        use_simplified_model = False,
        use_ultra_simplified_model = False,
    ):
        try: cls_file = __file__            # regular launch
        except NameError: cls_file = None   # when launched from Jupyter
        super().__init__(
            # AbstractHolderPart
            enclosure_wall_thickness,
            screw_block_thickness,
            # Part
            cls_file,
            PART_CATEGORY,
            PART_ID,
            OctopusMotherboardHolderPart.STEP_FILE,
            OctopusMotherboardHolderPart.SIMPLIFIED_STEP_FILE,
            OctopusMotherboardHolderPart.ULTRA_SIMPLIFIED_STEP_FILE,
            OctopusMotherboardHolderPart.MODEL_OFFSET,
        )
        super().set_screws_specs(OctopusMotherboardHolderPart.SCREWS_SPECS, OctopusMotherboardHolderPart.SCREWS_POS_OFFSET)
        super().set_support_blocks_specs(OctopusMotherboardHolderPart.SUPPORT_BLOCKS_SPECS, OctopusMotherboardHolderPart.SUPPORT_BLOCKS_POS_OFFSET)

        board_size = (*OctopusMotherboardHolderPart.BOARD_SIZE, enclosure_wall_thickness)
        self.size.width, self.size.length, self.size.thickness = board_size

        self.part, self.mask = super().get_base_board_and_mask(board_size)

        # Inside footprint
        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = OctopusMotherboardHolderPart.PCB_THICKNESS + screw_block_thickness
        self.inside_footprint_offset = 0

        footprint_in = cq.Workplane("front")
        if add_model_to_footprint:
            footprint_in = super().get_step_model(
                use_simplified_model,
                use_ultra_simplified_model,
                [0, self.inside_footprint[1], screw_block_thickness + enclosure_wall_thickness]
            )
        else:
            footprint_in = (
                cq.Workplane("front")
                    .box(*self.inside_footprint, self.inside_footprint_thickness - screw_block_thickness, centered=(True, True, False))
                    .translate([0, 0, screw_block_thickness + enclosure_wall_thickness])
            )

        self.debug_objects.footprint.inside  = footprint_in

        # Outside footprint
        self.outside_footprint = (self.size.width, self.size.length)
        self.outside_footprint_thickness = 0
        self.outside_footprint_offset = 0

        self.debug_objects.footprint.outside = None