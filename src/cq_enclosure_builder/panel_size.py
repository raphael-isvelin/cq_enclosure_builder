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

class PanelSize:
    def __init__(
        self,
        width: float,
        length: float,
        wall_thickness: float,
        total_thickness: float = None  # default: wall_thickness
    ):
        self.width = width
        self.length = length
        self.wall_thickness = wall_thickness
        self.total_thickness = total_thickness
        if self.total_thickness is None:
            self.total_thickness = self.wall_thickness