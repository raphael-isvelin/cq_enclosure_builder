# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Panel, Face

panel = Panel(Face.TOP, 180, 90, 2)

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

panel.add("Extruded", extruded_text, rel_pos=(0, -6))
panel.add("Cut", cut_text, rel_pos=(0, 10))

panel.assemble()

show_object(panel.panel)