# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

# Can be removed if you've installed cq_enclosure_builder on your system
import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Enclosure, EnclosureSize, Face, ProjectInfo

enclosure = Enclosure(EnclosureSize(180, 90, 38, 2))

pf.set_default_types({
    "button": 'SPST PBS-24B-4',
    "support": 'pyramid',
})
pf.set_default_parameters({"enclosure_wall_thickness": enclosure.size.wall_thickness})

spst = pf.build_button()

support_height = enclosure.size.outer_thickness - spst.inside_footprint_thickness - enclosure.size.wall_thickness
support = pf.build_support(support_height=support_height)

enclosure.add_part_to_face(Face.TOP, "SPST", spst, rel_pos=(-10, 0))
enclosure.add_part_to_face(Face.BOTTOM, "Support for SPST", support, rel_pos=(-10, 0))

enclosure.assemble()

# To view how, inside the enclosure, a pillar is supporting the button from underneath,
#   you'll want to enable the wireframe (Shift+F9) mode (or use Jupyter-CadQuery for more control)
show_object(enclosure.assembly_with_debug)