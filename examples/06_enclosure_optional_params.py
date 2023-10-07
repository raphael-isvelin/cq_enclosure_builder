# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Enclosure, EnclosureSize, Face, ProjectInfo

project_info = ProjectInfo("Hello World", "0.9")
enclosure = Enclosure(
    size=EnclosureSize(180, 90, 38, 2),
    project_info=project_info,
    lid_on_faces=[Face.BOTTOM],    # for now, can only be BOTTOM, feel free to contribute/open an issue if you have a more specific need
    lid_panel_size_error_margin=1.2, # meaning the lid is `margin` smaller than the hole (space for the lid) on both width and length
    lid_thickness_error_margin=2,  # if >0, the lid screws and support will be slightly sunk in the enclosure
    add_corner_lid_screws=True,    # one screw per corner; more can be added with Enclosure#add_screw
    add_lid_support=True,     # adds a rim all around the enclosure to prevent the lid from sinking in
    add_top_support=True,     # small support rim on the enclosure to provide additional strength
    lid_screws_heat_set=True, # use heat set inserts instead of printed threads
    no_fillet_top=True,      # removed the fillet (rounded edges) on the top of the enclosure
    no_fillet_bottom=True,   # removed the fillet (rounded edges) on the bottom of the enclosure
)

pf.set_default_types({"button": 'SPST PBS-24B-4'})
pf.set_default_parameters({"enclosure_wall_thickness": enclosure.size.wall_thickness})

enclosure.add_part_to_face(Face.TOP, "SPST", pf.build_button(), rel_pos=(0, 0))
enclosure.assemble()

show_object(enclosure.all_printables_assembly)

# Exports the following files, based on the project's name and version:
#   - stls/hello_world-box-v0.9.stl
#   - stls/hello_world-lid-v0.9.stl
#   - stls/hello_world-ALL-v0.9.stl
enclosure.export_printables()