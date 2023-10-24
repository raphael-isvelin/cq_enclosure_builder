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
from typing_extensions import Self

from cq_enclosure_builder.layout_builder.layout_element import LayoutElement
from cq_enclosure_builder.part import Part

class LayoutGroup(LayoutElement):
    def __init__(
        self,
        elements: List[LayoutElement],
        inside_footprint: Tuple[float, float],
        outside_footprint: Tuple[float, float],
        inside_footprint_offset: Tuple[float, float],
        outside_footprint_offset: Tuple[float, float],
    ):
        self.elements = elements
        self.inside_footprint = inside_footprint
        self.outside_footprint = outside_footprint
        self.total_footprint = (self.inside_footprint[0] if self.inside_footprint[0] > self.outside_footprint[0] else self.outside_footprint[0],
                                self.inside_footprint[1] if self.inside_footprint[1] > self.outside_footprint[1] else self.outside_footprint[1])
        self.pos = (0, 0)
        self.inside_footprint_offset = inside_footprint_offset
        self.outside_footprint_offset = outside_footprint_offset

    def move_to(self, pos: Tuple[float, float]) -> Self:
        for elem in self.elements:
            elem.move_to(pos)
        return self

    def translate(self, pos: Tuple[float, float]) -> Self:
        for elem in self.elements:
            elem.translate((pos[0], pos[1]))
        self.pos = (self.pos[0] + pos[0], self.pos[1] + pos[1])
        return self

    def get_pos(self) -> Tuple[float, float]:
        return self.pos

    def get_elements_including_with_none_part(self) -> List[LayoutElement]:
        # Using a LayoutElement with no actual part can be useful as spacer
        elems = []
        for elem in self.elements:
            if isinstance(elem, LayoutGroup):
                elems.extend(elem.get_elements())
            else:
                elems.append(elem)
        return elems

    def get_elements(self) -> List[LayoutElement]:
        elems = self.get_elements_including_with_none_part()

        # Using a LayoutElement with no actual element can be useful as spacer
        elems = [e for e in elems if e.part is not None]

        return elems

    @staticmethod
    def line_of_elements(
        elements: List[LayoutElement],
        margin: float = 5,
        horizontal: bool = True,
        align_other_dimension_at_0: bool = False,
        align_to_outside_footprint: bool = False
    ):
        if len(elements) == 0:
            raise ValueError("Cannot create a line with 0 element")

        index_of_size = 0 if horizontal else 1
        pos_in_line = 0
        for idx, e in enumerate(elements):
            if align_to_outside_footprint:
                pos_in_line = (pos_in_line
                    + e.outside_footprint[index_of_size]/2
                    + e.inside_footprint_offset[index_of_size]
                    + (margin if idx > 0 else 0)
                )
            else:
                pos_in_line = pos_in_line + e.total_footprint[index_of_size]/2 + (margin if idx > 0 else 0)

            if horizontal:
                y_shift_by = -e.inside_footprint_offset[1] if align_other_dimension_at_0 else 0
                outside_offset_or_zero = e.outside_footprint_offset[index_of_size] if align_to_outside_footprint else 0
                e.translate(
                    (
                        pos_in_line - outside_offset_or_zero - e.inside_footprint_offset[index_of_size],
                         y_shift_by
                    )
                )
            else:
                x_shift_by = -e.inside_footprint_offset[0] if align_other_dimension_at_0 else 0
                e.translate((x_shift_by, pos_in_line - e.inside_footprint_offset[index_of_size]))

            if align_to_outside_footprint:
                pos_in_line = (pos_in_line
                    + e.outside_footprint[index_of_size]/2
                    - e.inside_footprint_offset[index_of_size]
                )
            else:
                pos_in_line = pos_in_line + e.total_footprint[index_of_size]/2

        # Align centre (of outside or inside footprint) to 0,0
        translate_by = (0, 0)
        if horizontal:
            if align_to_outside_footprint:
                line_size = LayoutGroup.rightmost_point_in_footprints_of_elements(elements, False) - LayoutGroup.leftmost_point_in_footprints_of_elements(elements, False)
            else:
                line_size = LayoutGroup.rightmost_point_in_footprints_of_elements(elements, True) - LayoutGroup.leftmost_point_in_footprints_of_elements(elements, True)
            translate_by = ( -(line_size/2), 0 )
        else:
            line_size = 0
            if align_to_outside_footprint:
                line_size = LayoutGroup.topmost_point_in_footprints_of_elements(elements, False) - LayoutGroup.bottommost_point_in_footprints_of_elements(elements, False)
            else:
                line_size = LayoutGroup.topmost_point_in_footprints_of_elements(elements, True) - LayoutGroup.bottommost_point_in_footprints_of_elements(elements, True)
            translate_by = ( 0, -(line_size/2) )
        for idx, e in enumerate(elements):
            e.translate(translate_by)

        inside_footprint = (
            (LayoutGroup.rightmost_point_in_footprints_of_elements(elements, True) - LayoutGroup.leftmost_point_in_footprints_of_elements(elements, True)),
            (LayoutGroup.topmost_point_in_footprints_of_elements(elements, True) - LayoutGroup.bottommost_point_in_footprints_of_elements(elements, True))
        )
        outside_footprint = (
            (LayoutGroup.rightmost_point_in_footprints_of_elements(elements, False) - LayoutGroup.leftmost_point_in_footprints_of_elements(elements, False)),
            (LayoutGroup.topmost_point_in_footprints_of_elements(elements, False) - LayoutGroup.bottommost_point_in_footprints_of_elements(elements, False))
        )

        inside_footprint_offset = (
            (LayoutGroup.rightmost_point_in_footprints_of_elements(elements, True) + LayoutGroup.leftmost_point_in_footprints_of_elements(elements, True)) / 2,
            (LayoutGroup.topmost_point_in_footprints_of_elements(elements, True) + LayoutGroup.bottommost_point_in_footprints_of_elements(elements, True)) / 2
        )
        outside_footprint_offset = (
            (LayoutGroup.rightmost_point_in_footprints_of_elements(elements, False) + LayoutGroup.leftmost_point_in_footprints_of_elements(elements, False)) / 2,
            (LayoutGroup.topmost_point_in_footprints_of_elements(elements, False) + LayoutGroup.bottommost_point_in_footprints_of_elements(elements, False)) / 2
        )

        return LayoutGroup(elements, inside_footprint, outside_footprint, inside_footprint_offset, outside_footprint_offset)

    @staticmethod
    def line_of_parts(
        parts: Union[Part, Tuple[str, Part]],
        margin: float = 5,
        horizontal: bool = True,
        align_other_dimension_at_0: bool = True,
        align_to_outside_footprint: bool = False
    ):
        elements = [LayoutElement(part[0] if isinstance(part, tuple) else str(uuid.uuid4()), part[1] if isinstance(part, tuple) else part) for part in parts]
        return LayoutGroup.line_of_elements(elements, margin, horizontal, align_other_dimension_at_0, align_to_outside_footprint)

    @staticmethod
    def fixed_width_line_of_elements(
        size: float,
        elements: List[LayoutElement],
        horizontal: bool = True,
        add_margin_on_sides: bool = True,
        align_other_dimension_at_0: bool = True,
        align_to_outside_footprint: bool = False
    ):
        if len(elements) == 0:
            raise ValueError("Cannot create a line with 0 element")

        total_size_of_components = 0
        for elem in elements:
            if align_to_outside_footprint:
                total_size_of_components = (
                    total_size_of_components
                    + (elem.outside_footprint[0] if horizontal else elem.outside_footprint[1])
                )
            else:
                total_size_of_components = total_size_of_components + (elem.total_footprint[0] if horizontal else elem.total_footprint[1])
        total_size_needed = total_size_of_components
        
        margin = (size - total_size_needed) / (len(elements) + (2 if add_margin_on_sides else 0) - 1)

        return LayoutGroup.line_of_elements(
            elements, margin, horizontal, align_other_dimension_at_0, align_to_outside_footprint)

    @staticmethod
    def fixed_width_line_of_parts(
        size: float,
        parts: Union[Part, Tuple[str, Part]],
        horizontal: bool = True,
        add_margin_on_sides: bool = True,
        align_other_dimension_at_0: bool = True,
        align_to_outside_footprint: bool = False
    ):
        elements = [LayoutElement(part[0] if isinstance(part, tuple) else str(uuid.uuid4()), part[1] if isinstance(part, tuple) else part) for part in parts]
        return LayoutGroup.fixed_width_line_of_elements(
            size, elements, horizontal, add_margin_on_sides, align_other_dimension_at_0, align_to_outside_footprint)

    @staticmethod
    def grid_of_part(
        label: str,
        part: Part,
        rows: int,
        cols: int,
        margin_rows: float = 0,
        margin_cols: float = 0,
    ):
        row_groups = []
        for i in range(0, rows):
            parts = []
            for j in range(0, cols):
                parts.append((f"{label} {i+1}-{j+1}", part))
            row_groups.append(LayoutGroup.line_of_parts(parts, margin=margin_cols, horizontal=True))
        return LayoutGroup.line_of_elements(row_groups, margin=margin_rows, horizontal=False)

    @staticmethod
    def extreme_point_in_footprints_of_elements(
        elements: List[LayoutElement],
        in_inside_footprint: bool,
        direction: str,  # left, right, top, or bottom
        operation  # a method, min or max
    ) -> float:
        extreme_point = -99999999 if operation == max else 99999999
        for elem in elements:
            method_name = f'{direction}most_point_in_footprint'
            point = getattr(elem, method_name)(in_inside_footprint)
            extreme_point = operation(extreme_point, point)
        return extreme_point

    @staticmethod
    def leftmost_point_in_footprints_of_elements(elements: List[LayoutElement], in_inside_footprint: bool) -> float:
        return LayoutGroup.extreme_point_in_footprints_of_elements(elements, in_inside_footprint, 'left', min)

    @staticmethod
    def rightmost_point_in_footprints_of_elements(elements: List[LayoutElement], in_inside_footprint: bool) -> float:
        return LayoutGroup.extreme_point_in_footprints_of_elements(elements, in_inside_footprint, 'right', max)

    @staticmethod
    def topmost_point_in_footprints_of_elements(elements: List[LayoutElement], in_inside_footprint: bool) -> float:
        return LayoutGroup.extreme_point_in_footprints_of_elements(elements, in_inside_footprint, 'top', max)

    @staticmethod
    def bottommost_point_in_footprints_of_elements(elements: List[LayoutElement], in_inside_footprint: bool) -> float:
        return LayoutGroup.extreme_point_in_footprints_of_elements(elements, in_inside_footprint, 'bottom', min)