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
from cq_enclosure_builder.parts.common.knobs_and_caps import CAP_28_x_11_8_D

@register_part("encoder", "EC11")
class EncoderEc11Part(GenericThreadedWithStopPart):
    """
    Encoder EC11

    https://www.aliexpress.com/item/10000056483250.html
    """
    def __init__(self, enclosure_wall_thickness, encoder_knob = CAP_28_x_11_8_D):
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

        self.inside_footprint = (self.width + 2, self.length + 2)
        self.inside_footprint_offset = (0, 0)
        footprint_in = (
            cq.Workplane("front")
                .box(*self.inside_footprint, 10, centered=(True, True, False))
                .translate([0, 0, -10.0])
        )

        self.outside_footprint = (self.thread_diameter, self.thread_diameter)
        footprint_out_thickness_without_knob = 15.0 - self.enclosure_wall_thickness
        footprint_out = (
            cq.Workplane("front")
                .circle(thread_diameter/2)
                .extrude(footprint_out_thickness_without_knob)
                .translate([0, 0, enclosure_wall_thickness])
        )

        if encoder_knob is not None:
            self.outside_footprint = (encoder_knob.diameter, encoder_knob.diameter)
            knob_wp = (
                cq.Workplane("front")
                    .circle(encoder_knob.diameter/2)
                    .extrude(encoder_knob.thickness)
                    .translate([0, 0, enclosure_wall_thickness])
                    .translate([0, 0, footprint_out_thickness_without_knob - encoder_knob.inner_depth])
            )
            if encoder_knob.fillet > 0:
                knob_wp = knob_wp.edges("front").fillet(encoder_knob.fillet)
            footprint_out = footprint_out.add(knob_wp)

        footprint_in = self.mirror_and_translate(footprint_in)
        footprint_out = self.mirror_and_translate(footprint_out)

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out