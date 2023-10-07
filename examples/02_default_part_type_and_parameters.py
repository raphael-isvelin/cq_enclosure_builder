# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Panel, PanelSize, Face

panel_size = PanelSize(width=100, length=38, wall_thickness=2)
panel = Panel(Face.TOP, panel_size)

pf.set_default_types({
    "button": 'SPST PBS-24B-4',
})
pf.set_default_parameters({
    "enclosure_wall_thickness": panel_size.wall_thickness
})

button = pf.build_button()

panel.add("SPST", button, rel_pos=(-10, 0))
panel.add("SPST corner", button, abs_pos=(0, 0))

panel.assemble()

show_object(panel.panel_with_debug)