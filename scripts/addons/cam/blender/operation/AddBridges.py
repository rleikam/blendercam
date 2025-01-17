from ...bridges import addAutoBridges
from bpy.types import Operator
from bpy.props import IntProperty

class AddBridges(Operator):
    """Add bridge objects to curve"""
    bl_idname = "scene.cam_bridges_add"
    bl_label = "Add bridges"
    bl_options = {'REGISTER', 'UNDO'}

    operationIndex: IntProperty()

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = context.scene
        operation = scene.cam_operations[self.operationIndex]
        addAutoBridges(operation)
        return {'FINISHED'}