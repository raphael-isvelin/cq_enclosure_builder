# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Enclosure, EnclosureSize, Face, ProjectInfo

enclosure_size = EnclosureSize(180, 90, 38, 2)
enclosure = Enclosure(enclosure_size)

pf.set_default_types({"button": 'SPST PBS-24B-4'})
pf.set_default_parameters({"enclosure_wall_thickness": 2})

enclosure.add_part_to_face(Face.TOP, "SPST", pf.build_button(), abs_pos=(40, 10))

enclosure.assemble()

show_object(enclosure.assembly_with_debug)

# `enclosure.debug` (and `enclosure.assembly_with_debug`) will show
#   the 'printables' (you'll want to use Jupyter-CadQuery to hide individual parts and see them more easily)
#   they can then be exported

# Exports ready-to-print STLs in the 'stls/' folder
#   - my_project-box-v1.0.0.stl
#   - my_project-lid-v1.0.0.stl
# (names based on the default value of ProjectInfo; see next example)
enclosure.export_printables()