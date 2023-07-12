from bpy.types import PropertyGroup
from bpy.props import StringProperty

class OperationReferenceProperties(PropertyGroup):
    name: StringProperty(
        name = "Operation name",
        default = "Operation"
    )

    computing = False