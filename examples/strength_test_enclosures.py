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
    project_info = ProjectInfo(project_name, "10")
    enclosure = Enclosure(enclosure_size, project_info=project_info, lid_screws_size_category="m3", lid_screws_heat_set=True)

    pots = LayoutGroup.fixed_width_line_of_parts(
        enclosure_size.outer_width,
        [
            ("Pot left", pf.build_potentiometer()),
            ("Pot right", pf.build_potentiometer()),
        ],
        add_margin_on_sides=True,
        align_other_dimension_at_0=True,
        align_to_outside_footprint=False,
    )
    spacer = LayoutElement.spacer_y(15)  # size isn't very accurate for now, see TODO in the method's code
    spst = LayoutElement("SPST", pf.build_button())

    title = pf.build_text(text="Strength test", fontsize=8, cut=False, width=40, length=10, thickness=1.0)
    subtitle = pf.build_text(text="v10", fontsize=11, cut=False, width=20, length=12, thickness=1.0)
    enclosure.add_part_to_face(Face.TOP, "Title", title, rel_pos=(0, 6.4))
    enclosure.add_part_to_face(Face.TOP, "Subtitle", subtitle, rel_pos=(0, -4))
    enclosure.add_part_to_face(Face.BOTTOM, "Version", subtitle, rel_pos=(0, 0))

    top_elements = LayoutGroup.fixed_width_line_of_elements(
        enclosure_size.outer_length,
        [spst, spacer, pots],
        horizontal=False,
        add_margin_on_sides=True,
        align_other_dimension_at_0=False,
        align_to_outside_footprint=True,
    )
    for idx, elem in enumerate(top_elements.get_elements()):
        enclosure.add_part_to_face(Face.TOP, elem.label, elem.part, rel_pos=elem.get_pos())

    if with_support:
        support_height = enclosure_size.outer_thickness - spst.part.inside_footprint_thickness - enclosure_size.wall_thickness*2
        support = pf.build_support(support_height=support_height)
        support_pos = (spst.pos[0], -spst.pos[1])  # Y coords are inversed between TOP and BOTTOM

        enclosure.add_part_to_face(Face.BOTTOM, "Support for SPST", support, rel_pos=support_pos)

    enclosure.add_part_to_face(Face.BACK, "Barrel plug", pf.build_barrel_plug(), rel_pos=(0, 0))

    enclosure.add_part_to_face(Face.LEFT, "Jack out", pf.build_jack(), rel_pos=(0, 0))
    enclosure.add_part_to_face(Face.RIGHT, "Jack in", pf.build_jack(), rel_pos=(0, 0))

    enclosure.assemble(lid_panel_shift=0)

    return enclosure

without_support = build_strength_test_enclosure(False)
with_support = build_strength_test_enclosure(True)

show_object(without_support.assembly_with_debug)
show_object(with_support.assembly_with_debug)

without_support.export_printables()
with_support.export_printables()