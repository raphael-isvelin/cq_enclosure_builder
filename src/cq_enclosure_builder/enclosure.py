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

from typing import List, Dict, Union, Tuple
from typing_extensions import Self

import cadquery as cq
from cadquery import exporters

from cq_enclosure_builder import Part, Panel, PanelSize, Face, ProjectInfo
from cq_enclosure_builder.parts.common.screw_block import ScrewBlock, TaperOptions
from cq_enclosure_builder.parts.common.screws_providers import DefaultScrewProvider, DefaultHeatSetScrewProvider
from cq_enclosure_builder.parts.common.screws_providers import LargeBlockFlatHeadScrewProvider, LargeBlockHeatSetScrewProvider
from cq_enclosure_builder.parts.support.skirt import SkirtPart


def explode(pos_array, walls_explosion_factor=2.0):
    return [x * walls_explosion_factor for x in pos_array]


class EnclosureSize:
    def __init__(self, outer_width, outer_length, outer_thickness, wall_thickness):
        self.outer_width = outer_width
        self.outer_length = outer_length
        self.outer_thickness = outer_thickness
        self.inner_width = outer_width - wall_thickness*2
        self.inner_length = outer_length - wall_thickness*2
        self.inner_thickness = outer_thickness - wall_thickness*2
        self.wall_thickness = wall_thickness


