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

panel_size = PanelSize(100, 38, 2)
panel = Panel(Face.TOP, panel_size)

pf.set_default_types({
    "usb_a": '3.0 vertical cltgxdd',
    "button": 'SPST PBS-24B-4',
    "encoder": 'EC11',
})
pf.set_default_parameters({"enclosure_wall_thickness": panel_size.wall_thickness})

# fixed_width_line_of_parts will spread the parts so the first is directly on
#   the starting at 0, and the last ending at <panel_size.width>

# If using align_to_outside_footprint,
#   0 and <panel_size.width> will be aligned to the outside footprint of the parts
# If using add_margin_on_sides, the line will start and end
#   at the same distance from the borders as the distance between each part

group = LayoutGroup.fixed_width_line_of_parts(
    panel_size.width,
    [
        ("USB", pf.build_usb_a()),
        ("Button", pf.build_button()),
        ("Encoder", pf.build_encoder())
    ],
    horizontal=True,
    add_margin_on_sides=False,
    align_other_dimension_at_0=False,
    align_to_outside_footprint=True,
)

for idx, elem in enumerate(group.get_elements()):
    panel.add(elem.label, elem.part, rel_pos=elem.get_pos())

panel.assemble()

show_object(panel.panel_with_debug)