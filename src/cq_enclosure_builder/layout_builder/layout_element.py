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

from typing import Tuple, Callable
from typing_extensions import Self

from cq_enclosure_builder.part import Part
from cq_enclosure_builder.panel import Panel

class LayoutElement:
    def __init__(
        self,
        label: str,
        part: Part = None,  # either part or total_footprint should be present
        total_footprint: Tuple[float, float] = None,  # either part or total_footprint should be present
    ):
        self.part = part
        self.label = label
        self.pos = (0, 0)
        if part is not None:
            self.inside_footprint = part.inside_footprint
            self.outside_footprint = part.outside_footprint
            self.total_footprint = (self.inside_footprint[0] if self.inside_footprint[0] > self.outside_footprint[0] else self.outside_footprint[0],
                                    self.inside_footprint[1] if self.inside_footprint[1] > self.outside_footprint[1] else self.outside_footprint[1])
            self.inside_footprint_offset = part.inside_footprint_offset
        else:
            if total_footprint is None:
                raise ValueError(f"{label}: either part or total_footprint should be present")
            self.inside_footprint = total_footprint
            self.outside_footprint = total_footprint
            self.total_footprint = total_footprint
            self.inside_footprint_offset = (0, 0)
        self.outside_footprint_offset = (0, 0)

    @staticmethod
    def spacer_x(total_footprint_x: float, label: str = "Spacer"):
        return LayoutElement(label, part=None, total_footprint=(total_footprint_x, 0))

    @staticmethod
    def spacer_y(total_footprint_y: float, label: str = "Spacer"):
        return LayoutElement(label, part=None, total_footprint=(0, total_footprint_y))

    def set_inside_footprint_x(self, inside_footprint_x: float) -> None:
        self.inside_footprint = (inside_footprint_x, self.inside_footprint[1])
        self.total_footprint = (self.inside_footprint[0] if self.inside_footprint[0] > self.outside_footprint[0] else self.outside_footprint[0], self.total_footprint[1])

    def set_outside_footprint_x(self, outside_footprint_x: float) -> None:
        self.outside_footprint = (outside_footprint_x, self.outside_footprint[1])
        self.total_footprint = (self.inside_footprint[0] if self.inside_footprint[0] > self.outside_footprint[0] else self.outside_footprint[0], self.total_footprint[1])

    def set_footprints_x(self, footprint_x: float) -> None:
        self.inside_footprint = (footprint_x, self.inside_footprint[1])
        self.outside_footprint = (footprint_x, self.outside_footprint[1])
        self.total_footprint = (footprint_x, self.total_footprint[1])

    def set_inside_footprint_y(self, inside_footprint_y: float) -> None:
        self.inside_footprint = (self.inside_footprint[0], inside_footprint_y)
        self.total_footprint = (self.total_footprint[0], self.inside_footprint[1] if self.inside_footprint[1] > self.outside_footprint[1] else self.outside_footprint[1])

    def set_outside_footprint_y(self, outside_footprint_y: float) -> None:
        self.outside_footprint = (self.outside_footprint[0], outside_footprint_y)
        self.total_footprint = (self.total_footprint[0], self.inside_footprint[1] if self.inside_footprint[1] > self.outside_footprint[1] else self.outside_footprint[1])

    def set_footprints_y(self, footprint_y: float) -> None:
        self.inside_footprint = (self.inside_footprint[0], footprint_y)
        self.outside_footprint = (self.outside_footprint[0], footprint_y)
        self.total_footprint = (self.total_footprint[0], footprint_y)

    def move_to(self, pos: Tuple[float, float]) -> Self:
        self.pos = pos
        return self

    def translate(self, pos: Tuple[float, float]) -> Self:
        self.pos = (self.pos[0] + pos[0], self.pos[1] + pos[1])
        return self

    def get_pos(self) -> Tuple[float, float]:
        return self.pos

    def get_abs_pos(self, panel: Panel) -> Tuple[float, float]:
        width = panel.size.width
        length = panel.size.length
        return (width/2 + self.pos[0], length/2 + self.pos[1])

    def leftmost_point_in_footprint(self, in_inside_footprint: bool) -> float:
        return self._point_in_footprint(in_inside_footprint, 0, lambda x: -x)

    def rightmost_point_in_footprint(self, in_inside_footprint: bool) -> float:
        return self._point_in_footprint(in_inside_footprint,  0, lambda x: x)

    def topmost_point_in_footprint(self, in_inside_footprint: bool) -> float:
        return self._point_in_footprint(in_inside_footprint, 1, lambda x: x)

    def bottommost_point_in_footprint(self, in_inside_footprint: bool) -> float:
        return self._point_in_footprint(in_inside_footprint, 1, lambda x: -x)

    def _point_in_footprint(
        self,
        in_inside_footprint: bool,
        axis: int,  # 0 for X, 1 for Y
        operation: Callable[[float], float]  # a method, either identity or reverse sign
    ) -> float:
        fp = self.inside_footprint if in_inside_footprint else self.outside_footprint
        offset = self.inside_footprint_offset[axis] if in_inside_footprint else self.outside_footprint_offset[axis]
        return self.pos[axis] + offset + operation(fp[axis] / 2)