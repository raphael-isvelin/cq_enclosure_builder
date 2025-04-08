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
from cq_enclosure_builder.parts.common.generic_threaded_part import GenericThreadedWithStopPart
from cq_enclosure_builder.parts_factory import register_part


"""
Panel of 6.35mm female jacks connector ACJS-MV-5 (and 2, 3S, etc.)

6x2x8 layout - TODO when needed, make panel more modular (at least grid configuration, eventually jack model)

https://www.mouser.ee/ProductDetail/Amphenol-Audio/ACJS-MV-5?qs=c9RBuMmXG6JIOKwHTyIaMA%3D%3D
"""
@register_part("jack", "Panel_6x2x8")
class JacksPanel6x2x8Part(Part):


    def __init__(
        self,
        enclosure_wall_thickness: float,
        nut_diameter = 14.3,
        nut_thickness = 3.4,
        add_model_to_footprint: bool = True,
    ):
        super().__init__()

        board_size = (159, 42.13, enclosure_wall_thickness)

        board = (
            cq.Workplane("front")
                .box(*board_size, centered=(True, True, False))
        )

        pyramid = self.get_pyramid(15.8, 4.4 - enclosure_wall_thickness, 9.9)
        pyramid = pyramid.translate([0, 0, enclosure_wall_thickness])

        jacks_pos = [
            (0,        8.613),        (0, -8.387),
            (27,       8.613),       (27, -8.387),
            (27+17,    8.613),    (27+17, -8.387),
            (27+17*2,  8.613),  (27+17*2, -8.387),
            (27+17*3,  8.613),  (27+17*3, -8.387),
            (-27,      8.613),      (-27, -8.387),
            (-27-17,   8.613),   (-27-17, -8.387),
            (-27-17*2, 8.613), (-27-17*2, -8.387),
        ]
        jacks_offset = (-8.4, 0)

        dents = self.get_dents(enclosure_wall_thickness, 0.4)
        jacks_pyramids = cq.Workplane("front")
        all_dents = cq.Workplane("front")
        for base_pos in jacks_pos:
            pos = (base_pos[0] + jacks_offset[0], base_pos[1] + jacks_offset[1])
            board = board.add(pyramid.translate(pos))
            board = board.cut(dents.translate(pos))
        board.add(jacks_pyramids)
        board = (
            board
                .faces(">Z").workplane()
                .center(*jacks_offset)
                .pushPoints(jacks_pos)
                .hole(9.9)
        )
        # board = board.cut(all_dents)

        self.part = board
        self.mask = cq.Workplane("front").box(*board_size, centered=(True, True, False))

        self.size.width, self.size.length, self.size.thickness = board_size

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = 20
        # self.inside_footprint_offset = (8.4, 0)
        self.inside_footprint_offset = (0, 0)

        self.outside_footprint = (153.3, 31.29)
        self.outside_footprint_thickness = nut_thickness
        self.outside_footprint_offset = (0, 0)
        # self.outside_footprint_offset = (8.5, 0.113) # TODO seems like it's ignored - move whole board to 0,0

        if add_model_to_footprint:
            step_dir = "../src/cq_enclosure_builder/parts/jack"  # when launched from Jupyter
            try: step_dir = os.path.dirname(__file__)  # regular launch
            except NameError: pass
            model_path = os.path.join(step_dir, "jacks_panel_6x2x8.step")
            model = (
                cq.importers.importStep(model_path)
                    .rotate((0,0,0), (1,0,0), 180)
                    .translate([-132.5, -100, 30.145])  # base offset +8.4 / +8.613/-8.387. / all 17, big 27 
            )
            footprint_in = cq.Workplane("front").add(model)
            bounding_box = model.val().BoundingBox()
            self.inside_footprint_offset = (
                -abs(abs(bounding_box.xmin) - abs(bounding_box.xmax)) / 2,
                abs(abs(bounding_box.ymin) - abs(bounding_box.ymax)) / 2
            )
            self.inside_footprint_thickness = abs(bounding_box.zmin) + abs(bounding_box.zmax)
        else:
            footprint_in = (
                cq.Workplane("front")
                    .box(self.size.width, self.size.length, self.inside_footprint_thickness, centered=(True, True, False))
                    .translate([*self.inside_footprint_offset, enclosure_wall_thickness])
            )

        footprint_nut = cq.Workplane("front").circle(nut_diameter/2).extrude(nut_thickness).translate([0, 0, -nut_thickness])
        footprint_out = cq.Workplane("front")
        for base_pos in jacks_pos:
            pos = (base_pos[0] + jacks_offset[0], base_pos[1] + jacks_offset[1])
            footprint_out = footprint_out.add(footprint_nut.translate(pos))

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out


    def get_pyramid(self, size: float, block_thickness: float, thread_hole_diameter: float, taper: int = 45):
        base_pyramid: cq.Workplane = (
            cq.Workplane("front")
                .polyline([(0, 0), (size, 0), (size, size), (0, size)]).close()
                .extrude(-size, taper=taper)
                .translate([-(size/2), -(size/2), 0])
        )
        pyramid_cut_box = (
            cq.Workplane("front")
                .box(size, size, 20, centered=(True, True, False))
                .translate([0, 0, -20-block_thickness])
        )
        pyramid = base_pyramid.translate([0,0,0]).cut(pyramid_cut_box)
        pyramid = pyramid.rotate((0,0,0), (0,1,0), 180)
        return pyramid

    def get_dents(self, enclosure_wall_thickness: float, block_thickness: float, dent_thickness: float = 2):
        dents_specs=[
            ( (1.6, 2, dent_thickness), (-7, 0 )  ),
            ( (1.6, 2, dent_thickness), ( 7, 0 )  ),
            ( (2, 1.6, dent_thickness), (0, -7 )  ),
            ( (2, 1.6, dent_thickness), (0,  7 )  ),
        ]
        dents = cq.Workplane("back")
        for dent_sp in dents_specs:       
            dent_size, dent_pos = dent_sp
            dent = cq.Workplane("back").box(*dent_size, centered=(True, True, False)).translate([*dent_pos, block_thickness + enclosure_wall_thickness])
            dents = dents.add(dent)
        return dents