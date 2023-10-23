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

from cq_enclosure_builder.part import Part
from cq_enclosure_builder.parts_factory import register_part


@register_part("support", "pyramid")
class PyramidSupportPart(Part):
    """
    Can be placed underdeath components under a lot of stress (e.g. a guitar pedal switch) to strength it.
    """

    def __init__(
        self,
        enclosure_wall_thickness: float,
        support_height: float,
        base_size: float = 8,
        top_size: float = 5,
        pyramid_taper: float = 20
    ):
        super().__init__()

        # Board
        board = (
            cq.Workplane("front")
                .box(base_size, base_size, enclosure_wall_thickness, centered=(True, True, False))
        )
        board = board.add(
            cq.Workplane("front")
                .rect(base_size, base_size)
                .extrude(support_height, taper=pyramid_taper)
                .translate([0, 0, enclosure_wall_thickness])
        )
        board = board.add(
            cq.Workplane("front")
                .rect(top_size, top_size)
                .extrude(support_height + enclosure_wall_thickness)
        )

        self.part = board
        self.mask = (
            cq.Workplane("front")
                .box(base_size, base_size, enclosure_wall_thickness, centered=(True, True, False))
        )

        self.size.width     = base_size
        self.size.length    = base_size
        self.size.thickness = support_height

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = self.size.thickness
        self.inside_footprint_offset = (0, 0)

        self.outside_footprint = (0, 0)
        self.outside_footprint_thickness = 0

        self.debug_objects.footprint.inside  = board
        self.debug_objects.footprint.outside = None
        self.debug_objects.hole = None