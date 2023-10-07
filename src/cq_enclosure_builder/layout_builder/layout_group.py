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

import uuid
from typing import Union, List, Tuple

from cq_enclosure_builder.layout_builder.layout_element import LayoutElement
from cq_enclosure_builder.part import Part

class LayoutGroup(LayoutElement):
    def __init__(
        self,
        elements: List[LayoutElement],
        inside_footprint: Tuple[float, float],
        outside_footprint: Tuple[float, float],
        total_footprint_offset: Tuple[float, float],
        group_center_at_0_0: bool
    ):
        self.elements = elements
        self.inside_footprint = inside_footprint
        self.outside_footprint = outside_footprint
        self.total_footprint = (self.inside_footprint[0] if self.inside_footprint[0] > self.outside_footprint[0] else self.outside_footprint[0],
                                self.inside_footprint[1] if self.inside_footprint[1] > self.outside_footprint[1] else self.outside_footprint[1])
        self.total_footprint_offset = total_footprint_offset
        self.is_aligned_center_x = False
        self.is_aligned_center_y = False
        self.pos = (0, 0)
        if (isinstance(group_center_at_0_0, bool) and group_center_at_0_0) or (isinstance(group_center_at_0_0, str) and "x" in group_center_at_0_0):
            self.align_center_x()
        if (isinstance(group_center_at_0_0, bool) and group_center_at_0_0) or (isinstance(group_center_at_0_0, str) and "y" in group_center_at_0_0):
            self.align_center_y()

    def move_to(self, pos: Tuple[float, float]):
        for elem in self.elements:
            elem.move_to(pos)
        return self

    def translate(self, pos: Tuple[float, float]):
        for elem in self.elements:
            elem.translate((pos[0], pos[1]))
        self.pos = (self.pos[0] + pos[0], self.pos[1] + pos[1])
        return self

    def get_pos(self):
        return self.pos

    def get_elements(self):
        elems = []
        for elem in self.elements:
            if isinstance(elem, LayoutGroup):
                elems.extend(elem.get_elements())
            else:
                elems.append(elem)
        return elems
    
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

    @staticmethod
    def extreme_point_in_footprint(
        elements: List[LayoutElement],
        in_inside_footprint: bool,
        direction: str,  # left, right, top, or bottom
        operation  # a method, min or max
    ):
        extreme_point = -99999999 if operation == max else 99999999
        for elem in elements:
            method_name = f'{direction}most_point_in_footprint'
            point = getattr(elem, method_name)(in_inside_footprint)
            extreme_point = operation(extreme_point, point)
        return extreme_point

    @staticmethod
    def leftmost_point_in_footprints_of_elements(elements: List[LayoutElement], in_inside_footprint: bool):
        return LayoutGroup.extreme_point_in_footprint(elements, in_inside_footprint, 'left', min)

    @staticmethod
    def rightmost_point_in_footprints_of_elements(elements: List[LayoutElement], in_inside_footprint: bool):
        return LayoutGroup.extreme_point_in_footprint(elements, in_inside_footprint, 'right', max)

    @staticmethod
    def topmost_point_in_footprints_of_elements(elements: List[LayoutElement], in_inside_footprint: bool):
        return LayoutGroup.extreme_point_in_footprint(elements, in_inside_footprint, 'top', max)

    @staticmethod
    def bottommost_point_in_footprints_of_elements(elements: List[LayoutElement], in_inside_footprint: bool):
        return LayoutGroup.extreme_point_in_footprint(elements, in_inside_footprint, 'bottom', min)

    @staticmethod
    def grid_of_part(
        label: str,
        part: Part,
        rows: int,
        cols: int,
        margin_rows: float = 5,
        margin_cols: float = 5
    ):
        row_groups = []
        for i in range(0, rows):
            parts = []
            for j in range(0, cols):
                parts.append((f"{label} {i+1}-{j+1}", part))
            row_groups.append(LayoutGroup.line_of_parts(parts, margin=margin_cols, horizontal=True, group_center_at_0_0=True))
        return LayoutGroup.line_of_elements(row_groups, margin=margin_rows, horizontal=False)

    @staticmethod
    def fixed_width_line_of_elements(
        size: float,
        elements: List[LayoutElement],
        horizontal: bool = True,
        add_margin_on_sides: bool = True,
        group_center_at_0_0: bool = True,
        elements_centers_at_0_0: bool = True,
        align_to_outside_footprint: bool = False
    ):
        if len(elements) == 0:
            raise ValueError("Cannot create a line with 0 element")

        total_size_of_components = 0
        for elem in elements:
            if align_to_outside_footprint:
                total_size_of_components = total_size_of_components + (elem.outside_footprint[0] if horizontal else elem.outside_footprint[1])
            else:
                total_size_of_components = total_size_of_components + (elem.total_footprint[0] if horizontal else elem.total_footprint[1])
        total_size_needed = total_size_of_components

        
        margin = (size - total_size_needed) / (len(elements) + (2 if add_margin_on_sides else 0) - 1)

        offset_x = margin if add_margin_on_sides and horizontal else 0
        offset_y = margin if add_margin_on_sides and not horizontal else 0

        group = LayoutGroup.line_of_elements(elements, margin, horizontal,
                                             group_center_at_0_0, elements_centers_at_0_0,
                                             False, align_to_outside_footprint)

        if not group_center_at_0_0:
            group.translate((offset_x, offset_y))

        return group

    @staticmethod
    def fixed_width_line_of_parts(
        size: float,
        parts: Union[Part, Tuple[str, Part]],
        horizontal: bool = True,
        add_margin_on_sides: bool = True,
        group_center_at_0_0: bool = True,
        elements_centers_at_0_0: bool = True,
        align_to_outside_footprint: bool = False
    ):
        elements = [LayoutElement(part[0] if isinstance(part, tuple) else str(uuid.uuid4()), part[1] if isinstance(part, tuple) else part) for part in parts]
        return LayoutGroup.fixed_width_line_of_elements(size, elements, horizontal, add_margin_on_sides, group_center_at_0_0, elements_centers_at_0_0, align_to_outside_footprint)

    @staticmethod
    def line_of_elements(
        elements: List[LayoutElement],
        margin: float = 5,
        horizontal: bool =True,
        group_center_at_0_0: bool = True,
        elements_centers_at_0_0: bool = True,
        align_start_to_outside_footprint: bool = False,
        align_to_outside_footprint: bool = False
    ):
        if len(elements) == 0:
            raise ValueError("Cannot create a line with 0 element")
        if group_center_at_0_0 and align_start_to_outside_footprint:
            print("WARNING: Using both group_center_at_0_0=True and align_start_to_outside_footprint=True causes unexpected behaviours.")

        total_footprint_width = total_footprint_length = 0
        pos_in_line = 0

        initial_pos_in_line = 0
        index_of_size = 0 if horizontal else 1
        if align_start_to_outside_footprint and not align_to_outside_footprint:
            initial_pos_in_line = pos_in_line + elements[0].outside_footprint[index_of_size]/2 + elements[0].total_footprint_offset[index_of_size] - elements[0].total_footprint[index_of_size]/2
        pos_in_line = initial_pos_in_line
        for idx, e in enumerate(elements):
            if align_to_outside_footprint:
                pos_in_line = pos_in_line + e.outside_footprint[index_of_size]/2 + e.total_footprint_offset[index_of_size] + (margin if idx > 0 else 0)
            else:
                pos_in_line = pos_in_line + e.total_footprint[index_of_size]/2 + (margin if idx > 0 else 0)

            if horizontal:
                y_shift_by = 0 if elements_centers_at_0_0 else -e.total_footprint_offset[index_of_size]
                e.translate((pos_in_line - e.total_footprint_offset[index_of_size], y_shift_by))
            else:
                x_shift_by = 0 if elements_centers_at_0_0 else -e.total_footprint_offset[index_of_size]
                e.translate((x_shift_by, pos_in_line - e.total_footprint_offset[index_of_size]))

            if align_to_outside_footprint:
                pos_in_line = pos_in_line + e.outside_footprint[index_of_size]/2 - e.total_footprint_offset[index_of_size]
            else:
                pos_in_line = pos_in_line + e.total_footprint[index_of_size]/2

        inside_footprint = (
            (LayoutGroup.rightmost_point_in_footprints_of_elements(elements, True) - LayoutGroup.leftmost_point_in_footprints_of_elements(elements, True)),
            (LayoutGroup.topmost_point_in_footprints_of_elements(elements, True) - LayoutGroup.bottommost_point_in_footprints_of_elements(elements, True))
        )
        outside_footprint = (
            (LayoutGroup.rightmost_point_in_footprints_of_elements(elements, False) - LayoutGroup.leftmost_point_in_footprints_of_elements(elements, False)),
            (LayoutGroup.topmost_point_in_footprints_of_elements(elements, False) - LayoutGroup.bottommost_point_in_footprints_of_elements(elements, False))
        )

        used_fp = outside_footprint if align_to_outside_footprint else inside_footprint
        total_footprint_offset = (used_fp[0]/2 + 0*initial_pos_in_line, 0) if horizontal else (0, used_fp[1]/2 + 0*initial_pos_in_line)
        return LayoutGroup(elements, inside_footprint, outside_footprint, total_footprint_offset, group_center_at_0_0)

    @staticmethod
    def line_of_parts(
        parts: Union[Part, Tuple[str, Part]],
        margin: float = 5,
        horizontal: bool = True,
        group_center_at_0_0: bool = True,
        elements_centers_at_0_0: bool = True,
        align_start_to_outside_footprint: bool = False,
        align_to_outside_footprint: bool = False
    ):
        elements = [LayoutElement(part[0] if isinstance(part, tuple) else str(uuid.uuid4()), part[1] if isinstance(part, tuple) else part) for part in parts]
        return LayoutGroup.line_of_elements(elements, margin, horizontal, group_center_at_0_0, elements_centers_at_0_0, align_start_to_outside_footprint, align_to_outside_footprint)