class Enclosure:
    EXPORT_FOLDER: str = "stls"

    PRINTABLE_FRAME: str = "frame"
    PRINTABLE_SCREWS: str = "screws"
    PRINTABLE_LID_SUPPORT: str = "lid_support"

    LID_SCREWS_COLOR: Tuple[float, float, float] = (0.6, 0.45, 0.8)
    LID_SUPPORT_COLOR: Tuple[float, float, float] = (0.65, 0.5, 0.85)
    CORNER_LID_SCREWS_THICKNESS: float = 8
    TOP_PANEL_SUPPORT_COLOR: Tuple[float, float, float] = (0.65, 0.5, 0.85)

    def __init__(
        self,
        size: EnclosureSize,
        project_info: ProjectInfo = ProjectInfo(),
        lid_on_faces: List[Face] = [Face.BOTTOM],
        lid_panel_size_error_margin: float = 0.8,  # meaning the lid is `margin` smaller than the hole on both width and length
        lid_thickness_error_margin: float = 0.4,  # if >0, the lid screws and support will be slightly sunk in the enclosure
        add_corner_lid_screws: bool = True,
        add_lid_support: bool = True,
        add_top_support: bool = True,
        lid_screws_heat_set: bool = True,
        lid_screws_size_category: str = "m3",
        lid_screws_large_block_offcentered_hole: bool = True,
        lid_panel_add_chamfer: bool = True,
        no_fillet_top: bool = False,
        no_fillet_bottom: bool = False,
        backpanel_face: Face = None,
        backpanel_size: Tuple[float, float] = None,
        backpanel_thickness: float = 0.7,
        backpanel_pos: Tuple[float, float, float] = None,
        backpanel_tapered_top: bool = True,
        backpanel_screws_pos = [],
        backpanel_screw_diameter = 2.3,
    ):
        if lid_on_faces != [Face.BOTTOM]:
            # TODO: add support for lid != BOTTOM; see issue #2
            # TODO nice-to-have: also add support for multiple lids (faces); see issue #3
            raise ValueError("lid_on_faces: only value supported for now is [BOTTOM], got " + str(lid_on_faces))

        super().__init__()

        outer_width = size.outer_width
        outer_length = size.outer_length
        outer_thickness = size.outer_thickness
        wall_thickness = size.wall_thickness
        self.size = size
        self.project_info = project_info
        self.no_fillet_top = no_fillet_top
        self.no_fillet_bottom = no_fillet_bottom

        self.frame: Union[cq.Assembly, None] = None
        self.panels_specs = [
            (Face.TOP,    (outer_width-wall_thickness*2,  outer_length-wall_thickness*2,    wall_thickness),  [0, 0, outer_thickness - wall_thickness],   0.9 ),
            (Face.BOTTOM, (outer_width-wall_thickness*2,  outer_length-wall_thickness*2,    wall_thickness),  [0, 0, -wall_thickness],    0.9 ),
            (Face.FRONT,  (outer_width-wall_thickness*2,  outer_thickness-wall_thickness*2, wall_thickness),  [0, -(outer_length/2), outer_thickness/2 - wall_thickness], 0.9 ),
            (Face.BACK,   (outer_width-wall_thickness*2,  outer_thickness-wall_thickness*2, wall_thickness),  [0, outer_length/2, outer_thickness/2 - wall_thickness],  0.9 ),
            (Face.LEFT,   (outer_length-wall_thickness*2, outer_thickness-wall_thickness*2, wall_thickness),  [-(outer_width/2), 0, outer_thickness/2 - wall_thickness], 0.9 ),
            (Face.RIGHT,  (outer_length-wall_thickness*2, outer_thickness-wall_thickness*2, wall_thickness),  [outer_width/2, 0, outer_thickness/2 - wall_thickness],  0.9 ),
        ]

        self.panels = {}
        self.screws_specs = []
        self.screws = []
        self.lid_screws_assembly: cq.Assembly = None
        self.lid_support: cq.Workplane = None
        self.lid_thickness_error_margin = lid_thickness_error_margin
        self.add_lid_support: bool = add_lid_support

        for info in self.panels_specs:
            lid_size_error_margin = 0 if info[0] not in lid_on_faces else lid_panel_size_error_margin
            add_chamfer = False if info[0] not in lid_on_faces else lid_panel_add_chamfer

            if info[0] == backpanel_face:
                self.panels[info[0]] = Panel(
                    info[0],
                    PanelSize(*info[1]),
                    alpha=info[3],
                    lid_size_error_margin=lid_size_error_margin,
                    project_info=self.project_info,
                    add_chamfer=add_chamfer,
                    backpanel_size=backpanel_size,
                    backpanel_thickness=backpanel_thickness,
                    backpanel_pos=backpanel_pos,
                    backpanel_tapered_top=backpanel_tapered_top,
                    backpanel_screws_pos=backpanel_screws_pos,
                    backpanel_screw_diameter=backpanel_screw_diameter,
                )
            else:
                self.panels[info[0]] = Panel(
                    info[0],
                    PanelSize(*info[1]),
                    alpha=info[3],
                    lid_size_error_margin=lid_size_error_margin,
                    project_info=self.project_info,
                    add_chamfer=add_chamfer,
                )

        # Lid should be created before the screws are added (cut the screws' masks from the lid)
        if add_lid_support:
            self._build_lid_support()
        if add_corner_lid_screws:
            self.add_corner_lid_screws(
                screw_size_category=lid_screws_size_category,
                heat_set=lid_screws_heat_set,
                large_block_offcentered_hole=lid_screws_large_block_offcentered_hole,
            )

        if add_top_support:
            skirt = SkirtPart(
                enclosure_wall_thickness=size.wall_thickness,
                width=(size.outer_width - size.wall_thickness*2),
                length=(size.outer_length - size.wall_thickness*2))
            self.add_part_to_face(Face.TOP, "Skirt", skirt, rel_pos=(0, 0), color=Enclosure.TOP_PANEL_SUPPORT_COLOR)

        self.main_printables_config: Dict[str, List[Union[Face, str]]] = {
            "box": [Face.TOP, Face.LEFT, Face.RIGHT, Face.FRONT, Face.BACK,
                    Enclosure.PRINTABLE_FRAME, Enclosure.PRINTABLE_SCREWS, Enclosure.PRINTABLE_LID_SUPPORT],
            "lid": [Face.BOTTOM],
        }
        self.printables: Dict[str, Tuple[cq.Workplane, Tuple[float, float]]] = {}
        self.all_printables_assembly = cq.Assembly()

    def export_printables(self) -> None:
        for name, item in self.printables.items():
            wp = item[0]
            file_path = self._build_printable_file_path(name)
            print(f"Exporting '{name}' to '{file_path}'")
            exporters.export(wp, file_path)
        file_path = self._build_printable_file_path("ALL")
        print(f"Exporting 'ALL' to '{file_path}'")
        exporters.export(self.all_printables_assembly.toCompound(), file_path)

    def _assemble_printables(self) -> Self:
        for name, elements in self.main_printables_config.items():
            printable_a = cq.Assembly()
            for e in elements:
                if isinstance(e, Face.FaceInfo):
                    printable_a.add(self.panels[e].panel, name=str(e.label))
                elif e == Enclosure.PRINTABLE_FRAME:
                    printable_a.add(self.frame, name=e)
                elif e == Enclosure.PRINTABLE_SCREWS:
                    printable_a.add(self.lid_screws_assembly, name=e)
                elif e == Enclosure.PRINTABLE_LID_SUPPORT:
                    printable_a.add(self.lid_support, name=e)
                else:
                    raise ValueError("Unknown printable element " + str(e))
            printable_wp = printable_a.toCompound()
            printable_size = None
            # TODO make a bit more generic
            if name == "box":  # the box should be printed top-down
                printable_wp = (printable_wp
                    .rotate((0, 0, 0), (0, 1, 0), 180)
                    .translate([0, 0, self.size.outer_thickness - self.size.wall_thickness]))
                printable_size = (self.size.outer_width, self.size.outer_length)
            elif name == "lid":
                printable_wp = printable_wp.translate([0, 0, self.size.wall_thickness])
                lid_panel = self.panels[Face.BOTTOM]  # TODO unhardcode BOTTOM lid panel; see issue #2
                printable_size = (lid_panel.true_size.width, lid_panel.true_size.length)
            else:
                raise ValueError(f"Unsupported printable '{name}', you might run into alignment issues when displaying all_printables_assembly")
            self.printables[name] = (printable_wp, printable_size)

        self.all_printables_assembly = cq.Assembly(name="All printables")
        shift_by = 0
        printables_spacing = 8
        for name, item in self.printables.items():
            wp = item[0]
            printable_size = item[1]
            self.all_printables_assembly.add(wp.translate([0, shift_by + printable_size[1]/2, 0]), name=name)
            shift_by = shift_by + printable_size[1] + printables_spacing

    def add_part_to_face(
        self,
        face: Face.FaceInfo,
        part_label: str,
        part: Part,
        rel_pos: Tuple[float, float] = None,
        abs_pos: Tuple[float, float] = None,
        color: Tuple[float, float, float] = None,
        alpha: float = 1.0,
    ) -> Self:
        self.panels[face].add(part_label, part, rel_pos, abs_pos, color, alpha)
        return self

    def add_screw(
        self,
        screw_size_category: str = "m3",
        block_thickness: float = 8,
        rel_pos: Tuple[float, float] = None,
        abs_pos: Tuple[float, float] = None,
        pos_error_margin: float = 0,
        taper: TaperOptions = TaperOptions.NO_TAPER,
        taper_rotation: float = 0.0,
        screw_provider = DefaultScrewProvider,
        counter_sunk_screw_provider = DefaultScrewProvider,
        with_counter_sunk_block: bool = True,
        hole_position: Tuple[float, float] = (0, 0),
        counter_sunk_extrude_depth: float = 2.0,
    ) -> ScrewBlock:
        # TODO support lid != Face.BOTTOM + refactor; see issue #2

        pos = None
        if rel_pos == None and abs_pos == None:
            raise ValueError("Either rel_pos or abs_pos must be set.")
        elif rel_pos == None:
            pos = (
                abs_pos[0] - self.size.outer_width/2,
                abs_pos[1] - self.size.outer_length/2
            )
        elif abs_pos==None:
            pos = rel_pos

        screw = ScrewBlock(screw_provider, counter_sunk_screw_provider).build(
            screw_size_category,
            block_thickness=block_thickness,
            enclosure_wall_thickness=self.size.wall_thickness,
            taper=taper,
            taper_rotation=taper_rotation,
            with_counter_sunk_block=with_counter_sunk_block,
            hole_position=hole_position,
            counter_sunk_extrude_depth=counter_sunk_extrude_depth,
            counter_sunk_negative_mask_error_margin=pos_error_margin,
        )
        
        screw["block"] = screw["block"].translate([*pos, pos_error_margin])
        screw["mask"] = screw["mask"].translate([*pos, pos_error_margin])
        if with_counter_sunk_block:
            screw["counter_sunk_block"] = screw["counter_sunk_block"].translate([*pos, pos_error_margin])
            screw["counter_sunk_mask"] = screw["counter_sunk_mask"].translate([*pos, pos_error_margin])

            translate_z = screw["size"][2] + self.lid_thickness_error_margin + self.size.wall_thickness
            cs_block = screw["counter_sunk_block"].rotate((0, 0, 0), (1, 0, 0), 180).translate([0, 0, translate_z])
            cs_mask = screw["counter_sunk_mask"].rotate((0, 0, 0), (1, 0, 0), 180).translate([0, 0, translate_z])
            self.panels[Face.BOTTOM].add_screw_counter_sunk(cs_block, cs_mask)

        self.screws.append(screw)
        if self.add_lid_support:
            self.lid_support = self.lid_support.cut(screw["mask"])
        return screw

    def add_corner_lid_screws(
        self,
        screw_size_category: str = "m3",
        heat_set: bool = False,
        large_block_offcentered_hole: bool = True,
    ) -> None:
        # TODO support lid != Face.BOTTOM + refactor; see issue #2

        lid_screws_thickness = Enclosure.CORNER_LID_SCREWS_THICKNESS

        screw_provider = DefaultHeatSetScrewProvider if heat_set else DefaultScrewProvider
        counter_sunk_screw_provider = DefaultScrewProvider
        if large_block_offcentered_hole:
            screw_provider = LargeBlockHeatSetScrewProvider if heat_set else LargeBlockFlatHeadScrewProvider
            counter_sunk_screw_provider = LargeBlockFlatHeadScrewProvider

        screw_size = ScrewBlock(screw_provider).build(screw_size_category, lid_screws_thickness, self.size.wall_thickness)["size"]  # refactor to avoid this
        pw = self.size.outer_width
        pl = self.size.outer_length
        sw = screw_size[0]
        sl = screw_size[1]
        wt = self.size.wall_thickness
        corners = [
            ( (0+sw/2+wt,  0+sl/2+wt),    0,  (1.5, 1.5)   ),
            ( (0+sw/2+wt,  pl-sl/2-wt),  90,  (1.5, -1.5)  ),
            ( (pw-sw/2-wt, pl-sl/2-wt), 180,  (-1.5, -1.5) ),
            ( (pw-sw/2-wt, 0+sl/2+wt),  270,  (-1.5, 1.5)  )
        ]
        for c in corners:
            screw_pos = c[0]
            screw_rotation = c[1]
            hole_position = c[2] if large_block_offcentered_hole else (0, 0)
            screw = self.add_screw(
                screw_provider=screw_provider,
                counter_sunk_screw_provider=counter_sunk_screw_provider,
                screw_size_category=screw_size_category,
                block_thickness=lid_screws_thickness,
                abs_pos=screw_pos,
                pos_error_margin=self.lid_thickness_error_margin,
                taper=TaperOptions.Z_TAPER_ANGLE,
                taper_rotation=screw_rotation,
                with_counter_sunk_block=True,
                hole_position=hole_position,
                counter_sunk_extrude_depth=2.0,
            )
            translate_z = screw["size"][2] + self.lid_thickness_error_margin + self.size.wall_thickness
            cs_block = screw["counter_sunk_block"].mirror("XY").translate([0, 0, translate_z])
            cs_mask = screw["counter_sunk_mask"].mirror("XY").translate([0, 0, translate_z])
            self.panels[Face.BOTTOM].add_screw_counter_sunk(cs_block, cs_mask)

    def _build_lid_support(self) -> None:
        width = self.size.outer_width - self.size.wall_thickness*2
        length = self.size.outer_length - self.size.wall_thickness*2
        self.lid_support = (
            SkirtPart(self.size.wall_thickness, width, length, skirt_size=(2, 2), base_size=1)
                .part
                .translate([0, 0, -self.size.wall_thickness + self.lid_thickness_error_margin])
        )

    def assemble(
        self,
        walls_explosion_factor: float = 1.0,
        lid_panel_shift: float = 0.0
    ) -> Self:
        for panel in self.panels.values():
            panel.assemble()

            for printable in panel.additional_printables:
                printable_name = printable[0]
                printable_size = printable[1]
                self.printables[printable_name] = (printable[2], printable_size)

        panels_assembly, panels_masks_assembly = self._build_panels_assembly(walls_explosion_factor, lid_panel_shift)
        self.panels_assembly = panels_assembly
        self.panels_masks_assembly = panels_masks_assembly
        self.frame = self._build_frame_assembly(panels_masks_assembly)
        self.lid_screws_assembly = self._build_lid_screws_assembly()

        footprints_assembly = self._build_debug_assembly([("footprint_in", "I"), ("footprint_out", "O")], walls_explosion_factor, lid_panel_shift)
        holes_assembly = self._build_debug_assembly([("hole", "")], walls_explosion_factor, lid_panel_shift)
        other_debug_assembly = self._build_debug_assembly([("other", "")], walls_explosion_factor, lid_panel_shift)
        self.footprints_assembly = footprints_assembly
        self.holes_assembly = holes_assembly
        self.other_debug_assembly = other_debug_assembly

        self._assemble_printables();

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
                .add(self.frame, name="Frame")
                .add(self.lid_screws_assembly, name="Lid screws", color=cq.Color(*Enclosure.LID_SCREWS_COLOR))
                .add(self.lid_support, name="Lid support", color=cq.Color(*Enclosure.LID_SUPPORT_COLOR))
        )
        self.assembly_with_debug = (
            cq.Assembly(name="Assembly with debug objects")
                .add(self.assembly, name="Assembly")
                .add(self.debug, name="Debug")
        )
        return self

    def _build_printable_file_path(self, printable_name: str) -> str:
        project_name = self.project_info.name.lower().replace(" ", "_")
        version = self.project_info.version
        return f"{Enclosure.EXPORT_FOLDER}/{project_name}-{printable_name}-v{version}.stl"

    def _get_debug(self, panel: Panel, assembly_name="combined") -> Union[cq.Assembly, None]:
        if assembly_name in panel.debug_assemblies:
            return panel.debug_assemblies[assembly_name]
        return None

    def _build_panels_assembly(self, walls_explosion_factor, lid_panel_shift) -> Tuple[cq.Assembly, cq.Assembly]:
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
            self.size.outer_width - wall_thickness*2,
            self.size.outer_length - wall_thickness*2,
            self.size.outer_thickness - wall_thickness*2
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

    def _build_lid_screws_assembly(self) -> cq.Assembly:
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

    def _build_debug_assembly(self, assemblies_specs, walls_explosion_factor, lid_panel_shift) -> cq.Assembly:
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