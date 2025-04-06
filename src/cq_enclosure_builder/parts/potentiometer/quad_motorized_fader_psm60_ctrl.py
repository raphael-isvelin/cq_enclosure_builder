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
from cq_warehouse.fastener import CounterSunkScrew

@register_part("potentiometer", "PSM60_Ctrl_x4")
class QuadMotorizedFaderPsm60CtrlPart(Part):
    """
    Quad Motorized fader with controller

    PSM60-081A-103B2: https://www.mouser.ee/ProductDetail/652-PSM60-081A-103B2
    Controller: https://www.pcbway.com/project/shareproject/Motorized_Slide_Pot_Controller_0d1f8563.html
    """
    def __init__(
        self,
        enclosure_wall_thickness,
        fader_distance = 23,
        add_model_to_footprint = True,
    ):
        super().__init__()

        board_size = (112, 90.1, 1.5)
        board_offset = (-5.00, 3.55)
        slit_size = (72, 3)

        screws_pos = [
            (-40, fader_distance*0.5), (40, fader_distance*0.5),
            (-40, fader_distance*1.5), (40, fader_distance*1.5),
            (-40, fader_distance*-0.5), (40, fader_distance*-0.5),
            (-40, fader_distance*-1.5), (40, fader_distance*-1.5),
        ]
        screw = CounterSunkScrew(size="M3-0.5", fastener_type="iso7046",length=10)

        slit = cq.Workplane("front").box(*slit_size, 10, centered=(True, True, False))
        board = (
            cq.Workplane("front")
                .box(*board_size, centered=(True, True, False))
                .translate([*board_offset, 0])
                .faces("<Z").workplane()
                .pushPoints(screws_pos)
                .clearanceHole(fastener=screw, fit="Loose", counterSunk=True)
                .cut(slit.translate([0, fader_distance*0.5, 0]))
                .cut(slit.translate([0, fader_distance*1.5, 0]))
                .cut(slit.translate([0, fader_distance*-0.5, 0]))
                .cut(slit.translate([0, fader_distance*-1.5, 0]))
        )
        mask = (
            cq.Workplane("front")
                .box(board_size[0], board_size[1], enclosure_wall_thickness, centered=(True, True, False))
                .translate([*board_offset, 0])
        )

        self.part = board
        self.mask = mask

        self.size.width, self.size.length, self.size.thickness = board_size

        inside_footprint_single = (112, 21.095)
        self.inside_footprint = (112, 90.1)
        self.inside_footprint_thickness = 37.6
        self.inside_footprint_offset = (5.00, 3.55)

        self.outside_footprint = (86, 13)
        self.outside_footprint_thickness = 9

        footprint_in = None
        if add_model_to_footprint:
            step_dir = "../src/cq_enclosure_builder/parts/potentiometer"  # when launched from Jupyter
            try: step_dir = os.path.dirname(__file__)  # regular launch
            except NameError: pass
            model_path = os.path.join(step_dir, "psm60_with_controller_noslider.step")
            model = (
                cq.importers.importStep(model_path)
                    .rotate((0,0,0), (1,0,0), 180)
                    .translate([0, 0, min(board_size[2], enclosure_wall_thickness)])
            )
            footprint_in = cq.Workplane("front")
            for offset_y in [fader_distance*0.5, fader_distance*1.5, fader_distance*-0.5, fader_distance*-1.5]:
                footprint_in.add(model.translate([0, offset_y, 0]))
            bounding_box = model.val().BoundingBox()
            self.inside_footprint_offset = (
                -abs(abs(bounding_box.xmin) - abs(bounding_box.xmax)) / 2,
                abs(abs(bounding_box.ymin) - abs(bounding_box.ymax)) / 2
            )
            self.inside_footprint_thickness = abs(bounding_box.zmin) + abs(bounding_box.zmax)
        else:
            footprint_in = cq.Workplane("front")
            for offset_y in [fader_distance*0.5, fader_distance*1.5, fader_distance*-0.5, fader_distance*-1.5]:
                footprint_in.add(
                    cq.Workplane("front")
                        .box(*inside_footprint_single, self.inside_footprint_thickness, centered=(True, True, False))
                        .translate([*self.inside_footprint_offset, board_size[2]])
                        .translate([0, offset_y, 0])
                )
        footprint_out =  cq.Workplane("front")
        for offset_y in [fader_distance*0.5, fader_distance*1.5, fader_distance*-0.5, fader_distance*-1.5]:
            footprint_out.add(
                cq.Workplane("front")
                    .box(*self.outside_footprint, self.outside_footprint_thickness, centered=(True, True, False))
                    .translate([0, 0, -self.outside_footprint_thickness])
                    .translate([0, offset_y, 0])
            )
        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out