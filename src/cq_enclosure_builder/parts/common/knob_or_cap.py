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


class KnobOrCap:
    """
    Knobs and Caps

    `inner_depth` corresponds to the depth of the hole in which the shaft of component is entering.
    """

    def __init__(
        self,
        diameter: float,
        thickness: float,
        inner_depth: float,
        fillet: float = 0
    ):
        self.diameter = diameter
        self.thickness = thickness
        self.inner_depth = inner_depth
        self.fillet = fillet