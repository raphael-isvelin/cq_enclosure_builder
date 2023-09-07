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

from cq_enclosure_builder.constants import DEFAULT_PART_COLOR

class Face:
    class FaceInfo:
        def __init__(self, label, default_color, default_part_color):
            self.label = label
            self.default_color = default_color
            self.default_part_color = default_part_color

    TOP =    FaceInfo("TOP",    (87/255, 117/255, 144/255), DEFAULT_PART_COLOR)
    BOTTOM = FaceInfo("BOTTOM", (39/255, 125/255, 161/255), DEFAULT_PART_COLOR)
    FRONT =  FaceInfo("FRONT",  (67/255, 170/255, 139/255), DEFAULT_PART_COLOR)
    BACK =   FaceInfo("BACK",   (144/255, 190/255, 109/255), DEFAULT_PART_COLOR)
    LEFT =   FaceInfo("LEFT",   (249/255, 132/255, 74/255), DEFAULT_PART_COLOR)
    RIGHT =  FaceInfo("RIGHT",  (249/255, 199/255, 79/255), DEFAULT_PART_COLOR)