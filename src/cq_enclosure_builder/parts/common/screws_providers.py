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

from typing import Dict, Tuple

from cq_warehouse.fastener import HeatSetNut
from cq_enclosure_builder.screws.flat_head_screw import FlatHeadScrew
from .generic_screw_provider import GenericScrewProvider
from .hole_type import HoleType


class DefaultFlatHeadScrewProvider:
    SCREW_CLASS = FlatHeadScrew
    SCREW_MODEL_NAME: str = "aliexpress"
    SCREW_SIZE_REFERENCES: Dict[str, str] = {
        "m1.4": "M1.4-0.3",
        "m2": "M2-0.4",
        "m2.5": "M2.5-0.45",
        "m3": "M3-0.5",
        "m3.5": "M3.5-0.6",
        "m4": "M4-0.7",
        "m5": "M5-0.8",
    }
    BLOCK_SIZES: Dict[str, Tuple[int, int]] = {
        "m1.4": (5, 5),
        "m2": (6, 6),
        "m2.5": (7, 7),
        "m3": (8, 8),
        "m3.5": (9, 9),
        "m4": (10, 10),
        "m5": (12, 12),
    }
    COUNTER_SUNK_BLOCK_SIZES: Dict[str, Tuple[int, int]] = {
        "m1.4": (3, 3),
        "m2": (4.6, 4.6),
        "m2.5": (5.6, 5.6),  # TODO double-check once delivered
        "m3": (6.8, 6.8),
        "m3.5": (7.8, 7.8),  # TODO double-check once delivered
        "m4": (8.6, 8.6),
        "m5": (10.4, 10.4),
    }
    HOLE_TYPE: HoleType = HoleType.THREADED_HOLE
    INCLUDE_LENGTH_PARAM: bool = True

    @classmethod
    def build_fastener(cls, screw_size_category: str):
        return GenericScrewProvider.build_fastener(
            cls.SCREW_CLASS,
            cls.SCREW_MODEL_NAME,
            cls.SCREW_SIZE_REFERENCES,
            cls.BLOCK_SIZES,
            cls.HOLE_TYPE,
            cls.INCLUDE_LENGTH_PARAM,
            screw_size_category
        )

    @classmethod
    def build_counter_sunk_fastener(cls, screw_size_category: str):
        return GenericScrewProvider.build_counter_sunk_fastener(
            cls.SCREW_CLASS,
            cls.SCREW_MODEL_NAME,
            cls.SCREW_SIZE_REFERENCES,
            cls.COUNTER_SUNK_BLOCK_SIZES,
            cls.INCLUDE_LENGTH_PARAM,
            screw_size_category
        )


class TinyBlockFlatHeadScrewProvider:
    SCREW_CLASS = FlatHeadScrew
    SCREW_MODEL_NAME: str = "aliexpress"
    SCREW_SIZE_REFERENCES: Dict[str, str] = {
        "m1.4": "M1.4-0.3",
        "m2": "M2-0.4",
        "m2.5": "M2.5-0.45",
        "m3": "M3-0.5",
        "m3.5": "M3.5-0.6",
        "m4": "M4-0.7",
        "m5": "M5-0.8",
    }
    BLOCK_SIZES: Dict[str, Tuple[int, int]] = {
        "m1.4": (2.4, 2.4),
        "m2": (3.6, 3.6),
        "m2.5": (4.2, 4.2),
        "m3": (4.8, 4.8),
        "m3.5": (5.4, 5.4),
        "m4": (6, 6),
        "m5": (7.2, 7.2),
    }
    COUNTER_SUNK_BLOCK_SIZES: Dict[str, Tuple[int, int]] = {
        "m1.4": (3, 3),
        "m2": (4.6, 4.6),
        "m2.5": (5.6, 5.6),
        "m3": (6.8, 6.8),
        "m3.5": (7.8, 7.8),
        "m4": (8.6, 8.6),
        "m5": (10.4, 10.4),
    }
    HOLE_TYPE: HoleType = HoleType.THREADED_HOLE
    INCLUDE_LENGTH_PARAM: bool = True

    @classmethod
    def build_fastener(cls, screw_size_category: str):
        return GenericScrewProvider.build_fastener(
            cls.SCREW_CLASS,
            cls.SCREW_MODEL_NAME,
            cls.SCREW_SIZE_REFERENCES,
            cls.BLOCK_SIZES,
            cls.HOLE_TYPE,
            cls.INCLUDE_LENGTH_PARAM,
            screw_size_category
        )

    @classmethod
    def build_counter_sunk_fastener(cls, screw_size_category: str):
        return GenericScrewProvider.build_counter_sunk_fastener(
            cls.SCREW_CLASS,
            cls.SCREW_MODEL_NAME,
            cls.SCREW_SIZE_REFERENCES,
            cls.COUNTER_SUNK_BLOCK_SIZES,
            cls.INCLUDE_LENGTH_PARAM,
            screw_size_category
        )


class DefaultHeatSetScrewProvider:
    SCREW_CLASS = HeatSetNut
    SCREW_MODEL_NAME: str = "Hilitchi"
    SCREW_SIZE_REFERENCES: Dict[str, str] = {
        "m2": "M2-0.4-8",
        "m2.5": "M2.5-0.45-8",  # TODO check if exists for Hilitchi
        "m3": "M3-0.5-10",
        "m4": "M4-0.7-10",
        "m5": "M5-0.8-10",
        "m6": "M6-1-12"
    }
    BLOCK_SIZES: Dict[str, Tuple[int, int]] = {
        "m2": (6, 6),
        "m2.5": (7, 7),
        "m3": (8, 8),
        "m4": (10, 10),
        "m5": (12, 12),
        "m6": (12, 12),
    }
    HOLE_TYPE: HoleType = HoleType.INSERT_HOLE
    INCLUDE_LENGTH_PARAM: bool = False

    @classmethod
    def build_fastener(cls, screw_size_category: str):
        return GenericScrewProvider.build_fastener(
            cls.SCREW_CLASS,
            cls.SCREW_MODEL_NAME,
            cls.SCREW_SIZE_REFERENCES,
            cls.BLOCK_SIZES,
            cls.HOLE_TYPE,
            cls.INCLUDE_LENGTH_PARAM,
            screw_size_category
        )

    @classmethod
    def build_counter_sunk_fastener(cls, screw_size_category: str):
        raise ValueError("Counter-sunk fastener cannot be a HeadSetScrew")
