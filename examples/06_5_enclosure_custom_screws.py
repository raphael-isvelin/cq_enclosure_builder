# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Enclosure, EnclosureSize, Face, ProjectInfo
from cq_enclosure_builder.parts.common.screws_providers import DefaultScrewProvider
from cq_enclosure_builder.parts.common.screw_block import ScrewBlock, TaperOptions

enclosure = Enclosure(EnclosureSize(80, 56, 38, 1.4))

pf.set_default_types({"button": 'SPST PBS-24B-4'})
pf.set_default_parameters({"enclosure_wall_thickness": enclosure.size.wall_thickness})

enclosure.add_part_to_face(Face.TOP, "SPST", pf.build_button(), rel_pos=(0, 0))

# We need to know the size of the screw we're about to add,
#   as its centred at (0,0).
# This makes adding screws more verbose than it should; it should be refactored.
screw_size_category = "m2"
screw_size = ScrewBlock().build(screw_size_category, Enclosure.CORNER_LID_SCREWS_THICKNESS, enclosure.size.wall_thickness)["size"]

sw = screw_size[0]
sl = screw_size[1]
wt = enclosure.size.wall_thickness
screws_specs = [
    ( (15, sw/2 + wt), 270 ),
    ( (25, enclosure.size.outer_length - sw/2 - wt),  90 ),
]

for screw_specs in screws_specs:
    enclosure.add_screw(
        screw_size_category=screw_size_category,
        block_thickness=Enclosure.CORNER_LID_SCREWS_THICKNESS,
        abs_pos=screw_specs[0],
        pos_error_margin=enclosure.lid_thickness_error_margin,
        taper=TaperOptions.Z_TAPER_SIDE,
        taper_rotation=screw_specs[1],
    )

enclosure.assemble()

show_object(enclosure.assembly_with_debug)