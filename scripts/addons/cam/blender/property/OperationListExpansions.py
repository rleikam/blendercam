from bpy.types import PropertyGroup
from bpy.props import BoolProperty

class OperationListExpansions(PropertyGroup):
    operationCollapsed: BoolProperty(default=True)