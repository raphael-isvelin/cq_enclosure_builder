# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

# Can be removed if you've installed cq_enclosure_builder on your system
import sys
sys.path.append("../src")

import cadquery as cq

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Part, Panel, PanelSize, Face
from cq_enclosure_builder.parts_factory import register_part


@register_part("something", "from STEP file")  # only needed if you want to use the PartsFactory (see below)
class HeartPart(Part):
    def __init__(
        self,
        enclosure_wall_thickness: float,
    ):
        super().__init__()

        part_size = (26.79, 29.947)
        part_thickness = 6
        thing_poking_out_thickness = 5

        self.part = cq.importers.importStep("16_part.step")
        self.mask = cq.importers.importStep("16_mask.step")

        self.part = self.part.translate([0, 0, -(part_thickness - enclosure_wall_thickness)])

        part_offset = (0.395, 8.026)  # I exported the part slightly off-centre
        self.part = self.part.translate([*part_offset, 0])
        self.mask = self.mask.translate([*part_offset, 0])

        self.size.width     = part_size[0]
        self.size.length    = part_size[1]
        self.size.thickness = 6

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = 0
        self.inside_footprint_offset = (0, 0)

        self.outside_footprint = (self.size.width, self.size.length)
        self.outside_footprint_thickness = part_thickness

        self.debug_objects.footprint.inside  = None
        self.debug_objects.footprint.outside = self.part


panel = Panel(Face.TOP, PanelSize(80, 30, 2))

pf.set_default_types({
    "button": 'SPST PBS-24B-4',
    "something": 'from STEP file',
})
pf.set_default_parameters({"enclosure_wall_thickness": panel.size.wall_thickness})

panel.add("Heart", pf.build_something(), rel_pos=(0, 0))
panel.add("SPST", pf.build_button(), rel_pos=(20, 0))

panel.assemble()

show_object(panel.panel)