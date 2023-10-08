# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

# Can be removed if you've installed cq_enclosure_builder on your system
import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Panel, PanelSize, Face
from cq_enclosure_builder.layout_builder import LayoutGroup

panel = Panel(Face.TOP, PanelSize(100, 38, 2))

pf.set_default_types({"jack": '6.35mm PJ-612A'})
pf.set_default_parameters({"enclosure_wall_thickness": panel.size.wall_thickness})

jacks_grid = LayoutGroup.grid_of_part(
    "Jack 6.35",
    pf.build_jack(),
    rows=2,
    cols=5,
    margin_rows=0,
    margin_cols=2,
)

for idx, elem in enumerate(jacks_grid.get_elements()):
    panel.add(elem.label, elem.part, rel_pos=elem.get_pos())
panel.assemble()
show_object(panel.panel_with_debug)