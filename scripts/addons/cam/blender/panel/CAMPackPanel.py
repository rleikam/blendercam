import bpy
from .CAMButtonsPanel import CAMButtonsPanel

from bpy.types import Panel

class CAMPackPanel(CAMButtonsPanel, Panel):
    """CAM material panel"""
    bl_label = "Pack curves on sheet"
    bl_idname = "WORLD_PT_CAM_PACK"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        settings = scene.cam_pack
        layout.label(text='warning - algorithm is slow.')
        layout.label(text='only for curves now.')

        layout.operator("object.cam_pack_objects")
        layout.prop(settings, 'sheet_fill_direction')
        layout.prop(settings, 'sheet_x')
        layout.prop(settings, 'sheet_y')
        layout.prop(settings, 'distance')
        layout.prop(settings, 'tolerance')
        layout.prop(settings, 'rotate')
        if settings.rotate:
            layout.prop(settings, 'rotate_angle')