from bpy.types import Operator
from bpy.props import StringProperty

class ExpandOperation(Operator):
    bl_idname = "object.expand_operation"
    bl_label = "Expand operation"
    bl_options = {'REGISTER'}

    operationName: StringProperty()
    expansionName: StringProperty()

    def execute(self, context):
        foundOperationExpansion = (
            operationExpansion for operationExpansion in context.scene.cam_operation_expansions
            if operationExpansion.operationName == self.operationName
        )

        operationExpansion = next(foundOperationExpansion)
        operationExpansion.operationCollapsed = not operationExpansion.operationCollapsed

        return {'FINISHED'}