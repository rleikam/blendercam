from bpy.types import Operator
import bpy
from ...slice import sliceObject

class SliceObjects(Operator):
    """Slice a mesh object horizontally"""
    # warning, this is a separate and neglected feature, it's a mess - by now it just slices up the object.
    bl_idname = "object.cam_slice_objects"
    bl_label = "Slice object - usefull for lasercut puzzles e.t.c."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object = context.active_object
        sliceObject(object)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout