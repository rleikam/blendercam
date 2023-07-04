import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatProperty, EnumProperty


class ImportSettings(PropertyGroup):
    split_layers: BoolProperty(name="Split Layers", description="Save every layer as single Objects in Collection",
                               default=False)
    
    subdivide: BoolProperty(name="Subdivide",
                            description="Only Subdivide gcode segments that are bigger than 'Segment length' ",
                            default=False)
    
    output: EnumProperty(name="output type", items=(
        ('mesh', 'Mesh', 'Make a mesh output'), ('curve', 'Curve', 'Make curve output')), default='curve')
    
    max_segment_size: FloatProperty(name="", description="Only Segments bigger then this value get subdivided",
                                    default=0.001, min=0.0001, max=1.0, unit="LENGTH")