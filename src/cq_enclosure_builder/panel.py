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
from cq_enclosure_builder import Face
from cq_enclosure_builder.part import Part

class PanelSize:
    def __init__(self, width, length, wall_thickness, total_thickness):
        self.width = width
        self.length = length
        self.wall_thickness = wall_thickness
        self.total_thickness = total_thickness

class Panel:
    def __init__(self,
                 face: Face,
                 top_view_width,
                 top_view_length,
                 wall_thickness,
                 color=None,
                 part_color=None,
                 alpha=1.0,
                 lid_size_error_margin=0.0  # if provided, panel will be smaller than mask
        ):
        self.face = face
        self.size = PanelSize(top_view_width, top_view_length, wall_thickness, wall_thickness)
        self._color = color
        if self._color == None:
            self._color = self.face.default_color
        self._part_color = part_color
        if self._part_color == None:
            self._part_color = self.face.default_part_color
        self.panel = None
        self.mask = self._rotate_to_face(
            cq.Workplane("front")
                .workplane()
                .box(top_view_width, top_view_length, wall_thickness, centered=(True, True, False))
        )
        self.debug_assemblies = {}
        self.debug_assemblies["hole"] = None
        self.debug_assemblies["footprint_in"] = None
        self.debug_assemblies["footprint_out"] = None
        self.debug_assemblies["other"] = None
        self.debug_assemblies["combined"] = cq.Assembly(None, name=self.face.label + " - Debug")
        self.lid_size_error_margin = lid_size_error_margin
        self._alpha = alpha
        self._parts_to_add = []

    def add(self, label: str, part: Part, rel_pos=None, abs_pos=None):
        print(self.face.label + ": adding part '" + label + "'")
        pos = None
        if rel_pos == None and abs_pos == None:
            raise ValueError("Either rel_pos or abs_pos must be set.")
        elif rel_pos == None:
            pos = (
                abs_pos[0] - self.size.width/2,
                abs_pos[1] - self.size.length/2
            )
        elif abs_pos==None:
            pos = rel_pos
        self._parts_to_add.append({
            "part": part,
            "label": label,
            "pos": pos
        })
        return self

    def assemble(self):
        wall = (
            cq.Workplane("front")
                .workplane()
                .box(self.size.width - self.lid_size_error_margin, self.size.length - self.lid_size_error_margin, self.size.wall_thickness,
                     centered=(True, True, False))
        )
        self.panel = cq.Assembly(None, name="Panel TOP")
        for part_to_add in self._parts_to_add:
            part_obj = part_to_add["part"]
            self._add_part_to_debug_assemblies(part_to_add)
            wall = wall.cut(
                part_obj.mask.translate([*part_to_add["pos"], 0])
            )
            if part_obj.assembly_parts != None:
                self.panel = self.panel.add(
                    self._translate_assembly_objects_and_rotate_to_face(part_obj.assembly_parts, [*part_to_add["pos"], 0]))
                    #self._rotate_assembly_to_face(part_obj.part_assembly.translate([*part_to_add["pos"], 0])))
            else:
                self.panel = self.panel.add(
                    self._rotate_to_face(
                        part_obj.part.translate([*part_to_add["pos"], 0])),
                    name=part_to_add["label"],
                    color=cq.Color(*self._part_color, 1.0)
                )
            if part_obj.size.thickness > self.size.total_thickness:
                self.size.total_thickness = part_obj.size.thickness
        self.panel = self.panel.add(self._rotate_to_face(wall), name="Wall", color=cq.Color(*self._color, self._alpha))
        self.debug_assemblies["combined"] = self._build_combined_debug_assembly()
        return self

    def _rotate_to_face(self, wp):
        if self.face == Face.TOP:
            wp = wp.mirror("XY")
        elif self.face == Face.BOTTOM:
            wp = wp.mirror("XZ")
        elif self.face == Face.BACK:
            wp = wp.rotate((0, 0, 0), (1, 0, 0), 90)
            wp = wp.mirror("YZ")
        elif self.face == Face.FRONT:
            wp = wp.rotate((0, 0, 0), (1, 0, 0), 90)
            wp = wp.mirror("XZ")
        elif self.face == Face.LEFT:
            wp = wp.rotate((0, 0, 0), (1, 0, 0), 90)
            wp = wp.rotate((0, 0, 0), (0, 0, 1), 90)
            wp = wp.mirror("XZ")
        elif self.face == Face.RIGHT:
            wp = wp.rotate((0, 0, 0), (1, 0, 0), 90)
            wp = wp.rotate((0, 0, 0), (0, 0, 1), -90)
            wp = wp.mirror("XZ")
        return wp

    def _translate_assembly_objects_and_rotate_to_face(self, assembly_parts, translation):
        assembly = cq.Assembly()
        for assembly_part in assembly_parts:
            part, loc, name, color = assembly_part.as_assembly_add_parameters()
            part = part.translate(translation)
            part = self._rotate_to_face(part)
            assembly.add(part, name=name, color=color)
        return assembly

    def _add_part_to_debug_assemblies(self, part_to_add):
        part = part_to_add["part"]
        part_pos = part_to_add["pos"]
        part_label: str = part_to_add["label"]
        if part.debug_objects.hole != None:
            if self.debug_assemblies["hole"] == None:
                self.debug_assemblies["hole"] = cq.Assembly()
            hole = self._rotate_to_face(part.debug_objects.hole.translate([*part_pos, 0]))
            self.debug_assemblies["hole"] = self.debug_assemblies["hole"].add(hole, name=part_label, color=cq.Color(1, 0, 0))
        if part.debug_objects.footprint.inside != None:
            if self.debug_assemblies["footprint_in"] == None:
                self.debug_assemblies["footprint_in"] = cq.Assembly()
            footprint_in = self._rotate_to_face(part.debug_objects.footprint.inside.translate([*part_pos, 0]))
            self.debug_assemblies["footprint_in"] = self.debug_assemblies["footprint_in"].add(footprint_in, name=part_label, color=cq.Color(1, 0, 1))
        if part.debug_objects.footprint.outside != None:
            if self.debug_assemblies["footprint_out"] == None:
                self.debug_assemblies["footprint_out"] = cq.Assembly()
            footprint_out = self._rotate_to_face(part.debug_objects.footprint.outside.translate([*part_pos, 0]))
            self.debug_assemblies["footprint_out"] = self.debug_assemblies["footprint_out"].add(footprint_out, name=part_label, color=cq.Color(0, 1, 1))
        other_debug_assembly = None
        for key in part.debug_objects.others.keys():
            if other_debug_assembly == None:
                other_debug_assembly = cq.Assembly(None)
                self.debug_assemblies["other"] = cq.Assembly()
            debug_part = self._rotate_to_face(part.debug_objects.others[key].translate([*part_pos, 0]))
            other_debug_assembly = other_debug_assembly.add(debug_part, name=key)
        if other_debug_assembly != None:
            if self.debug_assemblies["other"] == None:
                self.debug_assemblies["other"] = cq.Assembly()
            self.debug_assemblies["other"] = self.debug_assemblies["other"].add(other_debug_assembly, name=part_label, color=cq.Color(1, 1, 0))

    def _build_combined_debug_assembly(self):
        combined = self.debug_assemblies["combined"]
        combined = combined.add(self.mask, name="Mask", color=cq.Color(0, 1, 0, 0.5))
        if self.debug_assemblies["hole"] != None:
            combined = combined.add(self.debug_assemblies["hole"], name="Holes")
        if self.debug_assemblies["footprint_in"] != None:
            combined = combined.add(self.debug_assemblies["footprint_in"], name="Footprint in")
        if self.debug_assemblies["footprint_out"] != None:
            combined = combined.add(self.debug_assemblies["footprint_out"], name="Footprint out")
        if self.debug_assemblies["other"] != None:
            combined = combined.add(self.debug_assemblies["other"], name="Other")
        return combined
