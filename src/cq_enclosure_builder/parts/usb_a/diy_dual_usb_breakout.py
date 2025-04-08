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

from cq_enclosure_builder.part import Part
from cq_enclosure_builder.parts_factory import register_part


PART_CATEGORY = "usb_a"
PART_ID = "DIY_Dual_USB"

"""
Custom dual USB breakout

TODO link to KiCad
"""
@register_part(PART_CATEGORY, PART_ID)
class DiyDualUsbBreakoutPart(Part):

    BOARD_SIZE_XY = (24.2, 30)

    # Blocks & screws
    BLOCK_THICKNESS = 5
    BLOCKS_SPECS = [
        ( [0, BOARD_SIZE_XY[1]/2-3.5],   (BOARD_SIZE_XY[0], 7) ),
        ( [0, -BOARD_SIZE_XY[1]/2+3.5],  (BOARD_SIZE_XY[0], 7) ),
        ( [BOARD_SIZE_XY[0]/2-1.5, 0],   (3, BOARD_SIZE_XY[1]) ),
        ( [-BOARD_SIZE_XY[0]/2+1.5, 0],  (3, BOARD_SIZE_XY[1]) ),
    ]
    SCREW_DISTANCE = 9 * 2.54
    SCREWS_POSITIONS = [ (-2.54*2, SCREW_DISTANCE/2), (0, -SCREW_DISTANCE/2) ]
    SCREW_HOLE_SIZE = 2.9

    # USB
    USB_HOLE_SIZE = (14.3, 13.3)
    USB_HOLE_CLEARANCE = (0.4, 0.4)
    USB_THICKNESS_AFTER_PCB = 14

    def __init__(
        self,
        enclosure_wall_thickness: float,
    ):
        try: cls_file = __file__            # regular launch
        except NameError: cls_file = None   # when launched from Jupyter
        super().__init__(
            cls_file,
            PART_CATEGORY,
            PART_ID,
        )

        block_thickness = DiyDualUsbBreakoutPart.BLOCK_THICKNESS

        calculated_block_thickness = DiyDualUsbBreakoutPart.USB_THICKNESS_AFTER_PCB - enclosure_wall_thickness
        block_spacer_thickness = calculated_block_thickness - block_thickness

        board_size = (
            DiyDualUsbBreakoutPart.BOARD_SIZE_XY[0],
            DiyDualUsbBreakoutPart.BOARD_SIZE_XY[1] + DiyDualUsbBreakoutPart.BLOCK_THICKNESS,
            enclosure_wall_thickness
        )
        self.size.width, self.size.length, self.size.thickness = board_size

        # Board & mask
        self.part = (
            cq.Workplane("front")
                .box(*board_size, centered=(True, True, False))

                .faces(">Z").workplane()
            .move(0, block_thickness/2)
                .rect(DiyDualUsbBreakoutPart.USB_HOLE_SIZE[0], DiyDualUsbBreakoutPart.USB_HOLE_SIZE[1])
                .cutThruAll()

                .add(self.build_blocks(enclosure_wall_thickness, DiyDualUsbBreakoutPart.BLOCKS_SPECS, block_thickness, DiyDualUsbBreakoutPart.SCREW_HOLE_SIZE).translate([0, block_thickness/2, 0]))
                .add(self.build_wedge(enclosure_wall_thickness, block_thickness).translate([0, block_thickness/2, 0]))
        )
        self.mask = (
            cq.Workplane("front")
                .box(*board_size, centered=(True, True, False))
        )

        # Spacer
        print("DIY dual USB: built required " + str(block_spacer_thickness) + "mm spacer (calculated " + str(calculated_block_thickness) + ", block_thicknes " + str(block_thickness) + ")")
        self.spacer = self.build_blocks(enclosure_wall_thickness, DiyDualUsbBreakoutPart.BLOCKS_SPECS, block_spacer_thickness, DiyDualUsbBreakoutPart.SCREW_HOLE_SIZE+0.8, block_spacer_thickness).translate([0, 0, -enclosure_wall_thickness])
      
        self.debug_objects.others["spacer"]  = (
            self.spacer
                .translate([0, block_thickness/2, block_thickness + enclosure_wall_thickness])
        )

        # Inside footprint
        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = 16.8 - enclosure_wall_thickness
        self.inside_footprint_offset = (0, 0)
        
        footprint_in = (
            cq.Workplane("front")
                .box(*self.inside_footprint, self.inside_footprint_thickness, centered=(True, True, False))
                .translate([0, 0, enclosure_wall_thickness])
        )
        self.debug_objects.footprint.inside  = footprint_in

        # Outside footprint
        self.outside_footprint = DiyDualUsbBreakoutPart.USB_HOLE_SIZE
        self.outside_footprint_thickness = 1
        self.outside_footprint_offset = (0, block_thickness/2)

        
        self.debug_objects.footprint.outside = (
            cq.Workplane("front")
                .box(*self.outside_footprint, 1, centered=(True, True, False))
                .translate([*self.outside_footprint_offset, -1])
        )

    def build_blocks(self, enclosure_wall_thickness: float, blocks_specs, block_thickness: float, screw_hole_size: float, screw_hole_depth = None):
        blocks = cq.Workplane("front")
        for specs in blocks_specs:
            pos, sz = specs
            blocks.add(
                cq.Workplane("front")
                    # .faces("<Z").workplane()
                    .move(*pos)
                    .rect(*sz)
                    .extrude(block_thickness)
                    .translate([0, 0, enclosure_wall_thickness])
            )
        if screw_hole_depth is None:
            screw_hole_depth = min(10, block_thickness-1)
        blocks = (
            blocks
                .faces(">Z").workplane()
                .pushPoints(DiyDualUsbBreakoutPart.SCREWS_POSITIONS)
                .hole(screw_hole_size, screw_hole_depth)
        )
        return blocks

    def build_wedge(self, enclosure_wall_thickness: float, block_thickness: float):
        return (
            cq.Workplane("right")
                .polyline([ (0, 0), (-block_thickness, 0), (0, -block_thickness) ])
                .close()
                .extrude(DiyDualUsbBreakoutPart.BOARD_SIZE_XY[0])
                .translate([-DiyDualUsbBreakoutPart.BOARD_SIZE_XY[0]/2, -DiyDualUsbBreakoutPart.BOARD_SIZE_XY[1]/2, enclosure_wall_thickness])
        )