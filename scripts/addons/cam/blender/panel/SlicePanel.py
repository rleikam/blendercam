import bpy
from .ButtonsPanel import ButtonsPanel

from bpy.types import Panel

class SlicePanel(ButtonsPanel, Panel):
    """CAM slicer panel"""
    bl_label = "Slice model to plywood sheets"
    bl_idname = "CAM_PT_slice"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        settings = scene.cam_slice

        layout.operator("object.cam_slice_objects")
        layout.prop(settings, 'slice_distance')
        layout.prop(settings, 'slice_above0')
        layout.prop(settings, 'slice_3d')
        layout.prop(settings, 'indexes')