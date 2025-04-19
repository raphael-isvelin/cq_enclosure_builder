import cadquery as cq

from cq_enclosure_builder.part import Part
from cq_enclosure_builder.parts_factory import register_part


PART_CATEGORY = "usb_a"
PART_ID = "Dual_USB"

"""
Custom dual USB breakout

TODO link to KiCad
"""
@register_part(PART_CATEGORY, PART_ID)
class DualUsbBreakoutPart(Part):

    BOARD_SIZE_XY = (22, 30)

    # Blocks & screws
    BLOCK_THICKNESS = 5
    BLOCKS_SPECS = [
        ( [0, BOARD_SIZE_XY[1]/2-3.5],   (BOARD_SIZE_XY[0], 7) ),
        ( [0, -BOARD_SIZE_XY[1]/2+3.5],  (BOARD_SIZE_XY[0], 7) ),
        ( [BOARD_SIZE_XY[0]/2-1.5, 0],   (3, BOARD_SIZE_XY[1]) ),
        ( [-BOARD_SIZE_XY[0]/2+1.5, 0],  (3, BOARD_SIZE_XY[1]) ),
    ]
    SCREW_DISTANCE = 23
    SCREWS_POSITIONS = [ (0, SCREW_DISTANCE/2), (0, -SCREW_DISTANCE/2) ]
    SCREW_HOLE_SIZE = 2.9

    # USB
    USB_WALL_THICKNESS = 1
    USB_HOLE_SIZE = (14.35, 13.1)
    USB_THICKNESS_AFTER_PCB = 18.585 - 1.6

    # STEP model
    DETAILED_STEP_FILE = "step/dual-USB_breakout.step"
    SIMPLIFIED_STEP_FILE = None
    ULTRA_SIMPLIFIED_STEP_FILE = None
    MODEL_OFFSET = [-BOARD_SIZE_XY[0]/2, -BOARD_SIZE_XY[1]/2, -20.585]# 2.54]

    def __init__(
        self,
        enclosure_wall_thickness: float,
        add_model_to_footprint: bool = True,
        use_simplified_model: bool = False,
        use_ultra_simplified_model: bool = False,
    ):
        try: cls_file = __file__            # regular launch
        except NameError: cls_file = None   # when launched from Jupyter
        super().__init__(
            cls_file,
            PART_CATEGORY,
            PART_ID,
            DualUsbBreakoutPart.DETAILED_STEP_FILE,
            DualUsbBreakoutPart.SIMPLIFIED_STEP_FILE,
            DualUsbBreakoutPart.ULTRA_SIMPLIFIED_STEP_FILE,
            DualUsbBreakoutPart.MODEL_OFFSET,
        )

        block_thickness = DualUsbBreakoutPart.BLOCK_THICKNESS
        usb_thickness_in_wall = enclosure_wall_thickness - DualUsbBreakoutPart.USB_WALL_THICKNESS

        calculated_block_thickness = DualUsbBreakoutPart.USB_THICKNESS_AFTER_PCB - usb_thickness_in_wall
        block_spacer_thickness = calculated_block_thickness - block_thickness

        board_size = (
            DualUsbBreakoutPart.BOARD_SIZE_XY[0],
            DualUsbBreakoutPart.BOARD_SIZE_XY[1] + DualUsbBreakoutPart.BLOCK_THICKNESS,
            enclosure_wall_thickness
        )
        self.size.width, self.size.length, self.size.thickness = board_size

        # Board & mask
        self.part = (
            cq.Workplane("front")
                .box(*board_size, centered=(True, True, False))
            

                .faces(">Z").workplane()
                .move(0, block_thickness/2)
                .rect(16, 11.1+0.6)
                .extrude(-usb_thickness_in_wall, combine="cut")
                .faces(">Z").workplane()
                .move(0, block_thickness/2)
                .rect(12.35+0.6, 15)
                .extrude(-usb_thickness_in_wall, combine="cut")

                .faces(">Z").workplane()
                .move(0, block_thickness/2)
                .rect(*DualUsbBreakoutPart.USB_HOLE_SIZE)
                .cutThruAll()
    
                .add(self.build_blocks(enclosure_wall_thickness, DualUsbBreakoutPart.BLOCKS_SPECS, block_thickness, DualUsbBreakoutPart.SCREW_HOLE_SIZE).translate([0, block_thickness/2, 0]))
                .add(self.build_wedge(enclosure_wall_thickness, block_thickness).translate([0, block_thickness/2, 0]))
        )
        self.mask = (
            cq.Workplane("front")
                .box(*board_size, centered=(True, True, False))
        )

        # Spacer
        self.spacer = self.build_blocks(enclosure_wall_thickness, DualUsbBreakoutPart.BLOCKS_SPECS, block_spacer_thickness, DualUsbBreakoutPart.SCREW_HOLE_SIZE+0.8, block_spacer_thickness).translate([0, 0, -enclosure_wall_thickness])
        
        self.debug_objects.others["spacer"]  = (
            self.spacer
                .translate([0, block_thickness/2, block_thickness + enclosure_wall_thickness])
        )

        # Inside footprint
        self.inside_footprint = (self.size.width, self.size.length)
        self.inside_footprint_thickness = 27.21 - usb_thickness_in_wall
        self.inside_footprint_offset = (0, 0)

        footprint_in = cq.Workplane("front")
        if add_model_to_footprint:
            footprint_in = super().get_step_model(
                use_simplified_model,
                use_ultra_simplified_model,
                [0, self.inside_footprint[1] - block_thickness/2, enclosure_wall_thickness - usb_thickness_in_wall]
            ).rotate((0, 0, 0), (0, 1, 0), 180)
        else:
            footprint_in = (
                cq.Workplane("front")
                    .box(*self.inside_footprint, DualUsbBreakoutPart.USB_THICKNESS_AFTER_PCB, centered=(True, True, False))
                    .translate([0, 0, enclosure_wall_thickness])
            )
        self.debug_objects.footprint.inside  = footprint_in

        # Outside footprint
        self.outside_footprint = (16, 15)
        self.outside_footprint_thickness = 0
        self.outside_footprint_offset = (0, block_thickness/2)
        
        self.debug_objects.footprint.outside = None
        # self.debug_objects.footprint.outside = (
        #     cq.Workplane("front")
        #         .box(*self.outside_footprint, self.outside_footprint_thickness, centered=(True, True, False))
        #         .translate([*self.outside_footprint_offset, -1])
        # )

    def build_blocks(self, enclosure_wall_thickness: float, blocks_specs, block_thickness: float, screw_hole_size: float, screw_hole_depth = None):
        blocks = cq.Workplane("front")
        for specs in blocks_specs:
            pos, sz = specs
            blocks.add(
                cq.Workplane("front")
                    # .faces("<Z").workplane()
                    .move(*pos)
                    .rect(*sz)
                    .extrude(block_thickness)
                    .translate([0, 0, enclosure_wall_thickness])
            )
        if screw_hole_depth is None:
            screw_hole_depth = min(10, block_thickness-1)
        blocks = (
            blocks
                .faces(">Z").workplane()
                .pushPoints(DualUsbBreakoutPart.SCREWS_POSITIONS)
                .hole(screw_hole_size, screw_hole_depth)
        )
        return blocks

    def build_wedge(self, enclosure_wall_thickness: float, block_thickness: float):
        return (
            cq.Workplane("right")
                .polyline([ (0, 0), (-block_thickness, 0), (0, -block_thickness) ])
                .close()
                .extrude(DualUsbBreakoutPart.BOARD_SIZE_XY[0])
                .translate([-DualUsbBreakoutPart.BOARD_SIZE_XY[0]/2, -DualUsbBreakoutPart.BOARD_SIZE_XY[1]/2, enclosure_wall_thickness])
        )