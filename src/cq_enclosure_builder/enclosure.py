"""
   Copyright 2023 Raphaël Isvelin

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from typing import List

import cadquery as cq
from cq_enclosure_builder import Part, Panel, Face, ProjectInfo
from cq_enclosure_builder.parts.common.screw_block import ScrewBlock, TaperOptions
from cq_enclosure_builder.parts.common.screws_providers import DefaultFlatHeadScrewProvider, DefaultHeatSetScrewProvider


def explode(pos_array, walls_explosion_factor=2.0):
    return [x * walls_explosion_factor for x in pos_array]


class EnclosureSize:
    def __init__(self, inner_width, inner_length, inner_thickness, wall_thickness):
        self.inner_width = inner_width
        self.inner_length = inner_length
        self.inner_thickness = inner_thickness
        self.wall_thickness = wall_thickness


class Enclosure:
    def __init__(
        self,
        size: EnclosureSize,
        lid_on_faces: List[Face] = [Face.BOTTOM],
        lid_panel_size_error_margin = 0.8,  # meaning the lid is `margin` smaller than the hole on both width and length
        lid_screws_thickness_error_margin = 0.4,
        add_corner_lid_screws = True,
        lid_screws_heat_set = True,
        no_fillet_top = False,
        no_fillet_bottom = False,
    ):
        super().__init__()

        inner_width = size.inner_width
        inner_length = size.inner_length
        inner_thickness = size.inner_thickness
        wall_thickness = size.wall_thickness
        self.size = size
        self.no_fillet_top = no_fillet_top
        self.no_fillet_bottom = no_fillet_bottom

        if lid_on_faces != [Face.BOTTOM]:
            # TODO: add support (upddate the correct face in panels_specs)
            # TODO nice-to-have: also add support for multiple lids (faces)
            raise ValueError("lid_on_faces: only value supported for now is [BOTTOM], got " + str(lid_on_faces))

        self.frame = (
            cq.Workplane("front")
                .box(inner_width - 4, inner_length - 4, inner_thickness - 4, centered=(True, True, False))
                #.faces("+Z")
                .shell(wall_thickness)
                #.translate([2, 2, 2])
        )
        self.panels_specs = [
            (Face.TOP,    (inner_width-4,  inner_length-4,    wall_thickness),  [0, 0, inner_thickness - wall_thickness],   0.9 ),
            (Face.BOTTOM, (inner_width-4,  inner_length-4,    wall_thickness),  [0, 0, -wall_thickness],    0.9 ),
            (Face.FRONT,  (inner_width-4,  inner_thickness-4, wall_thickness),  [0, -(inner_length/2), inner_thickness/2 - wall_thickness], 0.9 ),
            (Face.BACK,   (inner_width-4,  inner_thickness-4, wall_thickness),  [0, inner_length/2, inner_thickness/2 - wall_thickness],  0.9 ),
            (Face.LEFT,   (inner_length-4, inner_thickness-4, wall_thickness),  [-(inner_width/2), 0, inner_thickness/2 - wall_thickness], 0.9 ),
            (Face.RIGHT,  (inner_length-4, inner_thickness-4, wall_thickness),  [inner_width/2, 0, inner_thickness/2 - wall_thickness],  0.9 ),
        ]

        self.panels = {}
        self.screws_specs = []
        self.screws = []

        for info in self.panels_specs:
            lid_size_error_margin = 0 if info[0] not in lid_on_faces else lid_panel_size_error_margin
            self.panels[info[0]] = Panel(info[0], *info[1], alpha=info[3], lid_size_error_margin=lid_size_error_margin)

        if add_corner_lid_screws:
            self.add_corner_lid_screws(lid_screws_thickness_error_margin, heat_set=lid_screws_heat_set)

    def add_part_to_face(self, face: Face, part_label: str, part: Part, rel_pos=None, abs_pos=None):
        self.panels[face].add(part_label, part, rel_pos, abs_pos)
        return self

    def add_screw(
        self,
        screw_size_category: str = "m3",
        block_thickness: float = 8,
        rel_pos = None,
        abs_pos = None,
        pos_error_margin = 0,
        taper: TaperOptions = TaperOptions.NO_TAPER,
        taper_rotation: float = 0.0,
        screw_provider = DefaultFlatHeadScrewProvider,
        counter_sunk_screw_provider = DefaultFlatHeadScrewProvider,
        with_counter_sunk_block = True
    ):
        # TODO support lid != Face.BOTTOM + refactor

        pos = None
        if rel_pos == None and abs_pos == None:
            raise ValueError("Either rel_pos or abs_pos must be set.")
        elif rel_pos == None:
            pos = (
                abs_pos[0] - self.size.inner_width/2,
                abs_pos[1] - self.size.inner_length/2
            )
        elif abs_pos==None:
            pos = rel_pos

        screw = ScrewBlock(screw_provider, counter_sunk_screw_provider).build(
            screw_size_category,
            block_thickness=block_thickness,
            enclosure_wall_thickness=self.size.wall_thickness,
            taper=taper,
            taper_rotation=taper_rotation,
            with_counter_sunk_block=with_counter_sunk_block
        )
        
        screw["block"] = screw["block"].translate([*pos, pos_error_margin])
        screw["mask"] = screw["mask"].translate([*pos, pos_error_margin])
        if with_counter_sunk_block:
            screw["counter_sunk_block"] = screw["counter_sunk_block"].translate([*pos, pos_error_margin])
            screw["counter_sunk_mask"] = screw["counter_sunk_mask"].translate([*pos, pos_error_margin])
        self.screws.append(screw)
        return screw

    def add_corner_lid_screws(
        self,
        lid_screws_thickness_error_margin,
        screw_size_category: str = "m2",
        heat_set: bool = False
    ):
        # TODO support lid != Face.BOTTOM + refactor

        lid_screws_thickness = 8

        screw_provider = DefaultHeatSetScrewProvider if heat_set else DefaultFlatHeadScrewProvider

        screw_size = ScrewBlock(screw_provider).build(screw_size_category, lid_screws_thickness, self.size.wall_thickness)["size"]  # refactor to avoid this
        pw = self.size.inner_width
        pl = self.size.inner_length
        sw = screw_size[0]
        sl = screw_size[1]
        wt = self.size.wall_thickness
        corners = [
            ( (0+sw/2+wt,  0+sl/2+wt),    0 ),
            ( (0+sw/2+wt,  pl-sl/2-wt),  90 ),
            ( (pw-sw/2-wt, pl-sl/2-wt), 180 ),
            ( (pw-sw/2-wt, 0+sl/2+wt),  270 )
        ]
        for c in corners:
            screw_pos = c[0]
            screw_rotation = c[1]
            screw = self.add_screw(
                screw_size_category=screw_size_category,
                block_thickness=lid_screws_thickness,
                abs_pos=screw_pos,
                pos_error_margin=lid_screws_thickness_error_margin,
                taper=TaperOptions.Z_TAPER_ANGLE,
                taper_rotation=screw_rotation,
                with_counter_sunk_block=True,
                screw_provider=screw_provider
            )
            translate_z = screw["size"][2] + lid_screws_thickness_error_margin + self.size.wall_thickness
            cs_block = screw["counter_sunk_block"].rotate((0, 0, 0), (1, 0, 0), 180).translate([0, 0, translate_z])
            cs_mask = screw["counter_sunk_mask"].rotate((0, 0, 0), (1, 0, 0), 180).translate([0, 0, translate_z])
            self.panels[Face.BOTTOM].add_screw_counter_sunk(cs_block, cs_mask)

    def assemble(self, walls_explosion_factor=1.0, lid_panel_shift=0.0):
        for panel in self.panels.values():
            panel.assemble()

        panels_assembly, panels_masks_assembly = self._build_panels_assembly(walls_explosion_factor, lid_panel_shift)
        frame_assembly = self._build_frame_assembly(panels_masks_assembly)
        lid_screws_assembly = self._build_lid_screws_assembly()

        footprints_assembly = self._build_debug_assembly([("footprint_in", "I"), ("footprint_out", "O")], walls_explosion_factor, lid_panel_shift)
        holes_assembly = self._build_debug_assembly([("hole", "")], walls_explosion_factor, lid_panel_shift)
        other_debug_assembly = self._build_debug_assembly([("other", "")], walls_explosion_factor, lid_panel_shift)

        self.debug = (
            cq.Assembly(None, name="Box")
                .add(footprints_assembly, name="Footprints")
                .add(holes_assembly, name="Holes")
                .add(other_debug_assembly, name="Others")
                .add(panels_masks_assembly, name="Panels masks")
        )
        self.assembly = (
            cq.Assembly(None, name="Box")
                .add(panels_assembly, name="Panels")
                .add(frame_assembly, name="Frame")
                .add(lid_screws_assembly, name="Lid screws", color=cq.Color(0.6, 0.45, 0.8))
                .add(self.debug, name="Debug")
        )
        self.printable_assembly = (
            cq.Assembly(None, name="Box")
                .add(panels_assembly, name="Panels")
                .add(frame_assembly, name="Frame")
                .add(lid_screws_assembly, name="Lid screws", color=cq.Color(0.6, 0.45, 0.8))
        )
        return self

    def _get_debug(self, panel: Panel, assembly_name="combined"):
        if assembly_name in panel.debug_assemblies:
            return panel.debug_assemblies[assembly_name]
        return None

    def _build_panels_assembly(self, walls_explosion_factor, lid_panel_shift):
        a = cq.Assembly(None)
        masks_a = cq.Assembly(None)
        for face, size, position, alpha in self.panels_specs:
            panel: Panel = self.panels[face]
            translated_mask = panel.mask.translate(position)
            masks_a.add(translated_mask, name=(face.label + " mask"), color=cq.Color(0, 1, 0))
            if face == Face.BOTTOM:
                position = (position[0], position[1], position[2] - lid_panel_shift)
            translated_panel = panel.panel.translate(explode(position, walls_explosion_factor))
            a.add(translated_panel, name=face.label)
        return (a, masks_a)

    def _build_frame_assembly(self, panels_masks_assembly) -> cq.Workplane:
        """
        Get the frame of the enclosure (the masks of the panels will be .cut during the assembly).
        In this implemenmtation, it's only possible to remove the fillet
        on the top and bottom of the enclosure (TODO: better implementation needed when lid_on_faces != [Face.BOTTOM] allowed),
        but you can to override the method if you need something more custom (and feel free to contribute ;) )
        """
        # TODO: when implementing the lid on other faces than BOTTOM, will have to remake that code better

        wall_thickness = self.size.wall_thickness

        shell_faces_filter = []
        shell_size = [
            self.size.inner_width - wall_thickness*2,
            self.size.inner_length - wall_thickness*2,
            self.size.inner_thickness - wall_thickness*2
        ]
        shell_translate_z = 0

        if self.no_fillet_top:
            shell_faces_filter.append("+Z")
            shell_size[2] = shell_size[2] + wall_thickness
            shell_translate_z = shell_translate_z# + wall_thickness
        if self.no_fillet_bottom:
            shell_faces_filter.append("-Z")
            shell_size[2] = shell_size[2] + wall_thickness
            shell_translate_z = shell_translate_z - wall_thickness

        no_faces_filter = "+Z and -Z"  # as two faces cannot be true at once--cheeky way to avoid `.faces("")`
        shell_faces = no_faces_filter if len(shell_faces_filter) == 0 else " or ".join(shell_faces_filter)

        shell = (
            cq.Workplane()
                .box(*shell_size, centered=(True, True, False))
                .faces(shell_faces)
                .shell(wall_thickness)
                .translate([0, 0, shell_translate_z])
        )

        return shell.cut(panels_masks_assembly.toCompound())

    def _build_lid_screws_assembly(self):
        a = cq.Assembly(None)
        for idx, s in enumerate(self.screws):
            a.add(s["block"], name=f"Screw #{idx}", color=cq.Color(0.6, 0.45, 0.8))
        return a

    def _cut_panels_masks_from_frame(self, frame: cq.Workplane) -> cq.Workplane:
        for face, size, position, alpha in self.panels_specs:
            panel: Panel = self.panels[face]
            translated_mask = panel.mask.translate(position)
            frame = frame.cut(translated_mask)
        return frame

    def _build_debug_assembly(self, assemblies_specs, walls_explosion_factor, lid_panel_shift):
        a = cq.Assembly(None)
        for face, size, position, alpha in self.panels_specs:
            if face == Face.BOTTOM:
                position = (position[0], position[1], position[2] - lid_panel_shift)
            panel: Panel = self.panels[face]
            for assembly_type, assembly_name_suffix in assemblies_specs:
                debug_assembly = self._get_debug(panel, assembly_type)
                if debug_assembly != None:
                    translated_debug = debug_assembly.translate(explode(position, walls_explosion_factor))
                    a.add(translated_debug, name=(f"{face.label} {assembly_name_suffix}"))
        return a