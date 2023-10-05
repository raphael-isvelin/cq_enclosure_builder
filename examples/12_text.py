# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

import sys
sys.path.append("cq_enclosure_builder/src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Enclosure, EnclosureSize, Face, ProjectInfo

enclosure_size = EnclosureSize(180, 90, 38, 2)
enclosure = Enclosure(enclosure_size)

pf.set_default_types({"text": 'default'})
pf.set_default_parameters({"enclosure_wall_thickness": 2})

extruded_text = pf.build_text(
    text = "Sample text\nA new line",
)

cut_text = pf.build_text(
    text = "Hello",
    thickness = 5.6,
    cut = True,
    fontsize = 8,
    width = 30,
    length = 9,
    outside = True,
)

enclosure.add_part_to_face(Face.TOP, "Extruded", extruded_text, rel_pos=(0, -6))
enclosure.add_part_to_face(Face.TOP, "Cut", cut_text, rel_pos=(0, 10))

enclosure.assemble(lid_panel_shift=200)

show_object(enclosure.assembly)