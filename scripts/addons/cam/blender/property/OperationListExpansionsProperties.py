from bpy.types import PropertyGroup
from bpy.props import BoolProperty

class OperationListExpansionsProperties(PropertyGroup):
    operationCollapsed: BoolProperty(
        default=True
    )