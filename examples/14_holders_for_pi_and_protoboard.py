# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Panel, Face

panel = Panel(Face.BOTTOM, 180, 90, 2)

pf.set_default_parameters({"enclosure_wall_thickness": 2})

pi_holder = pf.build_holder(
    part_type="RPi 4B",
    add_pi_to_footprint=True,
)
protoboard_holder = pf.build_holder(
    part_type="Protoboard",
    add_board_to_footprint=True,
)

panel.add("Pi holder", pi_holder, rel_pos=(-40, 0))
panel.add("Protoboard holder", protoboard_holder, rel_pos=(60, 0))

panel.assemble()

show_object(panel.panel_with_debug)