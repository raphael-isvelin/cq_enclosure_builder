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

@register_part("button", "SPST XX")
class ButtonSpstXxxPart(GenericThreadedWithStopPart):
    """
    SPST connector XXX

    TODO
    """

    def __init__(self, enclosure_wall_thickness):
        super().__init__(
            enclosure_wall_thickness,

            width=16,
            length=16,

            thread_diameter=11.8,
            thread_diameter_error_margin=0.6,
            thread_depth=14,

            washer_thickness=0.75,
            nut_thickness=2.13,
            margin_after_nut=0.0,

            pyramid_taper=5
        )

        footprint_in_length = 30.8
        footprint_out_button_cap_diameter = 24
        footprint_out_button_cap_thickness = 12

        self.inside_footprint = (self.width, footprint_in_length)
        self.inside_footprint_offset = (0, -4.8)
        self.outside_footprint = (footprint_out_button_cap_diameter, footprint_out_button_cap_diameter)

        footprint_in = (
            cq.Workplane("front")
                .box(*self.inside_footprint, 16 - enclosure_wall_thickness, centered=(True, True, False))
                .translate([0, (footprint_in_length/2) - 20.2, -(25.0 - enclosure_wall_thickness)])
                .add((
                    cq.Workplane("front")
                        .box(self.width, self.length, 9, centered=(True, True, False))
                        .translate([0, 0, -9])
                ))
        )
        footprint_out = (
            cq.Workplane("front")
                .circle(self.thread_diameter/2)
                .extrude(15)
                .translate([0, 0, enclosure_wall_thickness])
                .add((
                    cq.Workplane("front")
                        .circle(footprint_out_button_cap_diameter/2)
                        .extrude(footprint_out_button_cap_thickness)
                        .translate([0, 0, enclosure_wall_thickness + 6.6])
                        .edges("front")
                        .fillet(1)
                ))
        )

        footprint_in = self.mirror_and_translate(footprint_in)
        footprint_out = self.mirror_and_translate(footprint_out)

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out