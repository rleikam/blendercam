from ...simple import addToGroup
from bpy.types import Operator
import bpy

class AddOrientation(Operator):
    """Add orientation to cam operation, for multiaxis operations"""
    bl_idname = "scene.cam_orientation_add"
    bl_label = "Add orientation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = bpy.context.scene
        activeOperationIndex = scene.cam_active_operation
        operation = scene.cam_operations[activeOperationIndex]
        gname = operation.name + '_orientations'
        bpy.ops.object.empty_add(type='ARROWS')

        oriob = bpy.context.active_object
        oriob.empty_draw_size = 0.02  # 2 cm

        addToGroup(oriob, gname)
        oriob.name = 'ori_' + operation.name + '.' + str(len(bpy.data.collections[gname].objects)).zfill(3)

        return {'FINISHED'}