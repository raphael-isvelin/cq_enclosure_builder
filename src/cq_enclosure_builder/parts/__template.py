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

@register_part("CAT", "TYPE")
class XxxPart(Part):
    """
    SOME_DEFINITION

    LINK_HERE
    """

    def __init__(self, width: int, height: int, thickness: int, test = None) -> None:
        pass