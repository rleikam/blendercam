import bpy
from bpy.types import Panel

from ..operation import AddChain
from .ButtonsPanel import ButtonsPanel
from ..list.Chains import Chains

class ChainsPanel(ButtonsPanel, Panel):
    """CAM chains panel"""
    bl_label = "Chains and operations"
    bl_idname = "CAM_PT_chains"
    bl_options = {"HIDE_HEADER"}

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout

        scene = bpy.context.scene

        column = layout.column(align=True)
        column.operator(AddChain.bl_idname, icon='ADD', text="Add chain")
        column.template_list(Chains.bl_idname, '', scene, "cam_chains", scene, 'cam_active_chain', rows=2)