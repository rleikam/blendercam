import bpy, math
from bpy.props import FloatProperty, EnumProperty, BoolProperty
from ...constants import *


class PackObjectsSettings(bpy.types.PropertyGroup):
    """stores all data for machines"""
    sheet_fill_direction: EnumProperty(name='Fill direction',
                                       items=(('X', 'X', 'Fills sheet in X axis direction'),
                                              ('Y', 'Y', 'Fills sheet in Y axis direction')),
                                       description='Fill direction of the packer algorithm',
                                       default='Y')
    
    sheet_x: FloatProperty(name="X size", description="Sheet size", min=0.001, max=10, default=0.5,
                           precision=PRECISION, unit="LENGTH")
    
    sheet_y: FloatProperty(name="Y size", description="Sheet size", min=0.001, max=10, default=0.5,
                           precision=PRECISION, unit="LENGTH")
    
    distance: FloatProperty(name="Minimum distance",
                            description="minimum distance between objects(should be at least cutter diameter!)",
                            min=0.001, max=10, default=0.01, precision=PRECISION, unit="LENGTH")
    
    tolerance: FloatProperty(name="Placement Tolerance",
                             description="Tolerance for placement: smaller value slower placemant",
                             min=0.001, max=0.02, default=0.005, precision=PRECISION, unit="LENGTH")
    
    rotate: BoolProperty(name="enable rotation", description="Enable rotation of elements", default=True)
    
    rotate_angle: FloatProperty(name="Placement Angle rotation step",
                                description="bigger rotation angle,faster placemant", default=0.19635 * 4,
                                min=math.pi/180,
                                max=math.pi, precision=5,
                                subtype="ANGLE", unit="ROTATION")