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

# TODO preset for sizes; approx. decent values for the default text:
# XL: 90 40 15
# LG: 60 30 10
# MD: 40 18 6
# SM: 20 10 3  (not great even with 0.15 layer height)

@register_part("text", "default")
class TextPart(Part):
    """
    A block with extruded or cut text
    """

    def __init__(
        self,
        enclosure_wall_thickness,
        text = "Sample text\nLine 2",
        thickness = 1.4,
        cut = False,
        fontsize = 6,
        width = 40,
        length = 18,
        halign = "center",
        valign = "center",
    ):
        super().__init__()

        text_wp = None
        if cut:
            text_wp = (
                cq.Workplane()
                    .box(width, length, enclosure_wall_thickness + thickness, centered=(True, True, False))
                    .faces(">Z").workplane()
                    .text(text, fontsize=fontsize, distance=-thickness, halign=halign, valign=valign)
            )
        else:
            text_wp = (
                cq.Workplane()
                    .box(width, length, enclosure_wall_thickness, centered=(True, True, False))
                    .add(
                        cq.Workplane()
                            .text(text, fontsize=fontsize, distance=thickness, halign=halign, valign=valign)
                            .translate([0, 0, enclosure_wall_thickness])
                    )
            )

        mask = (
            cq.Workplane()
                .box(width, length, enclosure_wall_thickness, centered=(True, True, False))
        )

        self.part = text_wp
        self.mask = mask

        self.size.width     = width
        self.size.length    = length
        self.size.thickness = enclosure_wall_thickness + thickness

        self.inside_footprint = (self.size.width, self.size.length)  # text isn't taken into account (can be more or less)
        self.inside_footprint_offset = (0, 0)

        self.outside_footprint = (self.size.width, self.size.length)

        self.debug_objects.footprint.inside  = text
        self.debug_objects.footprint.outside = None