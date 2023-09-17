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
        "m3": "M3-0.5",
        "m4": "M4-0.7",
        "m5": "M5-0.8",
    }
    BLOCK_SIZES: Dict[str, Tuple[int, int]] = {
        "m1.4": (5, 5),
        "m2": (6, 6),
        "m3": (8, 8),
        "m4": (10, 10),
        "m5": (12, 12),
    }
    COUNTER_SUNK_BLOCK_SIZES: Dict[str, Tuple[int, int]] = {
        "m1.4": (3, 3),
        "m2": (4.6, 4.6),
        "m3": (6.8, 6.8),
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


class DefaultHeadSetScrewProvider:
    SCREW_CLASS = HeatSetNut
    SCREW_MODEL_NAME: str = "Hilitchi"
    SCREW_SIZE_REFERENCES: Dict[str, str] = {
        "m2": "M2-0.4-8",
        "m3": "M3-0.5-10",
        "m4": "M4-0.7-10",
        "m5": "M5-0.8-10",
        "m6": "M6-1-12"
    }
    BLOCK_SIZES: Dict[str, Tuple[int, int]] = {
        "m2": (6, 6),
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
