from .CAMButtonsPanel import CAMButtonsPanel
from cam.utils import opencamlib_version

from bpy.types import Panel

class CAMInfoPanel(CAMButtonsPanel, Panel):
    """CAM info panel"""
    bl_label = "CAM info & warnings"
    bl_idname = "WORLD_PT_CAM_INFO"

    bl_options = {"HIDE_HEADER"}
    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    # Display the Info Panel
    def draw(self, context):
        version = opencamlib_version()

        if version is None:
            textVersion = "Opencamlib is not installed"
        else:
            textVersion = f"Opencamlib v{version} installed"

        self.layout.label(text=textVersion)