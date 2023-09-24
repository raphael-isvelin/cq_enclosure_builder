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

from typing import Tuple

import cadquery as cq
from cq_enclosure_builder.part import Part
from cq_enclosure_builder.parts_factory import register_part

@register_part("support", "skirt")
class SkirtPart(Part):
    """
    Makes a 'skirt' (triangles on all sides) to add some support to the panel.
    """
    def __init__(
        self,
        enclosure_wall_thickness,
        width,
        length,
        skirt_size: Tuple[float, float] = (4, 4)
    ):
        super().__init__()

        width_bar = (
            cq.Workplane("XY")
                .moveTo(0, 0)
                .lineTo(-skirt_size[1], 0)
                .lineTo(0, -skirt_size[0])
                .close()
                .extrude(width)
                .rotate((0, 0, 0), (1, 0, 0), 90)
                .translate([0, width/2, 0])
        )
        length_bar = (
            cq.Workplane("XY")
                .moveTo(0, 0)
                .lineTo(-skirt_size[1], 0)
                .lineTo(0, -skirt_size[0])
                .close()
                .extrude(length)
                .rotate((0, 0, 0), (1, 0, 0), 90)
                .translate([0, length/2, 0])
        )
        up = width_bar.rotate((0, 0, 0), (0, 0, 1), 90).translate([0, length/2, 0])
        down = width_bar.rotate((0, 0, 0), (0, 0, 1), -90).translate([0, -(length/2), 0])
        left = length_bar.rotate((0, 0, 0), (0, 0, 1), 180).translate([-(width/2), 0, 0])
        right = length_bar.translate([width/2, 0, 0])

        skirt = (
            up
                .add(down)
                .add(left)
                .add(right)
                .rotate((0, 0, 0), (0, 1, 0), 180)
                .translate([0, 0, enclosure_wall_thickness])
        )

        self.part = skirt
        self.mask = skirt

        self.size.width     = width
        self.size.length    = length
        self.size.thickness = skirt_size[1]

        self.inside_footprint = (self.size.width, self.size.length)  # TODO should account for the screw blocks (incl. taper)
        self.inside_footprint_offset = (0, 0)
        self.outside_footprint = (self.size.width, self.size.length)
        self.debug_objects.footprint.inside  = skirt
        self.debug_objects.footprint.outside = None
        
        self.debug_objects.hole = None