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

from typing import Dict, Union, Tuple
from typing_extensions import Self

import cadquery as cq
from cq_enclosure_builder import Face, ProjectInfo
from cq_enclosure_builder.part import Part
from cq_enclosure_builder import PanelSize


class Panel:
    def __init__(
            self,
            face: Face,
            size: PanelSize,
            color: Tuple[float, float, float] = None,
            part_color: Tuple[float, float, float] = None,
            alpha: float = 1.0,
            lid_size_error_margin: float = 0.0,  # if provided, panel will be smaller than mask
            project_info: ProjectInfo = ProjectInfo(),
            add_chamfer: bool = False,
            backpanel_size: Tuple[float, float] = None,
            backpanel_thickness: float = 0.7,
            backpanel_pos: Tuple[float, float, float] = None,
            backpanel_tapered_top: bool = True,
            backpanel_screws_pos = [],
            backpanel_screw_diameter = 2.3,
    ):
        self.face: Face = face
        self.size: PanelSize = size
        self.lid_size_error_margin: float = lid_size_error_margin
        # 'true_size' only applies if the panel is a lid (otherwise, it will just be the same as self.size)
        self.true_size: PanelSize = PanelSize(self.size.width - self.lid_size_error_margin, self.size.length - self.lid_size_error_margin, self.size.wall_thickness)
        self._color: Tuple[float, float, float] = color
        if self._color == None:
            self._color = self.face.default_color
        self._part_color: Tuple[float, float, float] = part_color
        if self._part_color == None:
            self._part_color = self.face.default_part_color
        self.panel: cq.Workplane = None
        self.mask: cq.Workplane = self._rotate_to_face(
            cq.Workplane("front")
                .workplane()
                .box(self.size.width, self.size.length, self.size.wall_thickness, centered=(True, True, False))
        )
        self.debug_assemblies: Dict[str, Union[Dict, cq.Workplane]] = {}
        self.debug_assemblies["hole"] = None
        self.debug_assemblies["footprint_in"] = None
        self.debug_assemblies["footprint_out"] = None
        self.debug_assemblies["other"] = None
        self.debug_assemblies["combined"] = cq.Assembly(None, name=self.face.label + " - Debug")
        self.project_info: ProjectInfo = project_info
        self.add_chamfer: bool = add_chamfer
        self.backpanel_size = backpanel_size
        self.backpanel_thickness = backpanel_thickness
        self.backpanel_pos = backpanel_pos
        self.backpanel_tapered_top = backpanel_tapered_top
        self.backpanel_screws_pos = backpanel_screws_pos
        self.backpanel_screw_diameter = backpanel_screw_diameter
        self.additional_printables: Dict[str, Tuple[float, float], cq.Workplane] = []
        self._alpha: float = alpha
        self._parts_to_add = []
        self._screw_counter_sunks = []

    def add(
        self,
        label: str,
        part: Part,
        rel_pos: Tuple[float, float] = None,
        abs_pos: Tuple[float, float] = None,
        color: Tuple[float, float, float] = None,
        alpha: float = 1.0,
    ) -> Self:
        print(f"[{str(self.project_info)}] {self.face.label}: adding part '{label}'")
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
            "pos": pos,
            "color": color,
            "alpha": alpha,
        })
        return self

    def add_screw_counter_sunk(self, block: cq.Workplane, mask: cq.Workplane) -> None:
        """
        Used by `Enclosure` when a screw is added; cut a countersunk hole in the panel.
        """
        self._screw_counter_sunks.append((block, mask))

    def assemble(self) -> Self:
        wall = (
            cq.Workplane("front")
                .workplane()
                .box(self.true_size.width, self.true_size.length, self.true_size.wall_thickness,
                     centered=(True, True, False))
        )
        if self.add_chamfer:
            wall = (
                wall
                    .faces("-Z").edges()
                    .chamfer(self.true_size.wall_thickness * 0.75, self.true_size.wall_thickness * 0.75 * 0.35)
            )

        backpanel = None
        backpanel_with_part_mask = None
        if self.backpanel_size is not None and self.backpanel_pos is not None:
            backpanel = self._build_backpanel()
            backpanel_with_part_mask = backpanel.translate([0,0,0])

        self.panel = cq.Assembly(None, name="Panel TOP")
        for part_to_add in self._parts_to_add:
            part_obj = part_to_add["part"]
            if part_obj.additional_printables is not None:
                self.additional_printables.extend(part_obj.additional_printables)
            self._add_part_to_debug_assemblies(part_to_add)
            translated_part_mask = part_obj.mask.translate([*part_to_add["pos"], 0])
            wall = wall.cut(translated_part_mask)
            if backpanel_with_part_mask is not None:
                backpanel_with_part_mask = backpanel_with_part_mask.cut(translated_part_mask)
            if part_obj.assembly_parts != None:
                if backpanel is not None:
                    print("WARNING - support of backpanel when assembly_parts is present hasn't been implemented yet")
                self.panel = self.panel.add(
                    self._translate_assembly_objects_and_rotate_to_face(part_obj.assembly_parts, [*part_to_add["pos"], 0]))
                    #self._rotate_assembly_to_face(part_obj.part_assembly.translate([*part_to_add["pos"], 0])))
            else:
                translated_part = part_obj.part.translate([*part_to_add["pos"], 0])
                if backpanel is not None:
                    translated_part = translated_part.cut(backpanel)
                self.panel = self.panel.add(
                    self._rotate_to_face(translated_part),
                    name=part_to_add["label"],
                    color=cq.Color(*self._part_color if part_to_add["color"] is None else part_to_add["color"], part_to_add["alpha"]),
                )
            if part_obj.size.thickness > self.size.total_thickness:
                self.size.total_thickness = part_obj.size.thickness
        for screw_cs in self._screw_counter_sunks:
            wall = wall.cut(screw_cs[1]).add(screw_cs[0])

        if backpanel is not None:
            wall = wall.cut(backpanel)
            if len(self.backpanel_screws_pos) > 0:
                wall = (
                    wall
                        .faces('front').workplane()
                        .center(self.backpanel_pos[0], self.backpanel_pos[1])
                        .pushPoints(self.backpanel_screws_pos)
                        .hole(self.backpanel_screw_diameter)
                )
                backpanel = (
                    backpanel
                        .faces('front').workplane()
                        .center(self.backpanel_pos[0], self.backpanel_pos[1])
                        .pushPoints(self.backpanel_screws_pos)
                        .hole(self.backpanel_screw_diameter)
                )
                self.additional_printables.append(("backpanel-" + str(self.face), (*self.backpanel_size, self.backpanel_thickness), backpanel_with_part_mask))

        self.wall = wall.translate([0,0,0])
        self.panelbefore = self.panel.translate([0,0,0])

        self.panel = self.panel.add(self._rotate_to_face(wall), name="Wall", color=cq.Color(*self._color, self._alpha))
        self.debug_assemblies["combined"] = self._build_combined_debug_assembly()
        self.panel_with_debug = (
            cq.Assembly(name="Panel with debug objects")
                .add(self.panel, name="Panel")
                .add(self.debug_assemblies["combined"], name="Debug")
        )
        return self

    def _build_backpanel(self):
        copper_size = self.backpanel_size
        copper_thickness = self.backpanel_thickness
        copper = cq.Workplane("front").rect(*copper_size).extrude(copper_thickness)
        if self.backpanel_tapered_top:
            copper = copper.cut(
                cq.Workplane("left")
                    .polyline([(0, 0), (copper_thickness, copper_thickness), (copper_thickness, 0)]).close()
                    .extrude(copper_size[0])
                    .translate([copper_size[0]/2, -copper_size[1]/2, 0])
            )
        copper = copper.translate(self.backpanel_pos)
        return copper

    def _rotate_to_face(self, wp) -> cq.Workplane:
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

    def _translate_assembly_objects_and_rotate_to_face(self, assembly_parts, translation) -> cq.Assembly:
        assembly = cq.Assembly()
        for assembly_part in assembly_parts:
            part, loc, name, color = assembly_part.as_assembly_add_parameters()
            part = part.translate(translation)
            part = self._rotate_to_face(part)
            assembly.add(part, name=name, color=color)
        return assembly

    def _add_part_to_debug_assemblies(self, part_to_add) -> None:
        part = part_to_add["part"]
        part_pos = part_to_add["pos"]
        part_label: str = part_to_add["label"]
        if part.debug_objects.hole != None:
            if self.debug_assemblies["hole"] == None:
                self.debug_assemblies["hole"] = cq.Assembly(name="Hole")
            hole = self._rotate_to_face(part.debug_objects.hole.translate([*part_pos, 0]))
            self.debug_assemblies["hole"] = self.debug_assemblies["hole"].add(hole, name=part_label, color=cq.Color(1, 0, 0))
        if part.debug_objects.footprint.inside != None:
            if self.debug_assemblies["footprint_in"] == None:
                self.debug_assemblies["footprint_in"] = cq.Assembly(name="Footprint IN")
            footprint_in = self._rotate_to_face(part.debug_objects.footprint.inside.translate([*part_pos, 0]))
            self.debug_assemblies["footprint_in"] = self.debug_assemblies["footprint_in"].add(footprint_in, name=part_label, color=cq.Color(1, 0, 1))
        if part.debug_objects.footprint.outside != None:
            if self.debug_assemblies["footprint_out"] == None:
                self.debug_assemblies["footprint_out"] = cq.Assembly(name="Footprint OUT")
            footprint_out = self._rotate_to_face(part.debug_objects.footprint.outside.translate([*part_pos, 0]))
            self.debug_assemblies["footprint_out"] = self.debug_assemblies["footprint_out"].add(footprint_out, name=part_label, color=cq.Color(0, 1, 1))
        other_debug_assembly = None
        for key in part.debug_objects.others.keys():
            if other_debug_assembly == None:
                other_debug_assembly = cq.Assembly()
                self.debug_assemblies["other"] = cq.Assembly()
            debug_part = self._rotate_to_face(part.debug_objects.others[key].translate([*part_pos, 0]))
            other_debug_assembly = other_debug_assembly.add(debug_part, name=key)
        if other_debug_assembly != None:
            if self.debug_assemblies["other"] == None:
                self.debug_assemblies["other"] = cq.Assembly()
            self.debug_assemblies["other"] = self.debug_assemblies["other"].add(other_debug_assembly, name=part_label, color=cq.Color(1, 1, 0))

    def _build_combined_debug_assembly(self) -> cq.Assembly:
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