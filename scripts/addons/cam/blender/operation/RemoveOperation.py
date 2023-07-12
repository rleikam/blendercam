from bpy.types import Operator
from bpy.props import IntProperty

class RemoveOperation(Operator):
    """Remove CAM operation"""
    bl_idname = "scene.cam_operation_remove"
    bl_label = "Remove CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    operationIndex: IntProperty()

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = context.scene

        scene.cam_operations.remove(self.operationIndex)
        if scene.cam_active_operation > 0:
            scene.cam_active_operation -= 1

        return {'FINISHED'}