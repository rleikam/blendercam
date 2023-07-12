import bpy
from bpy.types import Panel

from ..operation import AddMachinePreset
from .ButtonsPanel import ButtonsPanel
from ..menu.MachinePresetsMenu import MachinePresetsMenu

class MachinePanel(ButtonsPanel, Panel):
    """CAM machine panel"""
    bl_label = "Machine"
    bl_idname = "CAM_PT_machine"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        unitSettings = scene.unit_settings

        ao = scene.cam_machine

        if ao:
            # machine preset
            row = layout.row(align=True)
            row.menu(MachinePresetsMenu.bl_idname, text=MachinePresetsMenu.bl_label)
            row.operator(AddMachinePreset.bl_idname, text="", icon='ADD')
            row.operator(AddMachinePreset.bl_idname, text="", icon='REMOVE').remove_active = True
            layout.prop(ao, 'post_processor')
            layout.prop(ao, 'eval_splitting')
            if ao.eval_splitting:
                layout.prop(ao, 'split_limit')

            layout.prop(unitSettings, 'system')

            layout.prop(ao, 'use_position_definitions')
            if ao.use_position_definitions:
                layout.prop(ao, 'starting_position')
                layout.prop(ao, 'mtc_position')
                layout.prop(ao, 'ending_position')
            layout.prop(ao, 'working_area')
            layout.prop(ao, 'feedrate_min')
            layout.prop(ao, 'feedrate_max')
            layout.prop(ao, 'feedrate_default')
            # TODO: spindle default and feedrate default should become part of the cutter definition...
            layout.prop(ao, 'spindle_min')
            layout.prop(ao, 'spindle_max')
            layout.prop(ao, 'spindle_start_time')
            layout.prop(ao, 'spindle_default')
            layout.prop(ao, 'output_tool_definitions')
            layout.prop(ao, 'output_tool_change')
            if ao.output_tool_change:
                layout.prop(ao, 'output_g43_on_tool_change')

            if self.use_experimental:
                layout.prop(ao, 'axis4')
                layout.prop(ao, 'axis5')
                layout.prop(ao, 'collet_size')

                layout.prop(ao, 'output_block_numbers')
                if ao.output_block_numbers:
                    layout.prop(ao, 'start_block_number')
                    layout.prop(ao, 'block_number_increment')
            layout.prop(ao, 'hourly_rate')
