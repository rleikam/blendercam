from cam import bpy

from bpy.types import Panel

class CurveCreatorPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_idname = "CAM_PT_curve_creator"
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_label = "Curve CAM Creators"
    bl_option = 'DEFAULT_CLOSED'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.curve_plate")
        layout.operator("object.curve_drawer")
        layout.operator("object.curve_mortise")
        layout.operator("object.curve_interlock")
        layout.operator("object.curve_puzzle")
        layout.operator("object.sine")
        layout.operator("object.lissajous")
        layout.operator("object.hypotrochoid")
        layout.operator("object.customcurve")
        layout.operator("object.curve_hatch")
        layout.operator("object.curve_gear")
        layout.operator("object.curve_flat_cone")