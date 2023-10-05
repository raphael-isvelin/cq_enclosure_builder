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

from cq_enclosure_builder.part import Part
from cq_enclosure_builder.panel import Panel

class LayoutElement:
    def __init__(
        self,
        label: str,
        part: Part,
    ):
        self.part = part
        self.label = label
        self.pos = (0, 0)
        inside = part.inside_footprint
        outside = part.outside_footprint
        self.inside_footprint = inside
        self.outside_footprint = outside
        self.total_footprint = (inside[0] if inside[0] > outside[0] else outside[0],
                                inside[1] if inside[1] > outside[1] else outside[1])
        self.total_footprint_offset = part.inside_footprint_offset  # as of now, we consider that outside offset should be at 0,0
        self.is_aligned_center_x = False
        self.is_aligned_center_y = False

    def set_inside_footprint_x(self, inside_footprint_x):
        self.inside_footprint = (inside_footprint_x, self.inside_footprint[1])
        self.total_footprint = (self.inside_footprint[0] if self.inside_footprint[0] > self.outside_footprint[0] else self.outside_footprint[0], self.total_footprint[1])

    def set_outside_footprint_x(self, outside_footprint_x):
        self.outside_footprint = (outside_footprint_x, self.outside_footprint[1])
        self.total_footprint = (self.inside_footprint[0] if self.inside_footprint[0] > self.outside_footprint[0] else self.outside_footprint[0], self.total_footprint[1])

    def set_footprints_x(self, footprint_x):
        self.inside_footprint = (footprint_x, self.inside_footprint[1])
        self.outside_footprint = (footprint_x, self.outside_footprint[1])
        self.total_footprint = (footprint_x, self.total_footprint[1])

    def set_inside_footprint_y(self, inside_footprint_y):
        self.inside_footprint = (self.inside_footprint[0], inside_footprint_y)
        self.total_footprint = (self.total_footprint[0], self.inside_footprint[1] if self.inside_footprint[1] > self.outside_footprint[1] else self.outside_footprint[1])

    def set_outside_footprint_y(self, outside_footprint_y):
        self.outside_footprint = (self.outside_footprint[0], outside_footprint_y)
        self.total_footprint = (self.total_footprint[0], self.inside_footprint[1] if self.inside_footprint[1] > self.outside_footprint[1] else self.outside_footprint[1])

    def set_footprints_y(self, footprint_y):
        self.inside_footprint = (self.inside_footprint[0], footprint_y)
        self.outside_footprint = (self.outside_footprint[0], footprint_y)
        self.total_footprint = (self.total_footprint[0], footprint_y)

    def move_to(self, pos):
        self.pos = pos
        return self

    def translate(self, pos):
        self.pos = (self.pos[0] + pos[0], self.pos[1] + pos[1])
        return self

    def get_pos(self):
        return self.pos

    def get_abs_pos(self, panel: Panel):
        width = panel.size.width
        length = panel.size.length
        return (width/2 + self.pos[0], length/2 + self.pos[1])

    def align_center_x(self):
        correct_x = self.total_footprint_offset[0]
        self.translate((-correct_x, 0))
        self.total_footprint_offset = (0, self.total_footprint_offset[1])
        self.is_aligned_center_x = True
        return self
    
    def align_center_y(self):
        correct_y = self.total_footprint_offset[1]
        self.translate((0, -correct_y))
        self.total_footprint_offset = (self.total_footprint_offset[0], 0)
        self.is_aligned_center_y = True
        return self
    
    def align_center_to_0_0(self):
        self.align_center_x()
        self.align_center_y()
        return self

    def leftmost_point_in_footprint(self, in_inside_footprint):
        return self._point_in_footprint(in_inside_footprint, 0, lambda x: -x)

    def rightmost_point_in_footprint(self, in_inside_footprint):
        return self._point_in_footprint(in_inside_footprint,  0, lambda x: x)

    def topmost_point_in_footprint(self, in_inside_footprint):
        return self._point_in_footprint(in_inside_footprint, 1, lambda x: x)

    def bottommost_point_in_footprint(self, in_inside_footprint):
        return self._point_in_footprint(in_inside_footprint, 1, lambda x: -x)

    def _point_in_footprint(self, in_inside_footprint, axis, operation):
        fp = self.inside_footprint if in_inside_footprint else self.outside_footprint
        offset = self.total_footprint_offset[axis] if in_inside_footprint else 0
        return self.pos[axis] + offset + operation(fp[axis] / 2)