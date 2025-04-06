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
from cq_enclosure_builder.parts.common.generic_threaded_part import GenericThreadedWithStopPart
from cq_enclosure_builder.parts_factory import register_part


@register_part("jack", "6.35mm ACJS-MV-5")
class Jack6_35mmAcjsMv5Part(GenericThreadedWithStopPart):
    """
    6.35mm female jack connector ACJS-MV-5 (and 2, 3S, etc.)

    https://www.mouser.ee/ProductDetail/Amphenol-Audio/ACJS-MV-5?qs=c9RBuMmXG6JIOKwHTyIaMA%3D%3D
    """

    def __init__(
        self,
        enclosure_wall_thickness: float
    ):
        super().__init__(
            enclosure_wall_thickness,

            width=15.8,
            length=15.8,

            thread_diameter=9.5,
            thread_diameter_error_margin=0.4,
            thread_depth=7.2,

            washer_thickness=0.53,
            nut_thickness=2.0,
            margin_after_nut=0.47,

            pyramid_taper=40,

            dents_specs=[
                ( (1.6, 2, 1), (-7, 0 )  ),
                ( (1.6, 2, 1), ( 7, 0 )  ),
                ( (2, 1.6, 1), (0, -7 )  ),
                ( (2, 1.6, 1), (0,  7 )  ),
            ],
            dent_size_error_margin=0.2,
            dent_thickness_error_margin=0.0
        )
        
        jack_diameter_with_nut = 14.3

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = 20
        self.inside_footprint_offset = (0, 0)

        # TODO we want to add the nut [and washer], as well as in the debug object
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