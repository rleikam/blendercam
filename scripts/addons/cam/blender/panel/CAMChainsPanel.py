import bpy
from ..operation import CamChainAdd
from .CAMButtonsPanel import CAMButtonsPanel
from ..list.CAMULChains import CAMULChains

from bpy.types import Panel

class CAMChainsPanel(CAMButtonsPanel, Panel):
    """CAM chains panel"""
    bl_label = "Chains and operations"
    bl_idname = "WORLD_PT_CAM_CHAINS"
    bl_options = {"HIDE_HEADER"}

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout

        scene = bpy.context.scene

        column = layout.column(align=True)
        column.operator(CamChainAdd.bl_idname, icon='ADD', text="Add chain")
        column.template_list(CAMULChains.__name__, '', scene, "cam_chains", scene, 'cam_active_chain', rows=2)