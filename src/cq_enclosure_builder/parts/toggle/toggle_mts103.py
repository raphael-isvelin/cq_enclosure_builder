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

from cq_enclosure_builder.parts.common.generic_threaded_part import GenericThreadedWithStopPart
from cq_enclosure_builder.parts_factory import register_part


@register_part("toggle", "MTS-103")
class ToggleMts103Part(GenericThreadedWithStopPart):
    """
    MTS-103 3-pin toggle

    https://www.aliexpress.com/item/1005005708888531.html
    """

    def __init__(
        self,
        enclosure_wall_thickness: float
    ):
        super().__init__(
            enclosure_wall_thickness,

            width=14,
            length=14,

            thread_diameter=6.0,
            thread_diameter_error_margin=0.6,
            thread_depth=8.8,

            washer_thickness=0.6,
            nut_thickness=1.9,
            margin_after_nut=0.5,

            pyramid_taper=35,
        )

        toggle_block_size = (13, 8.2)
        toggle_block_thickness = 9.5 + 6.3
        self.inside_footprint = (
            toggle_block_size[0] if toggle_block_size[0] > self.width else self.width,
            toggle_block_size[1] if toggle_block_size[1] > self.length else self.length
        )
        self.inside_footprint_thickness = self.block_thickness + toggle_block_thickness
        self.inside_footprint_offset = (0, 0)

        toggle_thread_minus_wall = self.thread_depth - self.block_thickness - enclosure_wall_thickness
        toggle_stick_thickness = 10.2
        # TODO we want to add the nut [and washer], as well as in the debug object
        self.outside_footprint = (self.thread_diameter, self.thread_diameter)
        self.outside_footprint_thickness = toggle_thread_minus_wall + toggle_stick_thickness

        footprint_in = (
            cq.Workplane("front")
                .box(*toggle_block_size, toggle_block_thickness, centered=(True, True, False))
                .translate([0, 0, -(toggle_block_thickness + self.block_thickness)])
                .add(self.pyramid.mirror("XY").translate([0, 0, enclosure_wall_thickness]))
        )
        footprint_out = (
            cq.Workplane("front")
                .circle(self.thread_diameter/2)
                .extrude(toggle_thread_minus_wall)
                .translate([0, 0, enclosure_wall_thickness])
                .add(
                    cq.Workplane("front")
                        .circle(1.5)
                        .extrude(toggle_stick_thickness)
                        .translate([0, 0, toggle_thread_minus_wall + enclosure_wall_thickness])
                )
        )
        self.debug_objects.footprint.inside  = self.mirror_and_translate(footprint_in)
        self.debug_objects.footprint.outside = self.mirror_and_translate(footprint_out)