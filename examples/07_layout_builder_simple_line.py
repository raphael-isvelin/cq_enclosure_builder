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

pf.set_default_types({
    "usb_a": '3.0 vertical cltgxdd',
    "button": 'SPST PBS-24B-4',
    "encoder": 'EC11',
})
pf.set_default_parameters({"enclosure_wall_thickness": panel.size.wall_thickness})

group = LayoutGroup.line_of_parts(
    [
        ("USB", pf.build_usb_a()),
        ("Button", pf.build_button()),
        ("Encoder", pf.build_encoder())
    ],
    margin=0,
    horizontal=True,
    group_center_at_0_0=False,
    align_start_to_outside_footprint=False,  # redundant if align_to_outside_footprint is True
    align_to_outside_footprint=False,
)

# Example of alignments, when group_center_at_0_0 is True:
# - if align_to_outside_footprint,
#   the left of the USB's outside footprint (i.e. the port's hole) will be at -X,
#   and the right of the Encoder's outside footprint (i.e. the cap) will be at +X
# - if not, it will use the inside footprint (i.e. the board)

# Example of alignments, when group_center_at_0_0 is False:
# - if align_[start_]to_outside_footprint, (0,0) will correspond to the the left of the USB's outside footprint
# - if not, it will use the inside footprint

# align_to_outside_footprint will make sure all the outside footprints touch each other (if margin=0)
# while align_start_to_outside_footprint will only make the first outside footprint start at (0,0) and use the total footprint for the rest

for idx, elem in enumerate(group.get_elements()):
    panel.add(elem.label, elem.part, rel_pos=elem.get_pos())

panel.assemble()

show_object(panel.panel_with_debug)