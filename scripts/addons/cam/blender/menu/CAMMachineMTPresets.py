from bpy.types import Menu

class CAMMachineMTPresets(Menu):
    bl_label = "Machine presets"
    preset_subdir = "cam_machines"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset