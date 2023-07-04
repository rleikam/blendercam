from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty

class OperationListExpansions(PropertyGroup):
    operationName: StringProperty()
    operationCollapsed: BoolProperty()