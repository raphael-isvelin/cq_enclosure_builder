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

@register_part("midi", "MIDI_to_UART")
class MidiToUartHolderPart(Part):
    """
    MIDI to UART board holder
    """
    def __init__(
        self,
        enclosure_wall_thickness,
        screw_block_thickness = 2,
        add_model_to_footprint = True,
    ):
        super().__init__()

        screws_pos = [
            (3.5, 3.5),
            (3.5, 28-3.5)
        ]

        screw_part: Part = ScrewBlock().m2_5(screw_block_thickness, enclosure_wall_thickness)
        screw = screw_part["block"].translate([0, 0, enclosure_wall_thickness])
        screw_size = screw_part["size"]

        screws_a = cq.Assembly()
        for screw_pos in screws_pos:
            screws_a.add(screw.translate(screw_pos))

        board_size = (22, 28)

        board = (
            cq.Workplane("front")
                .box(*board_size, enclosure_wall_thickness, centered=(True, True, False))

                .faces(">Z").workplane()
                .move(board_size[0]/2-1.5, board_size[1]/2-1.5).rect(3, 3)
                .extrude(screw_block_thickness)
                .faces(">Z").workplane()
                .move(board_size[0]/2-1.5, -board_size[1]/2+1.5).rect(3, 3)
                .extrude(-screw_block_thickness)

                .add(screws_a.toCompound().translate([-board_size[0]/2, -board_size[1]/2, 0]))
                
        )
        mask = (
            cq.Workplane("front")
                .box(*board_size, enclosure_wall_thickness, centered=(True, True, False))
        )

        self.part = board
        self.mask = mask

        self.size.width, self.size.length = board_size
        self.size.thickness = enclosure_wall_thickness

        pcb_thickness = 11.54 - 1.31
        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = pcb_thickness + screw_block_thickness
        self.inside_footprint_offset = (0, 0)

        self.outside_footprint = (self.size.width, self.size.length)
        self.outside_footprint_thickness = 0

        footprint_in = cq.Workplane("front")
        if add_model_to_footprint:
            step_dir = "../src/cq_enclosure_builder/parts/midi"  # when launched from Jupyter
            try: step_dir = os.path.dirname(__file__)  # regular launch
            except NameError: pass
            model_path = os.path.join(step_dir, "midi_to_uart.step")
            model = cq.importers.importStep(model_path)
            footprint_in = (
                model
                    .translate([0, self.inside_footprint[1], 0])
                    .translate([-board_size[0]/2, -board_size[1]/2, 0])
                    .translate([0, 0, screw_block_thickness + enclosure_wall_thickness])
            )
            self.inside_footprint_thickness = screw_block_thickness + 20.1 - 1.8
        else:
            footprint_in = (
                cq.Workplane("front")
                    .box(*self.inside_footprint, self.inside_footprint_thickness - screw_block_thickness, centered=(True, True, False))
                    .translate([0, 0, screw_block_thickness + enclosure_wall_thickness])
            )

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = None