# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Enclosure, EnclosureSize, Face, ProjectInfo

enclosure = Enclosure(EnclosureSize(180, 120, 38, 2))

pf.set_default_types({"screen": 'DSI 5 inch CFsunbird'})
pf.set_default_parameters({"enclosure_wall_thickness": enclosure.size.wall_thickness})

enclosure.add_part_to_face(Face.TOP, "DSI screen", pf.build_screen(), rel_pos=(0, 0))

enclosure.assemble()

show_object(enclosure.all_printables_assembly)

# Exports ready-to-print STLs in the 'stls/' folder
#   - my_project-box-v1.0.0.stl
#   - my_project-lid-v1.0.0.stl
#   - my_project-screen-strip-1-v1.0.0.stl
#   - my_project-screen-strip-2-v1.0.0.stl
#   - my_project-screen-strip-3-optional-v1.0.0.stl
#   - my_project-ALL-v1.0.0.stl
# (names based on the default value of ProjectInfo; see next example)
enclosure.export_printables()