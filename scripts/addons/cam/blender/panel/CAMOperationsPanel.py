import bpy
from bpy.props import *
from bpy.types import Panel

from .CAMButtonsPanel import CAMButtonsPanel
from ..list.CAMULOperations import CAMULOperations

from ..operation.CamOperationAdd import CamOperationAdd

from ..menu.CAMOperationMTPresets import CAMOperationMTPresets

class CAMOperationsPanel(CAMButtonsPanel, Panel):
    """CAM operations panel"""
    bl_label = "Operations"
    bl_idname = "WORLD_PT_CAM_OPERATIONS"
    bl_options = {"HIDE_HEADER"}
    
    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    # Main draw function
    def draw(self, context):
        self.draw_operations_list()

        if (not self.has_operations()): return
        if self.active_op is None: return

        self.draw_presets()

        sub = self.layout.column()
        sub.active = not self.active_op.computing

    # Draw the list of operations and the associated buttons:
    # create, delete, duplicate, reorder
    def draw_operations_list(self):
        column = self.layout.column(align=True)

        column.operator(CamOperationAdd.bl_idname, icon='ADD', text="Add operation")
        column.template_list(CAMULOperations.__name__, '', bpy.context.scene, "cam_operations", bpy.context.scene, 'cam_active_operation')

    # Draw the list of preset operations, and preset add and remove buttons
    def draw_presets(self):
        row = self.layout.row(align=True)
        row.menu(CAMOperationMTPresets.__name__, text=CAMOperationMTPresets.bl_label)
        row.operator("render.cam_preset_operation_add", text="", icon='ADD')
        row.operator("render.cam_preset_operation_add", text="", icon='REMOVE').remove_active = True

    # Draw Operation options:
    # Remove redundant points (optimizes operation)
    # Use modifiers of the object
    # Hide all other paths
    # Parent path to object (?)