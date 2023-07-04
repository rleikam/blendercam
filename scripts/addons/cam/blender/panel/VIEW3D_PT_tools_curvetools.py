from cam import bpy

from bpy.types import Panel

class VIEW3D_PT_tools_curvetools(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_label = "Curve CAM Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.curve_boolean")
        layout.operator("object.convex_hull")
        layout.operator("object.curve_intarsion")
        layout.operator("object.curve_overcuts")
        layout.operator("object.curve_overcuts_b")
        layout.operator("object.silhouete")
        layout.operator("object.silhouete_offset")
        layout.operator("object.curve_remove_doubles")
        layout.operator("object.mesh_get_pockets")