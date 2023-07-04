from bpy.types import PropertyGroup
from bpy.props import FloatProperty, BoolProperty
from ...constants import *

class SliceObjectsSettings(PropertyGroup):
    """stores all data for machines"""
    slice_distance: FloatProperty(name="Slicing distance",
                                  description="slices distance in z, should be most often thickness of plywood sheet.",
                                  min=0.001, max=10, default=0.005, precision=PRECISION, unit="LENGTH")
    
    slice_above0: BoolProperty(name="Slice above 0", description="only slice model above 0", default=False)

    slice_3d: BoolProperty(name="3d slice", description="for 3d carving", default=False)

    indexes: BoolProperty(name="add indexes", description="adds index text of layer + index", default=True)