from bpy.types import Menu

class CAMOperationMTPresets(Menu):
    bl_label = "Operation presets"
    preset_subdir = "cam_operations"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset