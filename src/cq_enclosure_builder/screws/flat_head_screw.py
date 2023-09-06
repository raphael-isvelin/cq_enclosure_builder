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
from cq_warehouse.fastener import Screw, read_fastener_parameters_from_csv

class FlatHeadScrew(Screw):
    """
    size: str
    length: float
    fastener_type: str
        aliexpress - Flat head screws by some random sellers
    hand: Optional[Literal["right", "left"]] = "right"
    simple: Optional[bool] = True
    socket_clearance: Optional[float] = 6 * MM
    """

    # Need to copy the file to /Users/<username>/miniconda3/lib/python<python version>/site-packages/cq_warehouse/
    #   (or wherever you cq-warehouse install is.)
    fastener_data = read_fastener_parameters_from_csv("flat_head_parameters.csv")

    def head_profile(self):
        (k, dk) = (self.screw_data[p] for p in ["k", "dk"])
        profile = (
            cq.Workplane("XZ")
            .rect(dk / 2, k, centered=False)
            .wires()
        )
        return profile

    def head_plan(self) -> cq.Workplane:
        radius = self.screw_data["dk"]
        return cq.Workplane("XY").circle(radius)
    
    countersink_profile = Screw.default_countersink_profile