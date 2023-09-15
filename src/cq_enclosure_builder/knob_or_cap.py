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

    The distance_from_enclosure_wall is simply an easy way to position the knob/cap;
        the values provided are mostly arbitrary: ideally, we should be able to find it
        dynamically using the inner_depth and whichever pot/button/encoder/etc. we're using.
    """
    def __init__(self, diameter, thickness, inner_depth, distance_from_enclosure_wall, fillet=0):
        self.diameter = diameter
        self.thickness = thickness
        self.inner_depth = inner_depth
        self.distance_from_enclosure_wall = distance_from_enclosure_wall
        self.fillet = fillet