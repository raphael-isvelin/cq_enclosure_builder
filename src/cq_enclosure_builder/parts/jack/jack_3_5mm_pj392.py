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


@register_part("jack", "3.5mm PJ-392")
class Jack3_5mmXxxPart(GenericThreadedWithStopPart):
    """
    3.5mm female jack connector PJ-392

    https://www.aliexpress.com/item/4000147271338.html
    """

    def __init__(
        self,
        enclosure_wall_thickness: float
    ):
        super().__init__(
            enclosure_wall_thickness,

            width=9,
            length=9,

            thread_diameter=5.85,
            thread_diameter_error_margin=0.6,
            thread_depth=4.6,

            washer_thickness=1.9,
            nut_thickness=0.4,
            margin_after_nut=0.0,

            pyramid_taper=23
        )
        
        jack_diameter_with_nut = self.thread_diameter + 1.5

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_offset = (0, 0)
        self.inside_footprint_thickness = 10

        self.outside_footprint = (jack_diameter_with_nut, jack_diameter_with_nut)
        self.outside_footprint_thickness = self.nut_depth

        footprint_in = (
            cq.Workplane("front")
                .box(self.size.width, self.size.length, self.inside_footprint_thickness, centered=(True, True, False))
                .translate([0, 0, enclosure_wall_thickness])
        )
        footprint_out = (
            cq.Workplane("front")
                .circle(jack_diameter_with_nut/2)
                .extrude(self.outside_footprint_thickness)
                .translate([0, 0, -self.outside_footprint_thickness])
        )
        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out