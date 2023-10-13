import cadquery as cq

# Can be removed if you've installed cq_enclosure_builder on your system
import sys
sys.path.append("../src")

from cq_enclosure_builder import Enclosure, Face
from cq_enclosure_builder.layout_builder import LayoutElement

def rotate_to_face(face, wp) -> cq.Workplane:
    if face == Face.TOP:
        wp = wp.mirror("XY")
    elif face == Face.BOTTOM:
        wp = wp.mirror("XZ")
    elif face == Face.BACK:
        wp = wp.rotate((0, 0, 0), (1, 0, 0), 90)
        wp = wp.mirror("YZ")
    elif face == Face.FRONT:
        wp = wp.rotate((0, 0, 0), (1, 0, 0), 90)
        wp = wp.mirror("XZ")
    elif face == Face.LEFT:
        wp = wp.rotate((0, 0, 0), (1, 0, 0), 90)
        wp = wp.rotate((0, 0, 0), (0, 0, 1), 90)
        wp = wp.mirror("XZ")
    elif face == Face.RIGHT:
        wp = wp.rotate((0, 0, 0), (1, 0, 0), 90)
        wp = wp.rotate((0, 0, 0), (0, 0, 1), -90)
        wp = wp.mirror("XZ")
    return wp

def get_index_of_face(face, panels_specs):
    return next((index for index, panel in enumerate(panels_specs) if panel[0] == face), -1)

def translate_and_rotate_to_face(
    part,
    translation,
    face: Face,
    enclosure: Enclosure,
) -> cq.Workplane:
    part = part.translate(translation)
    part = rotate_to_face(face, part)
    index = get_index_of_face(face, enclosure.panels_specs)
    part = part.translate(enclosure.panels_specs[index][2])
    return part

def build_debug_layout_marker(
    layout_element: LayoutElement,
    face: Face,
    enclosure: Enclosure,
    thickness_in: float = 20,
    thickness_out: float = 20,
):
    marker_in = (
        cq.Workplane("front")
            .box(*layout_element.inside_footprint, thickness_in, centered=(True, True, False))
            .translate([0, 0, -(thickness_in/2)])
    )
    marker_out = (
        cq.Workplane("front")
            .box(*layout_element.outside_footprint, thickness_out, centered=(True, True, False))
            .translate([0, 0, -(thickness_out/2)])
    )
    pos_in = (
        layout_element.pos[0] + layout_element.inside_footprint_offset[0],
        layout_element.pos[1] + layout_element.inside_footprint_offset[1],
    )
    pos_out = (
        layout_element.pos[0] + layout_element.outside_footprint_offset[0],
        layout_element.pos[1] + layout_element.outside_footprint_offset[1],
    )
    marker_in = translate_and_rotate_to_face(marker_in, pos_in, face, enclosure)
    marker_out = translate_and_rotate_to_face(marker_out, pos_out, face, enclosure)
    return (marker_in, marker_out)