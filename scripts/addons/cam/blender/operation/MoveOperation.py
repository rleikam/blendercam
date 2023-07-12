from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty
import bpy

class MoveOperation(Operator):
    """Move CAM operation"""
    bl_idname = "scene.cam_operation_move"
    bl_label = "Move CAM operation in list"
    bl_options = {'REGISTER', 'UNDO'}

    direction: EnumProperty(name='direction',
                            items=(('UP', 'Up', ''), ('DOWN', 'Down', '')),
                            description='direction', default='DOWN')

    operationIndex: IntProperty(name="OperationIndex")

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        operations = bpy.context.scene.cam_operations

        if self.direction == 'UP':
            if self.operationIndex > 0:
                operations.move(self.operationIndex, self.operationIndex - 1)

        else:
            if self.operationIndex < len(operations) - 1:
                operations.move(self.operationIndex, self.operationIndex + 1)

        return {'FINISHED'}