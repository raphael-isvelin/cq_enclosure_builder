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

@register_part("encoder", "XXX")
class EncoderXxxPart(GenericThreadedWithStopPart):
    """
    SPST connector XXX

    TODO
    """

    def __init__(self, enclosure_wall_thickness):
        thread_diameter = 6.8
        super().__init__(
            enclosure_wall_thickness,

            width=12.05,
            length=15,

            thread_diameter=thread_diameter,
            thread_diameter_error_margin=0.6,
            thread_depth=5.5,

            washer_thickness=0.36,
            nut_thickness=2.28,
            margin_after_nut=0.36,

            pyramid_taper=65,

            dents_specs=[
                ( (2, 0.8, 1), (0, -(2.7 + thread_diameter/2)) )
            ],
            dent_size_error_margin=0.6,
            dent_thickness_error_margin=0.4
        )

        thread_and_button_depth = 16.4

        footprint_out_button_cap_diameter = 28
        footprint_out_button_cap_thickness = 12

        self.inside_footprint = (self.width + 2, self.length + 2)
        self.inside_footprint_offset = (0, 0)
        self.outside_footprint = (footprint_out_button_cap_diameter, footprint_out_button_cap_diameter)

        footprint_in = (
            cq.Workplane("front")
                .box(*self.inside_footprint, 10, centered=(True, True, False))
                .translate([0, 0, -10.0])
        )
        footprint_out = (
            cq.Workplane("front")
                .circle(thread_diameter/2)
                .extrude(thread_and_button_depth - enclosure_wall_thickness)
                .translate([0, 0, enclosure_wall_thickness])
                .add((
                    cq.Workplane("front")
                        .circle(footprint_out_button_cap_diameter/2)
                        .extrude(footprint_out_button_cap_thickness)
                        .translate([0, 0, enclosure_wall_thickness + (thread_and_button_depth - footprint_out_button_cap_thickness)])
                        .edges("front")
                        .fillet(1)
                ))
        )

        footprint_in = self.mirror_and_translate(footprint_in)
        footprint_out = self.mirror_and_translate(footprint_out)

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out