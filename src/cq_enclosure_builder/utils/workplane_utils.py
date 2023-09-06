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
from typing import Optional

def scale(workplane: cq.Workplane, x: float, y: Optional[float] = None, z: Optional[float] = None) -> cq.Workplane:
    y = y if y is not None else x
    z = z if z is not None else x
    t = cq.Matrix([
        [x, 0, 0, 0],
        [0, y, 0, 0],
        [0, 0, z, 0],
        [0, 0, 0, 1]
    ])
    return workplane.newObject([
        o.transformGeometry(t) if isinstance(o, cq.Shape) else o
        for o in workplane.objects
    ])