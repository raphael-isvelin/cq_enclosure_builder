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
from cq_enclosure_builder.parts.common.generic_threaded_part import GenericThreadedPart
from cq_enclosure_builder.parts_factory import register_part

@register_part("barrel_plug", "DC-022B")
class BarrelPlugDc022bPart(GenericThreadedPart):
    """
    Barrel plug connector DC-022B

    https://www.aliexpress.com/item/33026528272.html
    """

    def __init__(self, enclosure_wall_thickness):
        super().__init__(
            enclosure_wall_thickness,

            base_size=15.6,

            thread_diameter=10.7,
            thread_diameter_error_margin=0.6,

            footprint_specs=GenericThreadedPart.FootprintSpecs(
                inside_footprint_size=(15.6, 15.6),
                inside_footprint_depth=(8.1 + 5.9) - enclosure_wall_thickness,
                outside_footprint_size=(12.4, 12.4),
                outside_footprint_depth=3
            )
        )