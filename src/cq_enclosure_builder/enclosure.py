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
from cq_enclosure_builder import Part, Panel, Face

def explode(pos_array, walls_explosion_factor=2.0):
    return [x * walls_explosion_factor for x in pos_array]

class Enclosure:
    def __init__(self, inner_width, inner_length, inner_thickness, wall_thickness):
        super().__init__()

        self.frame = (
            cq.Workplane("front")
                .box(inner_width, inner_length, inner_thickness, centered=(True, True, False))
                .faces("+Z")
                .shell(wall_thickness)
                #.translate([2, 2, 2])
        )
        self.panels_specs = [
            (Face.TOP,    (inner_width,  inner_length,    wall_thickness),  [0, 0, inner_thickness],   0.9 ),
            (Face.BOTTOM, (inner_width,  inner_length,    wall_thickness),  [0, 0, 0],    0.9 ),
            (Face.FRONT,  (inner_width,  inner_thickness, wall_thickness),  [0, -(inner_length/2), inner_thickness/2], 0.9 ),
            (Face.BACK,   (inner_width,  inner_thickness, wall_thickness),  [0, inner_length/2, inner_thickness/2],  0.9 ),
            (Face.LEFT,   (inner_length, inner_thickness, wall_thickness),  [-(inner_width/2), 0, inner_thickness/2], 0.9 ),
            (Face.RIGHT,  (inner_length, inner_thickness, wall_thickness),  [inner_width/2, 0, inner_thickness/2],  0.9 ),
        ]
        self.panels = {}

        for info in self.panels_specs:
            self.panels[info[0]] = Panel(info[0], *info[1], alpha=info[3])

    def add_part_to_face(self, face: Face, part_label: str, part: Part, rel_pos=None, abs_pos=None):
        self.panels[face].add(part_label, part, rel_pos, abs_pos)
        return self

    def assemble(self, walls_explosion_factor=1.0, bottom_wall_z_shift=0.0):
        for panel in self.panels.values():
            panel.assemble()

        panels_assembly = self._build_assembly(walls_explosion_factor, bottom_wall_z_shift)
        footprints_assembly = self._build_debug_assembly([("footprint_in", "I"), ("footprint_out", "O")], walls_explosion_factor, bottom_wall_z_shift)
        holes_assembly = self._build_debug_assembly([("hole", "")], walls_explosion_factor, bottom_wall_z_shift)
        other_debug_assembly = self._build_debug_assembly([("other", "")], walls_explosion_factor, bottom_wall_z_shift)
        masks_assembly = self._build_debug_assembly([("mask", "")], walls_explosion_factor, bottom_wall_z_shift)

        self.debug = (
            cq.Assembly(None, name="Box")
                .add(footprints_assembly, name="Footprints")
                .add(holes_assembly, name="Holes")
                .add(other_debug_assembly, name="Others")
                .add(masks_assembly, name="Masks")
        )
        self.assembly = (
            cq.Assembly(None, name="Box")
                .add(panels_assembly, name="Panels")
                .add(self.debug, name="Debug")
        )
        return self

    def _get_debug(self, panel: Panel, assembly_name="combined"):
        if assembly_name in panel.debug_assemblies:
            return panel.debug_assemblies[assembly_name]
        return None

    def _build_assembly(self, walls_explosion_factor, bottom_wall_z_shift):
        a = cq.Assembly(None)
        for face, size, position, alpha in self.panels_specs:
            if face == Face.BOTTOM:
                position = (position[0], position[1], position[2] - bottom_wall_z_shift)
            panel: Panel = self.panels[face]
            translated_panel = panel.panel.translate(explode(position, walls_explosion_factor))
            a.add(translated_panel, name=face.label)
        return a

    def _build_debug_assembly(self, assemblies_specs, walls_explosion_factor, bottom_wall_z_shift):
        a = cq.Assembly(None)
        for face, size, position, alpha in self.panels_specs:
            if face == Face.BOTTOM:
                position = (position[0], position[1], position[2] - bottom_wall_z_shift)
            panel: Panel = self.panels[face]
            for assembly_type, assembly_name_suffix in assemblies_specs:
                if assembly_type == "mask":
                    translated_mask = panel.mask.translate(explode(position, walls_explosion_factor))
                    a.add(translated_mask, name=(face.label))
                else:
                    debug_assembly = self._get_debug(panel, assembly_type)
                    if debug_assembly != None:
                        translated_debug = debug_assembly.translate(explode(position, walls_explosion_factor))
                        a.add(translated_debug, name=(f"{face.label} {assembly_name_suffix}"))
        return a