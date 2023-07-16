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
        column = self.layout.column(align=True)
        column.operator("object.curve_plate")
        column.operator("object.curve_drawer")
        column.operator("object.curve_mortise")
        column.operator("object.curve_interlock")
        column.operator("object.curve_puzzle")
        column.operator("object.sine")
        column.operator("object.lissajous")
        column.operator("object.hypotrochoid")
        column.operator("object.customcurve")
        column.operator("object.curve_hatch")
        column.operator("object.curve_gear")
        column.operator("object.curve_flat_cone")