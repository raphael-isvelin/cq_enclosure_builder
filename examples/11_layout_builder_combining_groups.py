# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

# Can be removed if you've installed cq_enclosure_builder on your system
import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Panel, PanelSize, Face
from cq_enclosure_builder.layout_builder import LayoutGroup, LayoutElement

panel = Panel(Face.TOP, PanelSize(200, 80, 2))

pf.set_default_parameters({"enclosure_wall_thickness": panel.size.wall_thickness})

jacks_grid_1 = LayoutGroup.grid_of_part("Jack 6.35", pf.build_jack(part_type="6.35mm PJ-612A"), rows=2, cols=5, margin_rows=5, margin_cols=2)
jacks_grid_2 = LayoutGroup.grid_of_part("Jack 3.5", pf.build_jack(part_type="3.5mm PJ-392"), rows=4, cols=3, margin_rows=0, margin_cols=0)
one_usb = LayoutElement("USB", pf.build_usb_a(part_type="3.0 vertical cltgxdd"))

all_jacks = LayoutGroup.fixed_width_line_of_elements(
    200,
    [jacks_grid_1, jacks_grid_2, one_usb],
    align_to_outside_footprint=True,
)

for idx, elem in enumerate(all_jacks.get_elements()):
    panel.add(elem.label, elem.part, rel_pos=elem.get_pos())
panel.assemble()
show_object(panel.panel_with_debug)