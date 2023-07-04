from bpy.types import Operator
from ...utils import positionObject
import bpy

class CAMMaterialPositionObject(Operator):

    bl_idname = "object.material_cam_position"
    bl_label = "position object for CAM operation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        operation = context.scene.cam_operations[scene.cam_active_operation]
        if operation.object_name in bpy.data.objects:
            positionObject(operation)
        else:
            print('no object assigned')
        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")