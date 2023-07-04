from ...bridges import addAutoBridges
from bpy.types import Operator
import bpy

class CamBridgesAdd(Operator):
    """Add bridge objects to curve"""
    bl_idname = "scene.cam_bridges_add"
    bl_label = "Add bridges"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = bpy.context.scene
        activeOperationIndex = scene.cam_active_operation
        operation = scene.cam_operations[activeOperationIndex]
        addAutoBridges(operation)
        return {'FINISHED'}