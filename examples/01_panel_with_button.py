# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Panel, Face

WIDTH     = 100
LENGTH    = 38
THICKNESS = 2

panel = Panel(Face.TOP, WIDTH, LENGTH, THICKNESS)

button = pf.build_button(
    part_type="SPST PBS-24B-4",
    enclosure_wall_thickness=THICKNESS
)

panel.add("SPST", button, rel_pos=(10, 0))
panel.add("SPST corner", button, abs_pos=(0, 0))

panel.assemble()

show_object(panel.panel)