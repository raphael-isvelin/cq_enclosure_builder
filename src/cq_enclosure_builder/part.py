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

import os
from typing import List, Dict, Tuple

import cadquery as cq


class AssemblyPart:
    def __init__(self, workplane: cq.Workplane, name: str, color: cq.Color):
        self.workplane: cq.Workplane = workplane
        self.name: str = name
        self.color: cq.Color = color

    def as_assembly_add_parameters(self):
        return (self.workplane, None, self.name, self.color)


class DebugObjects:
    class Footprint:
        def __init__(self):
            self.inside: cq.Workplane = None
            self.outside: cq.Workplane = None

    def __init__(self):
        # Space taken by the component (anything: PCB, bolts, caps, etc.).
        # Used for visualisation only.
        self.footprint = DebugObjects.Footprint()

        # Materialisation of the actual hole in the enclosure (e.g. a ~9.35mm extruded circle hole for a female jack).
        # Used for visualisation only.
        self.hole: cq.Workplane = None

        self.others: Dict[str, cq.Workplane] = {}


class PartSize:
    def __init__(self):
        self.width: float = 0
        self.length: float = 0
        self.thickness: float = 0


"""Base class for all parts."""
class Part:
    def __init__(
        self,
        cls_file: str = None,       # (i.e. __file__ - TODO check other way) TODO add to all parts, remove default
        part_category: str = None,  # TODO add to all parts, remove default
        part_id: str = None,        # TODO add to all parts, remove default
        detailed_step_file: str = None,
        simplified_step_file: str = None,
        ultra_simplified_step_file: str = None,
        model_offset = [0, 0, 0],
    ):
        self.cls_file = cls_file
        self.part_category = part_category
        self.part_id = part_id
        self.detailed_step_file = detailed_step_file
        self.simplified_step_file = simplified_step_file
        self.ultra_simplified_step_file = ultra_simplified_step_file
        self.model_offset = model_offset

        # To simplify, we want to design all panels in a way where the side of the panel
        #   that's supposed to be inside of the box (e.g. screw holes, ramps, etc.) is on the top,
        #   and part that we want to stick out of the box (e.g. nothing so far) is on the bottom.
        # Z=0 corresponds to the point that will be touching the box's wall from the outside:
        # -> the wall panel and cut mask should be between 0 and <enclosure_wall_thickness>.

        self.part: cq.Workplane = None
        self.mask: cq.Workplane = None

        # Used to keep sub-parts visually separated (e.g. having screws colored differently);
        # Will be used for display if present, otherwise `part` will be.
        # Even when present, `part` should still be set to
        #   `assembly_parts_to_cq_assembly(assembly_parts).toCompound()` or equivalent.
        self.assembly_parts: List[AssemblyPart] = None

        self.additional_printables: Dict[str, Tuple[float, float], cq.Workplane] = None

        self.size: PartSize = PartSize()
        self.inside_footprint: Tuple[float, float] = None  # used by the layout builder  # TODO
        self.inside_footprint_thickness: float = None
        self.inside_footprint_offset: Tuple[float, float] = None  # how far is it from 0,0

        self.outside_footprint: Tuple[float, float] = None  # used by the layout builder
        self.outside_footprint_thickness: float = None
        self.outside_footprint_offset: Tuple[float, float] = (0, 0)  # currently, it is assumed the center of the outside-facing side of the part is at 0,0

        self.debug_objects: DebugObjects = DebugObjects()


    def assembly_parts_to_cq_assembly(self) -> cq.Assembly:
        if self.assembly_parts is None:
            return None
        panel_assembly = cq.Assembly()
        for part in self.assembly_parts:
            panel_assembly.add(part.workplane, name=part.name, color=part.color)
        return panel_assembly


    def validate(self) -> List[str]:
        errors: List[str] = []

        if self.part is None: errors.append("part is None")
        if self.mask is None: errors.append("mask is None")
        if self.size.width == 0: errors.append("size.width is 0")
        if self.size.length == 0: errors.append("size.length is 0")
        if self.size.thickness == 0: errors.append("size.thickness is 0")
        if self.inside_footprint is None: errors.append("inside_footprint is None")
        if self.inside_footprint_thickness is None: errors.append("inside_footprint_thickness is None")
        if self.inside_footprint_offset is None: errors.append("inside_footprint_offset is None")
        if self.outside_footprint is None: errors.append("outside_footprint is None")
        if self.outside_footprint_thickness is None: errors.append("outside_footprint_thickness is None")
        if self.outside_footprint_offset is None: errors.append("outside_footprint_offset is None")
        if self.debug_objects.footprint.inside is None and self.debug_objects.footprint.outside is None:
            errors.append("Both debug_objects.footprint.inside and debug_objects.footprint.outside are None")

        return errors


    def get_step_model_path(self, use_simplified_model: bool, use_ultra_simplified_model: bool) -> str:
        if self.detailed_step_file is None and self.simplified_step_file is None and self.ultra_simplified_step_file is None:
            return None

        step_dir = "../src/cq_enclosure_builder/parts/" + self.part_category    # when launched from Jupyter
        if self.cls_file is not None: os.path.dirname(self.cls_file)            # regular launch

        step_file = None
        # TODO less stupid..
        if use_ultra_simplified_model:
            if self.ultra_simplified_step_file is not None: step_file = self.ultra_simplified_step_file
            elif self.simplified_step_file is not None: step_file = self.simplified_step_file
            else: step_file= self.detailed_step_file
        elif use_simplified_model:
            if self.simplified_step_file is not None: step_file = self.simplified_step_file
            elif self.ultra_simplified_step_file is not None: step_file = self.ultra_simplified_step_file
            else: step_file = self.detailed_step_file
        else:
            if self.detailed_step_file is not None: step_file = self.detailed_step_file
            elif self.simplified_step_file is not None: step_file = self.simplified_step_file
            else: step_file = self.ultra_simplified_step_file

        return os.path.join(step_dir, step_file)


    def get_step_model(self, use_simplified_model: bool, use_ultra_simplified_model: bool, extra_offset = [0,0,0]):
            model_path = self.get_step_model_path(use_simplified_model, use_ultra_simplified_model)
            return (
                cq.importers.importStep(model_path)
                    .translate(self.model_offset)
                    .translate(extra_offset)
            )