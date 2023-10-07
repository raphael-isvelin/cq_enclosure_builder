import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf
from cq_enclosure_builder import Enclosure, EnclosureSize, Face, ProjectInfo
from cq_enclosure_builder import Panel, Face
from cq_enclosure_builder.layout_builder import LayoutElement, LayoutGroup
from cq_enclosure_builder.parts.common.knobs_and_caps import KNOB_18_x_17_25

enclosure_size = EnclosureSize(60, 113, 31, 2)  # 1590B

pf.set_default_types({
    "button": 'SPST PBS-24B-4',
    "potentiometer": 'WH148',
    "barrel_plug": 'DC-022B',
    "jack": '6.35mm PJ-612A',
    "support": 'pyramid',
})
pf.set_default_parameters({
    "enclosure_wall_thickness": enclosure_size.wall_thickness,
    "pot_knob": KNOB_18_x_17_25,
})

def build_strength_test_enclosure(with_support: bool):
    project_name = "strength-test-" + ("with" if with_support else "without") + "-support"
    project_info = ProjectInfo(project_name, "1")
    enclosure = Enclosure(enclosure_size, project_info=project_info)

    pots = LayoutGroup.fixed_width_line_of_parts(
        enclosure_size.outer_width,
        [
            ("Pot left", pf.build_potentiometer()),
            ("Pot right", pf.build_potentiometer()),
        ],
        add_margin_on_sides=True,
        group_center_at_0_0=True,
        elements_centers_at_0_0=True,
        align_to_outside_footprint=False,
    )
    pots.translate([0, 30, 0])
    for idx, elem in enumerate(pots.get_elements()):
        enclosure.add_part_to_face(Face.TOP, elem.label, elem.part, rel_pos=elem.get_pos())

    spst = pf.build_button()
    enclosure.add_part_to_face(Face.TOP, "SPST", spst, rel_pos=(0, -30))

    if with_support:
        support_height = enclosure_size.outer_thickness - spst.inside_footprint_thickness - enclosure_size.wall_thickness
        support = pf.build_support(support_height=support_height)

        enclosure.add_part_to_face(Face.BOTTOM, "Support for SPST", support, rel_pos=(0, 30))

    enclosure.add_part_to_face(Face.BACK, "Barrel plug", pf.build_barrel_plug(), rel_pos=(0, -5))

    enclosure.add_part_to_face(Face.LEFT, "Jack out", pf.build_jack(), rel_pos=(0, 0))
    enclosure.add_part_to_face(Face.RIGHT, "Jack in", pf.build_jack(), rel_pos=(0, 0))

    enclosure.assemble()

    return enclosure

without_support = build_strength_test_enclosure(False)
with_support = build_strength_test_enclosure(True)

show_object(without_support.assembly_with_debug)
show_object(with_support.assembly_with_debug)

without_support.export_printables()
with_support.export_printables()