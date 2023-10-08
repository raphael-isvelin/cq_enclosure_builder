# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

# WARNING
# This example takes a bit of time to render, and cq-editor fully freezes while rendering

# Can be removed if you've installed cq_enclosure_builder on your system
import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Panel, PanelSize, Face
from cq_enclosure_builder.layout_builder import LayoutElement, LayoutGroup

panel = Panel(Face.TOP, PanelSize(0.1, 0.1, 0.1))  # not caring about the panel size

pf.set_default_parameters({
    "enclosure_wall_thickness": panel.size.wall_thickness,
    "support_height": 10,  # used by support/pyramid
    "width": 8,  # used by support/skirt
    "length": 6,  # used by support/skirt
})
# Will break if new Parts with arguments without default values are added

lines = []

for category in pf.list_categories():
    part_types = pf.list_types_for_category(category)
    parts = []
    for part_type in part_types:
        parts.append((part_type, pf.build(category=category, part_type=part_type)))

    group = LayoutGroup.line_of_parts(
        parts,
        margin=5,
        horizontal=True,
        group_center_at_0_0=True,
    )
    lines.append(group)

group_of_groups = LayoutGroup.line_of_elements(
    lines,
    margin=15,
    horizontal=False,
    group_center_at_0_0=True,
)

for idx, elem in enumerate(group_of_groups.get_elements()):
    panel.add(elem.label, elem.part, rel_pos=elem.get_pos())

panel.assemble()

show_object(panel.panel_with_debug)