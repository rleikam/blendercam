from bpy.types import Operator
from bpy.props import StringProperty

class ExpandOperation(Operator):
    bl_idname = "object.expand_operation"
    bl_label = "Expand operation"
    bl_options = {'REGISTER'}

    operationName: StringProperty()
    expansionName: StringProperty()

    def execute(self, context):
        foundOperations = (
            operation for operation in context.scene.cam_operations
            if operation.name == self.operationName
        )

        operation = next(foundOperations)
        operation.expansion.operationCollapsed = not operation.expansion.operationCollapsed

        return {'FINISHED'}