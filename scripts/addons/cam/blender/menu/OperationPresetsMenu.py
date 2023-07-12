from bpy.types import Menu

class OperationPresetsMenu(Menu):
    bl_label = "Operation presets"
    preset_subdir = "cam_operations"
    preset_operator = "script.execute_preset"
    bl_idname = "CAM_MT_operation_presets"
    draw = Menu.draw_preset