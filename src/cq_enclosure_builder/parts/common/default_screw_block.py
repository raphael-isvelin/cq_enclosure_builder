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
import cq_warehouse.extensions
from cq_enclosure_builder.screws.flat_head_screw import FlatHeadScrew

class DefaultScrewBlock:
    # Hardcoded to one specific Screw class; will refactor when the need comes.
    SCREW_CLASS = FlatHeadScrew
    SCREW_MODEL_NAME = "aliexpress"
    SCREW_SIZE_REFERENCES = {
        "m1": "M1.4-0.3",
        "m2": "M2-0.4",
        "m3": "M3-0.5",
        "m4": "M4-0.7",
        "m5": "M5-0.8",
    }
    BLOCK_SIZES = {
        "m1": ( 5,  5),
        "m2": ( 6,  6),
        "m3": ( 8,  8),
        "m4": (10, 10),
        "m5": (12, 12),
    }

    DEFAULT_FIT = "Loose"
    DEFAULT_COUNTER_SUNK = False
    DEFAULT_SCREW_HOLE_DEPTH = None  # None -> fully go through
    
    @staticmethod
    def generic_screw(screw_size, block_thickness, screw_hole_depth, counter_sunk, fit):
        screw_size_reference = DefaultScrewBlock.SCREW_SIZE_REFERENCES[screw_size]
        fastener = DefaultScrewBlock.SCREW_CLASS(size=screw_size_reference, fastener_type=DefaultScrewBlock.SCREW_MODEL_NAME, length=20)

        block_size = (*DefaultScrewBlock.BLOCK_SIZES[screw_size], block_thickness)
        if screw_hole_depth == None:
            screw_hole_depth = block_size[2]

        screw_block = (
            cq.Workplane("XY")
                .box(*block_size, centered=(True, True, False))
                .faces(">Z").workplane().pushPoints([(0,0)])
                .threadedHole(fastener=fastener, depth=screw_hole_depth, fit=fit, counterSunk=counter_sunk)
        )
        mask = cq.Workplane("XY").box(*block_size, centered=(True, True, False))
        return {
            "block": screw_block,
            "mask": mask,
            "size": block_size
        }

    @staticmethod
    def m1(block_thickness, screw_hole_depth=DEFAULT_SCREW_HOLE_DEPTH, counter_sunk=DEFAULT_COUNTER_SUNK, fit=DEFAULT_FIT):
        return DefaultScrewBlock.generic_screw("m1", block_thickness, screw_hole_depth, counter_sunk, fit)

    @staticmethod
    def m2(block_thickness, screw_hole_depth=DEFAULT_SCREW_HOLE_DEPTH, counter_sunk=DEFAULT_COUNTER_SUNK, fit=DEFAULT_FIT):
        return DefaultScrewBlock.generic_screw("m2", block_thickness, screw_hole_depth, counter_sunk, fit)

    @staticmethod
    def m3(block_thickness, screw_hole_depth=DEFAULT_SCREW_HOLE_DEPTH, counter_sunk=DEFAULT_COUNTER_SUNK, fit=DEFAULT_FIT):
        return DefaultScrewBlock.generic_screw("m3", block_thickness, screw_hole_depth, counter_sunk, fit)

    @staticmethod
    def m4(block_thickness, screw_hole_depth=DEFAULT_SCREW_HOLE_DEPTH, counter_sunk=DEFAULT_COUNTER_SUNK, fit=DEFAULT_FIT):
        return DefaultScrewBlock.generic_screw("m4", block_thickness, screw_hole_depth, counter_sunk, fit)

    @staticmethod
    def m5(block_thickness, screw_hole_depth=DEFAULT_SCREW_HOLE_DEPTH, counter_sunk=DEFAULT_COUNTER_SUNK, fit=DEFAULT_FIT):
        return DefaultScrewBlock.generic_screw("m5", block_thickness, screw_hole_depth, counter_sunk, fit)