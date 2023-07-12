from bpy.types import Panel
from ..operation.WM_OT_gcode_import import WM_OT_gcode_import

class CustomPanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_label = "Import Gcode"
    bl_idname = "CAM_PT_custom"

    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT',
                                'EDIT_MESH'}  # with this poll addon is visibly even when no object is selected

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        isettings = scene.cam_import_gcode
        layout.prop(isettings, 'output')
        layout.prop(isettings, "split_layers")

        layout.prop(isettings, "subdivide")
        col = layout.column(align=True)
        col = col.row(align=True)
        col.split()
        col.label(text="Segment length")

        col.prop(isettings, "max_segment_size")
        col.enabled = isettings.subdivide
        col.separator()

        col = layout.column()
        col.scale_y = 2.0
        col.operator(WM_OT_gcode_import.bl_idname)