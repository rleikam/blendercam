from bpy.types import Operator
from bl_operators.presets import AddPresetBase

class AddMachinePreset(AddPresetBase, Operator):
    """Add a Cam Machine Preset"""
    bl_idname = "render.cam_preset_machine_add"
    bl_label = "Add Machine Preset"
    preset_menu = "CAM_MACHINE_MT_presets"

    preset_defines = [
        "d = bpy.context.scene.cam_machine",
        "s = bpy.context.scene.unit_settings"
    ]

    preset_values = [
        "d.post_processor",
        "s.system",
        "d.use_position_definitions",
        "d.starting_position",
        "d.mtc_position",
        "d.ending_position",
        "d.working_area",
        "d.feedrate_min",
        "d.feedrate_max",
        "d.feedrate_default",
        "d.spindle_min",
        "d.spindle_max",
        "d.spindle_default",
        "d.axis4",
        "d.axis5",
        "d.collet_size",
        "d.output_tool_change",
        "d.output_block_numbers",
        "d.output_tool_definitions",
        "d.output_g43_on_tool_change",
    ]

    preset_subdir = "cam_machines"