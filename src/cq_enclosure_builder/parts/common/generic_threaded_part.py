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

class GenericThreadedPart(Part):
    class FootprintSpecs:
        def __init__(self, inside_footprint_size, inside_footprint_depth,
                     outside_footprint_size, outside_footprint_depth):
            self.inside_footprint_size = inside_footprint_size
            self.inside_footprint_depth = inside_footprint_depth
            self.outside_footprint_size = outside_footprint_size
            self.outside_footprint_depth = outside_footprint_depth

    def __init__(self, enclosure_wall_thickness, base_size,
                thread_diameter, thread_diameter_error_margin,
                footprint_specs: FootprintSpecs = None):
        super().__init__()

        thread_diameter = thread_diameter + thread_diameter_error_margin

        self.enclosure_wall_thickness = enclosure_wall_thickness
        self.base_size = base_size
        self.thread_diameter = thread_diameter
        self.thread_diameter_error_margin = thread_diameter_error_margin

        thread_hole = (
            cq.Workplane("front")
                .circle(thread_diameter/2)
                .extrude(enclosure_wall_thickness)
                #.translate([0, 0, enclosure_wall_thickness])
        )

        panel = (
            cq.Workplane("front")
                .box(base_size, base_size, enclosure_wall_thickness, centered=(True, True, False))
                .cut(thread_hole)
        )

        mask = (
            cq.Workplane("front")
                .box(base_size, base_size, enclosure_wall_thickness, centered=(True, True, False))
        )

        self.size.length    = base_size
        self.size.width     = base_size
        self.size.thickness = enclosure_wall_thickness

        self.part = panel
        self.mask = mask
        self.debug_objects.hole = thread_hole

        if footprint_specs is not None:
            self.inside_footprint = footprint_specs.inside_footprint_size
            self.outside_footprint = footprint_specs.outside_footprint_size
            self.inside_footprint_offset = (0, 0)

            footprint_in = (
                cq.Workplane("front")
                    .circle(self.inside_footprint[0]/2)
                    .extrude(footprint_specs.inside_footprint_depth)
                    .translate([0, 0, enclosure_wall_thickness])
            )
            footprint_out = (
                cq.Workplane("front")
                    .circle(self.outside_footprint[0]/2)
                    .extrude(footprint_specs.outside_footprint_depth)
                    .translate([0, 0, -footprint_specs.outside_footprint_depth])
            )
            self.debug_objects.footprint.inside  = footprint_in
            self.debug_objects.footprint.outside = footprint_out


class GenericThreadedWithStopPart(Part):
    """
    Has an additional block that prevents the threaded part from sticking too far outside.
    """
    def __init__(self, enclosure_wall_thickness, width, length,
                thread_diameter, thread_diameter_error_margin, thread_depth,
                washer_thickness, nut_thickness, margin_after_nut,
                pyramid_taper,
                dents_specs=[], dent_size_error_margin=0, dent_thickness_error_margin=0):
        super().__init__()

        thread_diameter = thread_diameter + thread_diameter_error_margin

        self.enclosure_wall_thickness = enclosure_wall_thickness
        self.width = width
        self.length = length
        self.thread_diameter = thread_diameter
        self.thread_diameter_error_margin = thread_diameter_error_margin
        self.thread_depth = thread_depth
        self.washer_thickness = washer_thickness
        self.nut_thickness = nut_thickness
        self.margin_after_nut = margin_after_nut
        self.pyramid_taper = pyramid_taper
        self.dents_specs = dents_specs
        self.dent_size_error_margin = dent_size_error_margin
        self.dent_thickness_error_margin = dent_thickness_error_margin

        smaller_side = min(width, length)
        nut_depth = washer_thickness + nut_thickness + margin_after_nut
        block_thickness = thread_depth - nut_depth - enclosure_wall_thickness
        self.smaller_side = smaller_side
        self.nut_depth = nut_depth
        self.block_thickness = block_thickness

        if block_thickness <= 0.00001:
            print("WARNING! Hole for '" + type(self).__name__ + "' won't go through the hole as enclosure_wall_thickness is too high compared to the thread length. block_thickness=" + str(block_thickness) + ". TODO add support!")

        thread_hole = (
            cq.Workplane("front")
                .circle(thread_diameter/2)
                .extrude(-(enclosure_wall_thickness + block_thickness))
                .translate([0, 0, enclosure_wall_thickness])
        )

        dents = cq.Workplane("front")
        for dent_sp in dents_specs:       
            dent_size = dent_sp[0] 
            dent_pos = dent_sp[1] 
            dent = (
                cq.Workplane("front")
                    .box(dent_size[0] + dent_size_error_margin, dent_size[1] + dent_size_error_margin, dent_size[2] + dent_thickness_error_margin, centered=(True, True, False))
                    .translate([*dent_pos, -block_thickness])
            )
            dents = dents.add(dent)

        board = (
            cq.Workplane("front")
                .box(width, length, enclosure_wall_thickness, centered=(True, True, False))
                .cut(thread_hole)
        )

        pyramid = (
            cq.Workplane("front")
                .polyline([(0, 0), (smaller_side, 0), (smaller_side, smaller_side), (0, smaller_side)])
                .close()
                .extrude(-smaller_side, taper=pyramid_taper)
                .translate([-(smaller_side/2), -(smaller_side/2), 0])
                .cut((
                    cq.Workplane("front")
                        .box(smaller_side, smaller_side, 20, centered=(True, True, False))
                        .translate([0, 0, -(20 + block_thickness)]))

                )
                .cut(thread_hole)
        )

        panel_wall = (
            cq.Workplane("front")
                .circle(thread_diameter/2 + 1)
                .extrude(-block_thickness)
                .cut(thread_hole)
        )

        if len(dents_specs) > 0:
            board = board.cut(dents)
            pyramid = pyramid.cut(dents)
            panel_wall = panel_wall.cut(dents)
            
        panel = (
            board
                .add(pyramid)
                .add(panel_wall)
        )

        mask = (
            cq.Workplane("front")
                .box(width, length, enclosure_wall_thickness, centered=(True, True, False))
        )

        self.size.length    = length
        self.size.width     = width
        self.size.thickness = enclosure_wall_thickness + block_thickness

        objects = [panel, mask, board, pyramid, panel_wall, thread_hole, dents]
        objects = list(map(self.mirror_and_translate, objects))

        panel, mask, board, pyramid, panel_wall, thread_hole, dents = objects

        self.part = panel
        self.mask = mask
        self.debug_objects.hole = thread_hole
        self.debug_objects.others["pyramid"]    = pyramid
        self.debug_objects.others["panel_wall"] = panel_wall 
        self.debug_objects.others["dents"]      = dents

    def mirror_and_translate(self, obj):
        return obj.mirror("XY").translate([0, 0, self.enclosure_wall_thickness])