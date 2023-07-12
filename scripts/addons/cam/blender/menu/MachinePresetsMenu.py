from bpy.types import Menu

class MachinePresetsMenu(Menu):
    bl_label = "Machine presets"
    preset_subdir = "cam_machines"
    preset_operator = "script.execute_preset"
    bl_idname = "CAM_MT_machine_presets"
    draw = Menu.draw_preset