# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Panel, PanelSize, Face
from cq_enclosure_builder.layout_builder import LayoutElement, LayoutGroup

panel_size = PanelSize(100, 38, 2)
panel = Panel(Face.TOP, panel_size)

pf.set_default_types({
    "usb_a": '3.0 vertical cltgxdd',
    "button": 'SPST PBS-24B-4',
    "encoder": 'EC11',
})
pf.set_default_parameters({"enclosure_wall_thickness": panel_size.wall_thickness})

button_element = LayoutElement("Button", pf.build_button())
usb_element = LayoutElement("USB", pf.build_usb_a())
encoder_element = LayoutElement("Encoder", pf.build_encoder())
button_element.set_footprints_x(encoder_element.total_footprint[0])

# A hacky way to keep the middle element's center at (0,0) is to override the footprint
#   of the element[s] on its left and the element[s] of its right to be equal
# The margins, of course, won't be equal, but it can work better for some layout
#   (see Octopus' front panel for example: we want the screen at 0,0)

group = LayoutGroup.fixed_width_line_of_elements(
    panel_size.width,
    [button_element, usb_element, encoder_element],
    horizontal=True,
    add_margin_on_sides=True,
    group_center_at_0_0=False,
    elements_centers_at_0_0=True,
    align_to_outside_footprint=True,
)

group.translate([0, panel_size.length/2, 0])
for idx, elem in enumerate(group.get_elements()):
    panel.add(elem.label, elem.part, abs_pos=elem.get_pos())
panel.assemble()
show_object(panel.panel_with_debug)