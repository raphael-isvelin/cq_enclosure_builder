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
from cq_enclosure_builder.parts.common.knobs_and_caps import KnobOrCap, KNOB_18_x_17_25

@register_part("potentiometer", "WH148")
class PotentiometerWh148Part(GenericThreadedWithStopPart):
    """
    Potentiometer connector WH148 (basic 3-pin pot)
    """

    # TODO length is overkill, need to make it smaller, but add some offset
    def __init__(
        self,
        enclosure_wall_thickness: float,
        pot_knob: KnobOrCap = KNOB_18_x_17_25
    ):
        thread_depth = 6.4
        thread_diameter = 6.8
        super().__init__(
            enclosure_wall_thickness,

            width=18,
            length=27,

            thread_diameter=6.8,
            thread_diameter_error_margin=0.6,
            thread_depth=thread_depth,

            washer_thickness=0.36,
            nut_thickness=2.25,
            margin_after_nut=1.39,  # overwise the dent would go through the enclosure

            pyramid_taper=70,

            dents_specs=[
                ( (1.15, 2.5, 2), (-(11.85-(thread_diameter/2)-(2.2/2)), 0)  )
            ],
            dent_size_error_margin=0.6,
            dent_thickness_error_margin=0.0
        )

        potentiometer_block_thickness = 9.5
        self.inside_footprint = (self.width + 2, self.length + 2)
        self.inside_footprint_thickness = potentiometer_block_thickness + self.block_thickness
        self.inside_footprint_offset = (0, 3.15)  # TODO unhardcode

        thread_and_tip_depth = 14.8
        # TODO we want to add the nut [and washer], as well as in the debug object (esp. important if no cap)
        self.outside_footprint = (self.thread_diameter, self.thread_diameter)
        self.outside_footprint_thickness = thread_and_tip_depth - self.block_thickness - enclosure_wall_thickness  # updated later if button_cap is not None

        footprint_in = (
            cq.Workplane("front")
                .circle(17.2/2)
                .extrude(self.inside_footprint_thickness)

                .translate([0, 0, -self.inside_footprint_thickness - self.block_thickness])
                .add(
                    cq.Workplane("front")
                        .box(15.1, 21.4-(17.2/2), 3.4, centered=(True, False, False))
                        # .translate([0, -17.2/2, -3.4 - self.block_thickness])
                        .translate([0, -(21.4-(17.2/2)), -3.4 - self.block_thickness])
                )
                .add(self.dents.translate([0, 0, self.actual_wall_thickness - self.enclosure_wall_thickness]))
        )
        footprint_out = (
            cq.Workplane("front")
                .circle(self.thread_diameter/2)
                .extrude(self.outside_footprint_thickness)
                .translate([0, 0, self.actual_wall_thickness])
                
        )

        if pot_knob is not None:
            self.outside_footprint = (pot_knob.diameter, pot_knob.diameter)
            knob_wp = (
                cq.Workplane("front")
                    .circle(pot_knob.diameter/2)
                    .extrude(pot_knob.thickness)
                    .translate([0, 0, enclosure_wall_thickness])
                    .translate([0, 0, self.outside_footprint_thickness - pot_knob.inner_depth])
            )
            if pot_knob.fillet > 0:
                knob_wp = knob_wp.edges("front").fillet(pot_knob.fillet)
            footprint_out = footprint_out.add(knob_wp)
            self.outside_footprint_thickness = self.outside_footprint_thickness + (pot_knob.thickness - pot_knob.inner_depth)

        footprint_in = self.mirror_and_translate(footprint_in)
        footprint_out = self.mirror_and_translate(footprint_out)
        footprint_in = footprint_in.translate([0, 0, self.actual_wall_thickness - self.enclosure_wall_thickness])
        footprint_out = footprint_out.translate([0, 0, self.actual_wall_thickness - self.enclosure_wall_thickness])

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out