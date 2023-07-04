from cam import pack
from bpy.types import Operator
import bpy

class CamPackObjects(Operator):
    """calculate all CAM paths"""
    bl_idname = "object.cam_pack_objects"
    bl_label = "Pack curves on sheet"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')     # force object mode
        obs = bpy.context.selected_objects
        pack.packCurves()
        # layout.
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout