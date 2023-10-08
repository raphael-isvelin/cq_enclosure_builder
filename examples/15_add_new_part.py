# NOTE
# It is strongly recommended to use Jupyter-Cadquery and the .ipynb sample file instead of this
# to view the examples: it will make it way easier for you to naviguate through the enclosure:
# interract with the models, hide parts, view the debug assemblies more easily, and much more.

# Can be removed if you've installed cq_enclosure_builder on your system
import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Part, Panel, PanelSize, Face
from cq_enclosure_builder.parts_factory import register_part


@register_part("cool_thing", "ABC-45")  # only required to use the PartsFactory (see below)
class Abc45Part(Part):
    def __init__(
        self,
        enclosure_wall_thickness: float,
    ) -> None:
        super().__init__()

        part_size = (10, 8)
        thing_poking_out_thickness = 5

        self.part = (
            cq.Workplane("front")
                .box(*part_size, thing_poking_out_thickness + enclosure_wall_thickness, centered=(True, True, False))
                .translate([0, 0, -thing_poking_out_thickness])
        )
        self.mask = (
            cq.Workplane("front")
                .box(*part_size, enclosure_wall_thickness, centered=(True, True, False))
        )

        self.size.width     = part_size[0]
        self.size.length    = part_size[1]
        self.size.thickness = thing_poking_out_thickness + enclosure_wall_thickness

        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = 0
        self.inside_footprint_offset = (0, 0)

        self.outside_footprint = (self.size.width, self.size.length)
        self.outside_footprint_thickness = thing_poking_out_thickness

        self.debug_objects.footprint.inside  = None
        self.debug_objects.footprint.outside = (
            cq.Workplane("front")
                .box(*part_size, thing_poking_out_thickness, centered=(True, True, False))
                .translate([0, 0, -thing_poking_out_thickness])
        )


panel = Panel(Face.TOP, PanelSize(60, 30, 2))

my_part = Abc45Part(enclosure_wall_thickness=2)
panel.add("test 1", my_part, rel_pos=(-20, 0))

panel.add("test 2", pf.build_cool_thing(part_type='ABC-45', enclosure_wall_thickness=2), rel_pos=(00, 10))

pf.set_default_types({"cool_thing": 'ABC-45'})
pf.set_default_parameters({"enclosure_wall_thickness": panel.size.wall_thickness})
panel.add("test 3", pf.build_cool_thing(), rel_pos=(20, 0))

panel.assemble()

show_object(panel.panel_with_debug)