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


@register_part("button", "PBS-110")
class ButtonPbs110Part(GenericThreadedWithStopPart):
    """
    Button PBS-110

    Could extend GenericThreadedWithStopPart instead, based on preferences (wouldn't poke out as much).

    https://www.aliexpress.com/item/32711341102.html
    """

    def __init__(
        self,
        enclosure_wall_thickness: float
    ):
        thread_diameter = 6.8
        super().__init__(
            enclosure_wall_thickness,

            width=12,
            length=12,

            thread_diameter=thread_diameter,
            thread_diameter_error_margin=0.6,
            thread_depth=6.8,

            washer_thickness=0.4,
            nut_thickness=2.2,
            margin_after_nut=1,

            pyramid_taper=42
        )

        button_block_thickness = 8.3 + 6.5
        self.inside_footprint = (self.width + 2, self.length + 2)
        self.inside_footprint_thickness = self.block_thickness + button_block_thickness
        self.inside_footprint_offset = (0, 0)

        button_outside_thickness = 20.7 - 8.3
        self.outside_footprint = (self.thread_diameter, self.thread_diameter)
        self.outside_footprint_thickness = button_outside_thickness - self.block_thickness - enclosure_wall_thickness  # updated later if button_cap is not None

        footprint_in = (
            cq.Workplane("front")
                .box(*self.inside_footprint, self.inside_footprint_thickness, centered=(True, True, False))
                .translate([0, 0, -self.inside_footprint_thickness])
        )
        footprint_out = (
            cq.Workplane("front")
                .circle(thread_diameter/2)
                .extrude(self.outside_footprint_thickness)
        )

        footprint_in = self.mirror_and_translate(footprint_in)
        footprint_out = self.mirror_and_translate(footprint_out)

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out