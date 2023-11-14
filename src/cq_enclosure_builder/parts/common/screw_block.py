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

from typing import Dict, List, Tuple, Union
from enum import Enum

import cadquery as cq
import cq_warehouse.extensions
from cq_enclosure_builder.parts.common.hole_type import HoleType
from cq_enclosure_builder.parts.common.screws_providers import DefaultScrewProvider

class FitOptions(Enum):
    CLOSE = "Close"
    NORMAL = "Normal"
    LOOSE = "Loose"

class TaperOptions(Enum):
    NO_TAPER = 1
    XY_TAPER = 2
    Z_TAPER_ANGLE = 3
    Z_TAPER_SIDE = 4

class ScrewBlock:
    DEFAULT_FIT: FitOptions = FitOptions.LOOSE
    DEFAULT_TAPER: TaperOptions = TaperOptions.NO_TAPER
    DEFAULT_IS_COUNTER_SUNK: bool = False
    DEFAULT_WITH_COUNTER_SUNK_BLOCK: bool = False
    DEFAULT_SCREW_HOLE_DEPTH: Union[float, None] = None  # None -> fully go through. If still going through, read comment for fill_pointy_bit.

    def __init__(
        self,
        screw_provider=DefaultScrewProvider,
        counter_sunk_screw_provider=DefaultScrewProvider
    ):
        self.screw_provider = screw_provider
        self.counter_sunk_screw_provider = counter_sunk_screw_provider
        for size in self.get_available_screw_sizes():
            method_name = size.replace('.', '_')
            setattr(self, method_name, self._create_method_for_category(size))

    def get_available_screw_sizes(self) -> List[str]:
        return list(self.screw_provider.SCREW_SIZE_REFERENCES.keys())

    def build(
        self,
        screw_size_category: str,
        block_thickness: float,
        enclosure_wall_thickness: float,  # TOD move parameter before block_thickness for consistency
        screw_hole_depth: Union[float, None] = DEFAULT_SCREW_HOLE_DEPTH,
        fill_pointy_bit: bool = False,  # read comment where used
        is_counter_sunk: bool = DEFAULT_IS_COUNTER_SUNK,
        with_counter_sunk_block: bool = DEFAULT_WITH_COUNTER_SUNK_BLOCK,
        fit: FitOptions = DEFAULT_FIT,
        taper: TaperOptions = DEFAULT_TAPER,
        taper_rotation: float = 0.0,
        xy_taper_incline: float = 0.75,
        xy_taper_from: float = 0,  # useful to start your screw inside of a wall
        hole_position: Tuple[float, float] = (0, 0),
        counter_sunk_extrude_depth: float = 0,
        counter_sunk_negative_mask_error_margin: float = 0.4,
    ):
        fastener, block_size, hole_type = self.screw_provider.build_fastener(screw_size_category)
        cs_fastener = cs_block_size = None
        if with_counter_sunk_block and self.counter_sunk_screw_provider is not None:
            cs_fastener, cs_block_size = self.counter_sunk_screw_provider.build_counter_sunk_fastener(screw_size_category)
        elif with_counter_sunk_block:
                print("with_counter_sunk_block is true, but no counter_sunk_screw_provider given")

        block_size = (*block_size, block_thickness)

        if screw_hole_depth == None:
            screw_hole_depth = block_size[2]

        screw_block = (
            cq.Workplane("XY")
                .box(*block_size, centered=(True, True, False))
                .faces(">Z").workplane().pushPoints([hole_position])
        )
        if hole_type == HoleType.THREADED_HOLE:
            screw_block = screw_block.threadedHole(fastener=fastener, depth=screw_hole_depth, fit=fit.value, counterSunk=is_counter_sunk)
        elif hole_type == HoleType.INSERT_HOLE:
            screw_block = screw_block.insertHole(fastener=fastener, depth=screw_hole_depth, fit=fit.value)
        elif hole_type == HoleType.CLEARANCE_HOLE:
            screw_block = screw_block.clearanceHole(fastener=fastener, depth=screw_hole_depth, fit=fit.value, counterSunk=is_counter_sunk)

        if fill_pointy_bit and screw_hole_depth != block_thickness:  # if the goal wasn't to pierce through the entire block
            # With threadedHole, cq_warehouse digs deeper than screw_hole_depth to make space for the 'pointy tip' of the screw,
            # leading the hole to pierce through; any better way to deal with that?
            # Only filling half of the hole to give a bit of leeway.
            filler_thickness = (block_thickness - screw_hole_depth) / 2
            screw_block = screw_block.add(
                cq.Workplane("XY")
                    .box(block_size[0], block_size[1], filler_thickness, centered=(True, True, False))
            )

        if taper == TaperOptions.Z_TAPER_ANGLE:
            screw_block.add(
                cq.Workplane("XY")
                    .rect(block_size[0]*2, block_size[1]*2)
                    .extrude(block_size[0]*2, taper=45)
                    .cut(cq.Workplane("XY").rect(block_size[0], block_size[1]).extrude(block_size[0]*2).translate([-(block_size[0]/2), -(block_size[1]/2), 0]))
                    .cut(cq.Workplane("XY").rect(block_size[0], block_size[1]).extrude(block_size[0]*2).translate([-(block_size[0]/2), block_size[1]/2, 0]))
                    .cut(cq.Workplane("XY").rect(block_size[0], block_size[1]).extrude(block_size[0]*2).translate([block_size[0]/2, -(block_size[1]/2), 0]))
                    .translate([-(block_size[0]/2), -(block_size[1]/2), screw_hole_depth])
                    .rotate((0, 0, 0), (0, 0, 1), -taper_rotation)
            )
        elif taper == TaperOptions.Z_TAPER_SIDE:
            screw_block.add(
                cq.Workplane("XZ")
                    .moveTo(0, 0)
                    .lineTo(block_size[0], 0)
                    .lineTo(0, block_size[0])
                    .close()
                    .extrude(block_size[1])
                    .translate([-(block_size[0]/2), block_size[1]/2, screw_hole_depth])
                    .rotate((0, 0, 0), (0, 0, 1), -taper_rotation)
            )
        elif taper == TaperOptions.XY_TAPER:
            screw_block.add(
                cq.Workplane("YZ")
                    .moveTo(0, xy_taper_from)
                    .lineTo((block_size[2]-xy_taper_from)*xy_taper_incline, xy_taper_from)
                    .lineTo(0, block_size[2])
                    .close()
                    .extrude(block_size[1])
                    .translate([-(block_size[0]/2), block_size[1]/2, 0])
                    .rotate((0, 0, 0), (0, 0, 1), -taper_rotation)
            )

        mask = cq.Workplane("XY").box(*block_size, centered=(True, True, False))

        cs_block = cs_mask = None
        if with_counter_sunk_block and self.counter_sunk_screw_provider is not None:
            try:
                cs_block = (
                    cq.Workplane("XY")
                        .box(*cs_block_size, enclosure_wall_thickness + counter_sunk_extrude_depth, centered=(True, True, False))
                        .faces(">Z").workplane().pushPoints([(0, 0)])
                        .clearanceHole(fastener=cs_fastener, depth=enclosure_wall_thickness + counter_sunk_extrude_depth, fit=fit.value, counterSunk=True)
                        .translate([*hole_position, block_thickness - counter_sunk_extrude_depth])
                )
                cs_mask = (
                    cq.Workplane("XY")
                        .box(*cs_block_size, enclosure_wall_thickness, centered=(True, True, False))
                        .translate([*hole_position, block_thickness])
                )
                if counter_sunk_extrude_depth > 0:
                    negative_mask_size = (
                        cs_block_size[0] + counter_sunk_negative_mask_error_margin*2,
                        cs_block_size[1] + counter_sunk_negative_mask_error_margin*2,
                        enclosure_wall_thickness + counter_sunk_extrude_depth
                    )
                    cs_block_negative_mask = (
                        cq.Workplane("XY")
                            .box(*negative_mask_size, centered=(True, True, False))
                            .translate([*hole_position, block_thickness])
                            .translate([0, 0, -(block_size[2] + enclosure_wall_thickness)])
                    )
                    screw_block = screw_block.cut(cs_block_negative_mask)
            except Exception as e:
                raise ValueError("Couldn't create counter-sunk; enclosure_wall_thickness should be thickness than the screw head") from e

        return {
            "block": screw_block,
            "counter_sunk_block": cs_block,
            "mask": mask,
            "counter_sunk_mask": cs_mask,
            "size": block_size
        }

    def _create_method_for_category(self, screw_size_category):
        def method(
            block_thickness: float,
            enclosure_wall_thickness: float = 2,
            screw_hole_depth: Union[int, None] = ScrewBlock.DEFAULT_SCREW_HOLE_DEPTH,
            fill_pointy_bit: bool = False,  # read comment where used
            is_counter_sunk: bool = ScrewBlock.DEFAULT_IS_COUNTER_SUNK,
            with_counter_sunk_block: bool = ScrewBlock.DEFAULT_WITH_COUNTER_SUNK_BLOCK,
            fit: FitOptions = ScrewBlock.DEFAULT_FIT,
            taper: TaperOptions = ScrewBlock.DEFAULT_TAPER,
            taper_rotation: float = 0.0,
            xy_taper_incline: float = 0.75,
            xy_taper_from: float = 0  # useful to start your screw inside of a wall
        ):
            return self.build(
                screw_size_category,
                block_thickness,
                enclosure_wall_thickness,
                screw_hole_depth,
                fill_pointy_bit,
                is_counter_sunk,
                with_counter_sunk_block,
                fit,
                taper,
                taper_rotation,
                xy_taper_incline,
                xy_taper_from
            )
        return method