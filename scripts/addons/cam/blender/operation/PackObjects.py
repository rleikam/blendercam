import bpy
from ...pack import packCurves
from bpy.types import Operator

class PackObjects(Operator):
    bl_idname = "object.cam_pack_objects"
    bl_label = "Pack curves on sheet"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')     # force object mode
        packCurves()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout