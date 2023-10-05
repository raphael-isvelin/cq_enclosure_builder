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
from typing import List

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
        self.hole = None

        self.others = {}

class PartSize:
    def __init__(self):
        self.width: float = 0
        self.length: float = 0
        self.thickness: float = 0

class Part:
    """Base class for all parts."""

    def __init__(self):
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

        self.additional_printables = None

        self.size = PartSize()
        self.inside_footprint = None  # used by the layout builder  # TODO
        self.inside_footprint_thickness = None
        self.inside_footprint_offset = None  # how far is it from 0,0
        self.outside_footprint = None  # used by the layout builder
        self.outside_footprint_thickness = None
        self.outside_footprint_offset = (0, 0)  # currently, it is assumed the center of the outside-facing side of the part is at 0,0

        self.debug_objects = DebugObjects()

    def assembly_parts_to_cq_assembly(self):
        if self.assembly_parts is None:
            return None
        panel_assembly = cq.Assembly()
        for part in self.assembly_parts:
            panel_assembly.add(part.workplane, name=part.name, color=part.color)
        return panel_assembly

    def show(self):  # TODO delete
        print("debug show() part " + self.__class__.__name__ + " - TODO delete")

    def validate(self):
        print("VALIDATING CLASS: " + self.__class__.__name__)
