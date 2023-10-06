VIEWER_THEME = "light"  # light, dark
VIEWER_HEIGHT = 900
ENABLE_REPLAY = True

import cadquery as cq

from jupyter_cadquery import show as jcq_show, open_viewer

from jupyter_cadquery.replay import replay, enable_replay, disable_replay
enable_replay(ENABLE_REPLAY)

cv = open_viewer("Assembly", anchor="right")  # sets default viewer

objects_to_hide = [
    "/Mask",
    "/Panels masks"
]

def hide_objects_matching_strings(strings, keep_edges=True, cv=cv):
    for state in cv.widget.states:
        should_hide = False
        for s in strings:
            if s in state:
                should_hide = True
                break
        if should_hide:
            cv.update_states({
                state: (0, 0 if keep_edges else 0),
            })

def show(obj, viewer="Assembly", anchor="right", hide_contains=objects_to_hide):
    cv = jcq_show(
        obj,
        viewer=viewer,
        anchor=anchor,
        #cad_width=1640,
        height=VIEWER_HEIGHT,
        theme=VIEWER_THEME,
        collapse=1,
        optimal_bb=True,
        render_edges=True,
        axes=True,
        axes0=True,
        grid=[True, True, True],
        #black_edges=True,
        reset_camera=False,
        #show_parent=True,
        #timeit=True,
        #js_debug=True
    )
    hide_objects_matching_strings(hide_contains, cv=cv)

def show_b(obj, viewer="Quick", hide_contains=objects_to_hide):
    cv2 = open_viewer(viewer, anchor="split-bottom")
    show(obj, viewer, anchor="split-bottom", hide_contains=hide_contains)

def show_x(obj, hide_contains=objects_to_hide):
    show(obj, viewer=None, hide_contains=hide_contains)

def show_part(part, bottom=False):
    footprint_assembly = (
        cq.Assembly()
            .add(part.debug_objects.footprint.inside, name="Inside", color=cq.Color(1, 0, 1))
            .add(part.debug_objects.footprint.outside, name="Outside", color=cq.Color(0, 1, 1))
    )
    test_assembly = (
        cq.Assembly(None, name="test_assembly")
            .add(part.mask, name="Mask", color=cq.Color(0, 1, 0))
            .add(part.part, name="Part")
            .add(part.assembly_parts_to_cq_assembly(), name="Part assembly")
            .add(footprint_assembly, name="Footprint")
    )
    debug_assembly = cq.Assembly()
    debug_assembly.add(part.debug_objects.hole, name="Hole", color=cq.Color(1, 0, 0))
    for debug_obj_name in part.debug_objects.others.keys():
        obj = part.debug_objects.others[debug_obj_name]
        if not isinstance(obj, dict):
            debug_assembly.add(obj, name=debug_obj_name, color=cq.Color(0.5, 0.7, 0.5))
    test_assembly.add(debug_assembly, name="Debug")

    if bottom: show_b(test_assembly)
    else: show(test_assembly)