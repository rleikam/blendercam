from bpy.types import Operator
from bpy.props import IntProperty

from bl_operators.presets import AddPresetBase
from..menu import ToolPresetsMenu

class AddToolPreset(AddPresetBase, Operator):
    """Add a Cutter Preset"""
    bl_idname = "render.cam_preset_cutter_add"
    bl_label = "Add Cutter Preset"
    preset_menu = ToolPresetsMenu.bl_idname

    operationIndex: IntProperty()

    preset_defines = [
        "d = bpy.context.scene.cam_operations[self.operationIndex]"
    ]

    preset_values = [
        "d.cutter_id",
        "d.cutter_type",
        "d.cutter_diameter",
        "d.cutter_length",
        "d.cutter_flutes",
        "d.cutter_tip_angle",
        "d.cutter_description",
    ]

    preset_subdir = "cam_cutters"