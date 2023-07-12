from bpy.types import Menu

class ToolPresetsMenu(Menu):
    bl_label = "Tool presets"
    preset_subdir = "cam_cutters"
    preset_operator = "script.execute_preset"
    bl_idname = "CAM_MT_tool_presets"
    draw = Menu.draw_preset