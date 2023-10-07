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
from cq_enclosure_builder.parts.common.knobs_and_caps import KnobOrCap, KNOB_16_4_x_14_8


@register_part("encoder", "EC11")
class EncoderEc11Part(GenericThreadedWithStopPart):
    """
    Encoder EC11

    https://www.aliexpress.com/item/10000056483250.html
    """

    def __init__(
        self,
        enclosure_wall_thickness: float,
        encoder_knob: KnobOrCap = KNOB_16_4_x_14_8
    ):
        super().__init__(
            enclosure_wall_thickness,

            width=12.05,
            length=15,

            thread_diameter=6.8,
            thread_diameter_error_margin=0.6,
            thread_depth=6.5,

            washer_thickness=0.36,
            nut_thickness=2.28,
            margin_after_nut=0.96,

            pyramid_taper=65,

            dents_specs=[
                ( (2, 0.8, 1), (0, -(2.7 + thread_diameter/2)) )
            ],
            dent_size_error_margin=0.6,
            dent_thickness_error_margin=0.4
        )

        encoder_block_thickness = 11.5
        self.inside_footprint = (self.width + 2, self.length + 2)
        self.inside_footprint_offset = (0, 0)
        self.inside_footprint_thickness = self.block_thickness + encoder_block_thickness

        # TODO we want to add the nut [and washer], as well as in the debug object (esp. important if no cap)
        self.outside_footprint = (self.thread_diameter, self.thread_diameter)
        self.outside_footprint_thickness = 30 - self.block_thickness - enclosure_wall_thickness  # updated later if encoder_knob is not None

        footprint_in = (
            cq.Workplane("front")
                .box(*self.inside_footprint, self.inside_footprint_thickness, centered=(True, True, False))
                .translate([0, 0, -self.inside_footprint_thickness])
        )
        footprint_out = (
            cq.Workplane("front")
                .circle(self.thread_diameter/2)
                .extrude(self.outside_footprint_thickness)
                .translate([0, 0, enclosure_wall_thickness])
        )

        if encoder_knob is not None:
            self.outside_footprint = (encoder_knob.diameter, encoder_knob.diameter)
            knob_wp = (
                cq.Workplane("front")
                    .circle(encoder_knob.diameter/2)
                    .extrude(encoder_knob.thickness)
                    .translate([0, 0, enclosure_wall_thickness])
                    .translate([0, 0, self.outside_footprint_thickness - encoder_knob.inner_depth])
            )
            if encoder_knob.fillet > 0:
                knob_wp = knob_wp.edges("front").fillet(encoder_knob.fillet)
            footprint_out = footprint_out.add(knob_wp)
            self.outside_footprint_thickness = self.outside_footprint_thickness + (encoder_knob.thickness - encoder_knob.inner_depth)

        footprint_in = self.mirror_and_translate(footprint_in)
        footprint_out = self.mirror_and_translate(footprint_out)

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out