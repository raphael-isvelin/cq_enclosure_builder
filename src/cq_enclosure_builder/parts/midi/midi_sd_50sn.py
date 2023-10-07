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


@register_part("midi", "SD-50SN")
class MidiSd50SnPart(Part):
    """
    MIDI connector SD-50SN

    https://www.aliexpress.com/item/4000583940302.html
    https://eu.mouser.com/ProductDetail/CUI-Devices/SD-50SN?qs=WyjlAZoYn50pT1yyPY7AcA%3D%3D
    """

    def __init__(
        self,
        enclosure_wall_thickness: float
    ):
        super().__init__()

        width = 19.2
        length = 28.4

        hole_diameter = 15.1 + 0.5
        screw_holes_diameter = 2.9 + 0.3

        # Board
        board = (
            cq.Workplane("front")
                .box(width, length, enclosure_wall_thickness, centered=(True, True, False))
        )

        # Adding main hole
        board = board.faces(">Z").workplane().pushPoints([(0,0)]).hole(hole_diameter)

        # Adding screws holes
        screws_pos = [ (0, -10.8), (0,  10.8) ]
        board = board.faces(">Z").workplane().pushPoints(screws_pos).hole(screw_holes_diameter)

        # Mask
        mask = (
            cq.Workplane("front")
                .box(width, length, enclosure_wall_thickness, centered=(True, True, False))
        )

        self.part = board
        self.mask = mask

        self.size.width     = width
        self.size.length    = length
        self.size.thickness = enclosure_wall_thickness

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = 19.4
        self.inside_footprint_offset = (0, 0)

        self.outside_footprint = (self.size.width, self.size.length)
        self.outside_footprint_thickness = 2.2

        # Front panel (very rough estimation--should normally follow the curves of the holes)
        hwx = (width / 2) + 0.2
        hlx = (length / 2) + 1.6
        points = [ (-hwx, 0), (0, -hlx), (hwx, 0), (0, hlx) ]
        diamond = (
            cq.Workplane("XY")
                .moveTo(*points[0]).lineTo(*points[1]).lineTo(*points[2]).lineTo(*points[3])
                .close()
                .extrude(self.outside_footprint_thickness)
        )
        rounded_diamond = diamond.edges("|Z").fillet(2.0)

        footprint_in = (
            cq.Workplane("front")
                .rect(*self.inside_footprint)
                .extrude(self.inside_footprint_thickness - enclosure_wall_thickness)
                .translate([0, 0, enclosure_wall_thickness])
        )
        footprint_out = rounded_diamond.translate([0, 0, -self.outside_footprint_thickness])

        self.debug_objects.footprint.inside  = footprint_in
        self.debug_objects.footprint.outside = footprint_out