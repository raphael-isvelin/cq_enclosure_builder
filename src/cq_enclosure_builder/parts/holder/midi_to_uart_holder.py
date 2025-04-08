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
from cq_enclosure_builder.parts.common.screw_block import ScrewBlock
from cq_enclosure_builder.parts_factory import register_part

PART_CATEGORY = "holder"
PART_ID = "MIDI_to_UART"

"""
MIDI to UART board holder
"""
@register_part(PART_CATEGORY, PART_ID)
class MidiToUartHolderPart(AbstractHolderPart):

    BOARD_SIZE_XY = (22, 28)

    # STEP model
    STEP_FILE = "step/midi_to_uart.step"
    SIMPLIFIED_STEP_FILE = None
    ULTRA_SIMPLIFIED_STEP_FILE = None

    MODEL_OFFSET = [-BOARD_SIZE_XY[0]/2, -BOARD_SIZE_XY[1]/2, 0]
    PCB_THICKNESS = 11.54 - 1.31  # excluding everything under the PCB (pins)

    # Screws and Supports
    SCREWS_SPECS = [
        ( [3.5, 3.5],                   USE_DEFAULT_SCREW_BLOCK_PROVIDER ),
        ( [3.5, BOARD_SIZE_XY[1] - 3.5],   USE_DEFAULT_SCREW_BLOCK_PROVIDER ),
    ]
    SCREWS_POS_OFFSET = [-BOARD_SIZE_XY[0]/2, -BOARD_SIZE_XY[1]/2, 0]
    SUPPORT_BLOCKS_SPECS = [
        ( [BOARD_SIZE_XY[0] - 1.5, 1.5],                   (3, 3) ),
        ( [BOARD_SIZE_XY[0] - 1.5, BOARD_SIZE_XY[1] - 1.5],   (3, 3) ),
    ]
    SUPPORT_BLOCKS_POS_OFFSET = [-BOARD_SIZE_XY[0]/2, -BOARD_SIZE_XY[1]/2, 0]

    def __init__(
        self,
        enclosure_wall_thickness,
        screw_block_thickness = 2,
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
            # Part - TODO move before ewt/sbt once mandatory
            cls_file,
            PART_CATEGORY,
            PART_ID,
            MidiToUartHolderPart.STEP_FILE,
            MidiToUartHolderPart.SIMPLIFIED_STEP_FILE,
            MidiToUartHolderPart.ULTRA_SIMPLIFIED_STEP_FILE,
            MidiToUartHolderPart.MODEL_OFFSET,
        )
        super().set_screws_specs(MidiToUartHolderPart.SCREWS_SPECS, MidiToUartHolderPart.SCREWS_POS_OFFSET)
        super().set_support_blocks_specs(MidiToUartHolderPart.SUPPORT_BLOCKS_SPECS, MidiToUartHolderPart.SUPPORT_BLOCKS_POS_OFFSET)

        # Board & mask
        super().build_and_set_default_board_and_mask(MidiToUartHolderPart.BOARD_SIZE_XY)

        # Inside & outside footprints
        super().build_and_set_default_footprints(MidiToUartHolderPart.PCB_THICKNESS, add_model_to_footprint, use_simplified_model, use_ultra_simplified_model)