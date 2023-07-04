import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty

class OpReference(PropertyGroup):  # this type is defined just to hold reference to operations for chains
    name: StringProperty(name="Operation name", default="Operation")
    computing = False  # for UiList display