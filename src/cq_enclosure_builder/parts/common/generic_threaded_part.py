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


class GenericThreadedPart(Part):
    class FootprintSpecs:
        def __init__(
            self,
            inside_footprint_size: Tuple[float, float],
            inside_footprint_depth: float,
            outside_footprint_size: Tuple[float, float],
            outside_footprint_depth: float,
        ):
            self.inside_footprint_size = inside_footprint_size
            self.inside_footprint_depth = inside_footprint_depth
            self.outside_footprint_size = outside_footprint_size
            self.outside_footprint_depth = outside_footprint_depth

    def __init__(
        self,
        enclosure_wall_thickness: float,
        base_size: float,
        thread_diameter: float,
        thread_diameter_error_margin: float,
        footprint_specs: FootprintSpecs = None,
    ):
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
            self.inside_footprint_offset = (0, 0)
            self.inside_footprint_thickness = footprint_specs.inside_footprint_depth

            # TODO we want to add the nut [and washer], as well as in the debug object (esp. important if no cap)
            self.outside_footprint = footprint_specs.outside_footprint_size
            self.outside_footprint_thickness = footprint_specs.outside_footprint_depth

            footprint_in = (
                cq.Workplane("front")
                    .circle(self.inside_footprint[0]/2)
                    .extrude(self.inside_footprint_thickness)
                    .translate([0, 0, enclosure_wall_thickness])
            )
            footprint_out = (
                cq.Workplane("front")
                    .circle(self.outside_footprint[0]/2)
                    .extrude(self.outside_footprint_thickness)
                    .translate([0, 0, -self.outside_footprint_thickness])
            )
            self.debug_objects.footprint.inside  = footprint_in
            self.debug_objects.footprint.outside = footprint_out


class GenericThreadedWithStopPart(Part):
    """
    Has an additional block that prevents the threaded part from sticking too far outside.
    """
    def __init__(
        self,
        enclosure_wall_thickness: float,
        width: float,
        length: float,
        thread_diameter: float,
        thread_diameter_error_margin: float,
        thread_depth: float,
        washer_thickness: float,
        nut_thickness: float,
        margin_after_nut: float,
        pyramid_taper: float,
        dents_specs: Tuple[Tuple[float, float], Tuple[float, float]] = [],
        dent_size_error_margin: float = 0,
        dent_thickness_error_margin: float = 0
    ):
        super().__init__()

        thread_diameter = thread_diameter + thread_diameter_error_margin

        self.enclosure_wall_thickness: float = enclosure_wall_thickness
        self.width: float = width
        self.length: float = length
        self.thread_diameter: float = thread_diameter
        self.thread_diameter_error_margin: float = thread_diameter_error_margin
        self.thread_depth: float = thread_depth
        self.washer_thickness: float = washer_thickness
        self.nut_thickness: float = nut_thickness
        self.margin_after_nut: float = margin_after_nut
        self.pyramid_taper: float = pyramid_taper
        self.dents_specs: Tuple[Tuple[float, float], Tuple[float, float]] = dents_specs
        self.dent_size_error_margin: float = dent_size_error_margin
        self.dent_thickness_error_margin: float = dent_thickness_error_margin

        smaller_side = min(width, length)
        nut_depth = washer_thickness + nut_thickness + margin_after_nut
        required_distance_to_inner_wall = thread_depth - nut_depth - 0.01
        block_thickness = max(0, required_distance_to_inner_wall - enclosure_wall_thickness)
        self.smaller_side: float = smaller_side
        self.nut_depth: float = nut_depth
        self.block_thickness: float = block_thickness
        extrude_block = enclosure_wall_thickness < required_distance_to_inner_wall
        self.actual_wall_thickness = enclosure_wall_thickness if extrude_block else required_distance_to_inner_wall
        board_offset = enclosure_wall_thickness - self.actual_wall_thickness

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
                    .translate([*dent_pos, 0])
            )
            dent = dent.translate([0, 0, -block_thickness if extrude_block else (enclosure_wall_thickness - required_distance_to_inner_wall)])
            dents = dents.add(dent)

        panel = (
            cq.Workplane("front")
                .box(width, length, self.actual_wall_thickness, centered=(True, True, False))
                .translate([0, 0, board_offset])
                .cut(thread_hole)
        )

        if extrude_block:
            base_pyramid: cq.Workplane = (
                cq.Workplane("front")
                    .polyline([(0, 0), (smaller_side, 0), (smaller_side, smaller_side), (0, smaller_side)])
                    .close()
                    .extrude(-smaller_side, taper=pyramid_taper)
                    .translate([-(smaller_side/2), -(smaller_side/2), 0])
            )
            pyramid_cut_box = (
                cq.Workplane("front")
                    .box(smaller_side, smaller_side, 20, centered=(True, True, False))
                    .translate([0, 0, -(20 + block_thickness)])
            )
            self.pyramid = (
                base_pyramid
                    .cut(pyramid_cut_box)
                    .cut(thread_hole)
            )

        # panel_wall = (
        #     cq.Workplane("front")
        #         .circle(thread_diameter/2 + 1)
        #         .extrude(-block_thickness)
        #         .cut(thread_hole)
        # )
        panel_wall = cq.Workplane("front")
        if len(dents_specs) > 0:
            panel = panel.cut(dents)
            if extrude_block:
                self.pyramid = self.pyramid.cut(dents)
                panel_wall = (
                    panel_wall
                        .circle(thread_diameter/2 + 1)
                        .extrude(-block_thickness)
                        .cut(thread_hole)
                )
                panel_wall = panel_wall.cut(dents)
                panel = panel.add(panel_wall)

        if extrude_block:
            panel.add(self.pyramid)

        mask = (
            cq.Workplane("front")
                .box(width, length, enclosure_wall_thickness, centered=(True, True, False))
        )

        self.size.length    = length
        self.size.width     = width
        self.size.thickness = enclosure_wall_thickness + block_thickness

        objects = [panel, mask, thread_hole]
        if extrude_block:
            self.pyramid = self.mirror_and_translate(self.pyramid)
            panel_wall = self.mirror_and_translate(panel_wall)
        objects = list(map(self.mirror_and_translate, objects))
        panel, mask, thread_hole = objects

        self.part = panel
        self.mask = mask
        self.dents = dents
        self.debug_objects.hole = thread_hole

    def mirror_and_translate(self, obj):
        return obj.mirror("XY").translate([0, 0, self.enclosure_wall_thickness])