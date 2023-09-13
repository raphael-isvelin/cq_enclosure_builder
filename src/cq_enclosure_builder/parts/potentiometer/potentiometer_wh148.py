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
# from cq_enclosure_builder import KnobOrCap

@register_part("potentiometer", "WH148")
class PotentiometerWh148Part(GenericThreadedWithStopPart):
    """
    Potentiometer connector WH148 (basic 3-pin pot)
    """

    def __init__(
        self,
        enclosure_wall_thickness,
        pot_knob = None
    ):
        thread_depth = 6.4
        thread_diameter = 6.8
        thread_and_tip_depth = 14.8  # how much would be sticking out if enclosure_wall_thickness was 0
        super().__init__(
            enclosure_wall_thickness,

            width=17.2,
            length=20.4,

            thread_diameter=thread_diameter,
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
            dent_thickness_error_margin=0.2
        )

        self.inside_footprint = (self.width + 2, self.length + 2)
        self.inside_footprint_offset = (0, 3.15)  # TODO unhardcode
        self.outside_footprint = (thread_diameter, thread_diameter)

        inside_footprint_depth = 9.1
        footprint_in = (
            cq.Workplane("front")
                .circle(17.2/2)
                .extrude(inside_footprint_depth)
                .translate([0, 0, -inside_footprint_depth - self.block_thickness])
                .add(
                    cq.Workplane("front")
                        .box(15.1, 21.2-(17.2/2), 3.4, centered=(True, True, False))
                        .translate([0, 17.2/2, -3.4 - self.block_thickness])
                )
        )

        footprint_out_thickness_without_knob = thread_and_tip_depth - self.block_thickness - enclosure_wall_thickness
        footprint_out = (
            cq.Workplane("front")
                .circle(thread_diameter/2)
                .extrude(footprint_out_thickness_without_knob)
                .translate([0, 0, enclosure_wall_thickness])
                
        )

        if pot_knob is not None:
            self.outside_footprint = (pot_knob.diameter, pot_knob.diameter)
            knob_wp = (
                cq.Workplane("front")
                    .circle(pot_knob.diameter/2)
                    .extrude(pot_knob.thickness)
                    .translate([0, 0, enclosure_wall_thickness + pot_knob.distance_from_enclosure_wall])
            )
            if pot_knob.fillet > 0:
                knob_wp = knob_wp.edges("front").fillet(pot_knob.fillet)
            footprint_out = footprint_out.add(knob_wp)


        footprint_in = self.mirror_and_translate(footprint_in)
        footprint_out = self.mirror_and_translate(footprint_out)

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out