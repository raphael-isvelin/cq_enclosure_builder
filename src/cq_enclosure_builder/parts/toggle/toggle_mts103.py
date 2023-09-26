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

    def __init__(self, enclosure_wall_thickness):
        thread_diameter = 6.0
        super().__init__(
            enclosure_wall_thickness,

            width=14,
            length=14,

            thread_diameter=thread_diameter,
            thread_diameter_error_margin=0.6,
            thread_depth=8.8,

            washer_thickness=0.6,
            nut_thickness=1.9,
            margin_after_nut=0.5,

            pyramid_taper=35,
        )

        self.inside_footprint = (13, 8.2)
        self.inside_footprint_offset = (0, 0)
        footprint_in = (
            cq.Workplane("front")
                .box(*self.inside_footprint, 10, centered=(True, True, False))
                .translate([0, 0, -10.0])
        )

        self.outside_footprint = (self.thread_diameter, self.thread_diameter)
        footprint_out = (
            cq.Workplane("front")
                .circle(thread_diameter/2)
                .extrude(self.thread_depth)
                .translate([0, 0, enclosure_wall_thickness])
                .add(
                    cq.Workplane("front")
                        .circle(1.5)
                        .extrude(10.2)
                        .translate([0, 0, self.thread_depth])
                )
        )

        footprint_in = self.mirror_and_translate(footprint_in)
        footprint_out = self.mirror_and_translate(footprint_out)

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out