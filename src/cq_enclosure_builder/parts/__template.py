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

from cq_enclosure_builder.part import Part
from cq_enclosure_builder.parts_factory import register_part

@register_part("<category>", "<part_type>")
class XxxPart(Part):
    """
    <some definition for the part>

    <link to part here>
    """
    def __init__(
        self,
        enclosure_wall_thickness: float,  # can be removed if unused
    ) -> None:
        super().__init__()

        self.part = None  # TODO (required)
        self.mask = None  # TODO (required)

        self.size.width     = None  # TODO (required)
        self.size.length    = None  # TODO (required)
        self.size.thickness = None  # TODO (required)

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = None  # TODO (required for supports)
        self.inside_footprint_offset = (0, 0)

        self.outside_footprint = (self.size.width, self.size.length)
        self.outside_footprint_thickness = None  # TODO (optional)

        self.debug_objects.footprint.inside  = None  # TODO (optional)
        self.debug_objects.footprint.outside = None  # TODO (optional)