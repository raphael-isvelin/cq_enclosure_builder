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
        reinforced: bool = True,
        button_cap: KnobOrCap = CAP_23_75_x_11_9
    ):
        # TODO test dome vs. pyramid for reinforcement
        base_size = 28 if reinforced else 16
        taper = 35 if reinforced else 5
        super().__init__(
            enclosure_wall_thickness,

            width=base_size,
            length=base_size,

            thread_diameter=11.8,
            thread_diameter_error_margin=0.6,
            thread_depth=14,

            washer_thickness=0.75,
            nut_thickness=2.13,
            margin_after_nut=0.62,

            pyramid_taper=taper
        )

        button_block_thickness = 14
        self.inside_footprint = (16, 30.8)
        self.inside_footprint_thickness = self.block_thickness + button_block_thickness
        self.inside_footprint_offset = (0, -4.8)

        # TODO we want to add the nut [and washer], as well as in the debug object (esp. important if no cap)
        self.outside_footprint = (self.thread_diameter, self.thread_diameter)
        self.outside_footprint_thickness = 25.9 - self.block_thickness - enclosure_wall_thickness  # updated later if button_cap is not None

        footprint_in = (
            cq.Workplane("front")
                .box(*self.inside_footprint, button_block_thickness, centered=(True, True, False))
                .translate([0, (self.inside_footprint[1]/2) - 20.2, -(button_block_thickness + self.block_thickness)])
                .add(self.pyramid.mirror("XY").translate([0, 0, enclosure_wall_thickness]))
        )
        footprint_out = (
            cq.Workplane("front")
                .circle(self.thread_diameter/2)
                .extrude(self.outside_footprint_thickness)
                .translate([0, 0, enclosure_wall_thickness])
        )

        if button_cap is not None:
            self.outside_footprint = (button_cap.diameter, button_cap.diameter)
            knob_wp = (
                cq.Workplane("front")
                    .circle(button_cap.diameter/2)
                    .extrude(button_cap.thickness)
                    .translate([0, 0, enclosure_wall_thickness])
                    .translate([0, 0, self.outside_footprint_thickness - button_cap.inner_depth])
            )
            if button_cap.fillet > 0:
                knob_wp = knob_wp.edges("front").fillet(button_cap.fillet)
            footprint_out = footprint_out.add(knob_wp)
            self.outside_footprint_thickness = self.outside_footprint_thickness + (button_cap.thickness - button_cap.inner_depth)

        footprint_in = self.mirror_and_translate(footprint_in)
        footprint_out = self.mirror_and_translate(footprint_out)

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out