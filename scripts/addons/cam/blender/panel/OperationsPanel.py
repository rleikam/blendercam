import bpy
from bpy.props import *
from bpy.types import Panel
from ..operation.AddOperationPreset import AddOperationPreset

from .ButtonsPanel import ButtonsPanel
from ..list.OperationList import OperationList

from ..operation.AddOperation import AddOperation

from ..menu.OperationPresetsMenu import OperationPresetsMenu

class OperationsPanel(ButtonsPanel, Panel):
    """CAM operations panel"""
    bl_label = "Operations"
    bl_idname = "CAM_PT_operations"
    bl_options = {"HIDE_HEADER"}
    
    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    # Main draw function
    def draw(self, context):
        self.draw_operations_list()
        self.draw_presets()

    # Draw the list of operations and the associated buttons:
    # create, delete, duplicate, reorder
    def draw_operations_list(self):
        column = self.layout.column(align=True)

        column.operator(AddOperation.bl_idname, icon='ADD', text="Add operation")
        column.template_list(OperationList.bl_idname, '', bpy.context.scene, "cam_operations", bpy.context.scene, 'cam_active_operation')

    # Draw the list of preset operations, and preset add and remove buttons
    def draw_presets(self):
        row = self.layout.row(align=True)
        row.menu(OperationPresetsMenu.bl_idname, text=OperationPresetsMenu.bl_label)
        row.operator(AddOperationPreset.bl_idname, text="", icon='ADD')
        row.operator(AddOperationPreset.bl_idname, text="", icon='REMOVE').remove_active = True

    # Draw Operation options:
    # Remove redundant points (optimizes operation)
    # Use modifiers of the object
    # Hide all other paths
    # Parent path to object (?)