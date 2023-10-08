# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

# Can be removed if you've installed cq_enclosure_builder on your system
import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Enclosure, EnclosureSize, Face, ProjectInfo

enclosure_size = EnclosureSize(
    outer_width=180,
    outer_length=90,
    outer_thickness=38,
    wall_thickness=2
)
enclosure = Enclosure(enclosure_size)

pf.set_default_types({"button": 'SPST PBS-24B-4'})
pf.set_default_parameters({"enclosure_wall_thickness": enclosure.size.wall_thickness})

enclosure.add_part_to_face(Face.TOP, "SPST", pf.build_button(), rel_pos=(-10, 0))

# The explosion factor and lid panel shift will helps you to see the insides of the enclosure
enclosure.assemble(walls_explosion_factor=1.5, lid_panel_shift=20)

show_object(enclosure.assembly)