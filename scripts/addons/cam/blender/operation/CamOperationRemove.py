from bpy.types import Operator
import bpy
from ..property.callback import was_hidden_dict

class CamOperationRemove(Operator):
    """Remove CAM operation"""
    bl_idname = "scene.cam_operation_remove"
    bl_label = "Remove CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = context.scene
        try:
            if len(scene.cam_operations) == 0: return {'CANCELLED'}
            active_op = scene.cam_operations[scene.cam_active_operation]
            active_op_object = bpy.data.objects[active_op.name]
            scene.objects.active = active_op_object
            bpy.ops.object.delete(True)
        except:
            pass

        activeOperation = scene.cam_operations[scene.cam_active_operation]
        print(was_hidden_dict)
        if activeOperation.name in was_hidden_dict:
            del was_hidden_dict[activeOperation.name]

        scene.cam_operations.remove(scene.cam_active_operation)
        if scene.cam_active_operation > 0:
            scene.cam_active_operation -= 1

        return {'FINISHED'}