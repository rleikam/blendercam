from bpy.types import PropertyGroup
from bpy.props import FloatProperty, BoolProperty
from ...constants import *

class SliceObjectProperties(PropertyGroup):
    
    slice_distance: FloatProperty(
        name="Slicing distance",
        description="Slices distance in z, should be most often thickness of plywood sheet.",
        min=0.001,
        max=10,
        default=0.005,
        precision=PRECISION,
        unit="LENGTH"
    )
    
    slice_above0: BoolProperty(
        name = "Slice above 0",
        description = "Only slice model above 0",
        default = False
    )

    slice_3d: BoolProperty(
        name = "3D slice",
        description = "For 3D carving",
        default = False
    )

    indexes: BoolProperty(
        name = "Add indexes",
        description = "Adds index text of layer + index",
        default = True
    )