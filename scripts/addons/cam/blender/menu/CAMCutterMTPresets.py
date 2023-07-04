from bpy.types import Menu

class CAMCutterMTPresets(Menu):
    bl_label = "Cutter presets"
    preset_subdir = "cam_cutters"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset