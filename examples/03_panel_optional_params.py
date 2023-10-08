# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

# Can be removed if you've installed cq_enclosure_builder on your system
import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Panel, PanelSize, Face

panel_size = PanelSize(100, 38, 1.2)
panel = Panel(
    Face.TOP,
    panel_size,
    color=(1, 0, 0),  # colors are RGB with a scale from 0 to 1
    part_color=(0, 1, 0),
    alpha=0.2,  # affects the panel itself, not its parts
)

pf.set_default_types({"button": 'SPST PBS-24B-4'})
pf.set_default_parameters({"enclosure_wall_thickness": panel_size.wall_thickness})

button = pf.build_button()

panel.add("SPST", pf.build_button(), rel_pos=(0, 5))

panel.assemble()

show_object(panel.panel)