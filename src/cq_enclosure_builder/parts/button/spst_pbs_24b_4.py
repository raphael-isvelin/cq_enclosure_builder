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
from cq_enclosure_builder.parts.common.knobs_and_caps import KnobOrCap, CAP_23_75_x_11_9

@register_part("button", "SPST PBS-24B-4")
class ButtonSpstPbs24b4Part(GenericThreadedWithStopPart):
    """
    SPST connector PBS-24B-4

    https://www.aliexpress.com/item/1005004646906063.html
    """
    def __init__(
        self,
        enclosure_wall_thickness: float,
        button_cap: KnobOrCap = CAP_23_75_x_11_9
    ):
        super().__init__(
            enclosure_wall_thickness,

            width=16,
            length=16,

            thread_diameter=11.8,
            thread_diameter_error_margin=0.6,
            thread_depth=14,

            washer_thickness=0.75,
            nut_thickness=2.13,
            margin_after_nut=0.62,

            pyramid_taper=5
        )

        footprint_in_length = 30.8
        self.inside_footprint = (self.width, footprint_in_length)
        self.inside_footprint_thickness = 23
        self.inside_footprint_offset = (0, -4.8)
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

        self.outside_footprint = (self.thread_diameter, self.thread_diameter)
        footprint_out_thickness_without_knob = 25.8 - self.block_thickness - self.enclosure_wall_thickness
        footprint_out = (
            cq.Workplane("front")
                .circle(self.thread_diameter/2)
                .extrude(15)
                .translate([0, 0, enclosure_wall_thickness])
        )

        if button_cap is not None:
            self.outside_footprint = (button_cap.diameter, button_cap.diameter)
            knob_wp = (
                cq.Workplane("front")
                    .circle(button_cap.diameter/2)
                    .extrude(button_cap.thickness)
                    .translate([0, 0, enclosure_wall_thickness])
                    .translate([0, 0, footprint_out_thickness_without_knob - button_cap.inner_depth])
            )
            if button_cap.fillet > 0:
                knob_wp = knob_wp.edges("front").fillet(button_cap.fillet)
            footprint_out = footprint_out.add(knob_wp)

        footprint_in = self.mirror_and_translate(footprint_in)
        footprint_out = self.mirror_and_translate(footprint_out)

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out