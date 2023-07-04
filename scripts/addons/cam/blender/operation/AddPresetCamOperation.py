from bpy.types import Operator
from bl_operators.presets import AddPresetBase

class AddPresetCamOperation(AddPresetBase, Operator):
    """Add an Operation Preset"""
    bl_idname = "render.cam_preset_operation_add"
    bl_label = "Add Operation Preset"
    preset_menu = "CAM_OPERATION_MT_presets"

    preset_defines = ["o = bpy.context.scene.cam_operations[bpy.context.scene.cam_active_operation]"]

    preset_values = ['o.use_layers', 'o.info.duration', 'o.info.chipload', 'o.material.estimate_from_model', 'o.stay_low', 'o.carve_depth',
                     'o.dist_along_paths', 'o.source_image_crop_end_x', 'o.source_image_crop_end_y', 'o.material.size',
                     'o.material.radius_around_model', 'o.use_limit_curve', 'o.cut_type', 'o.optimisation.use_exact',
                     'o.optimisation.exact_subdivide_edges', 'o.minz_from_ob', 'o.free_movement_height',
                     'o.source_image_crop_start_x', 'o.movement_insideout', 'o.spindle_rotation_direction', 'o.skin',
                     'o.source_image_crop_start_y', 'o.movement_type', 'o.source_image_crop', 'o.limit_curve',
                     'o.spindle_rpm', 'o.ambient_behaviour', 'o.cutter_type', 'o.source_image_scale_z',
                     'o.cutter_diameter', 'o.source_image_size_x', 'o.curve_object', 'o.curve_object1',
                     'o.cutter_flutes', 'o.ambient_radius', 'o.optimisation.simulation_detail', 'o.update_offsetimage_tag',
                     'o.dist_between_paths', 'o.max', 'o.min', 'o.optimisation.pixsize', 'o.slice_detail', 'o.parallel_step_back',
                     'o.drill_type', 'o.source_image_name', 'o.dont_merge', 'o.update_silhouete_tag',
                     'o.material.origin', 'o.inverse', 'o.waterline_fill', 'o.source_image_offset', 'o.optimisation.circle_detail',
                     'o.strategy', 'o.update_zbufferimage_tag', 'o.stepdown', 'o.feedrate', 'o.cutter_tip_angle',
                     'o.cutter_id', 'o.path_object_name', 'o.pencil_threshold', 'o.geometry_source',
                     'o.optimize_threshold', 'o.protect_vertical', 'o.plunge_feedrate', 'o.minz', 'o.info.warnings',
                     'o.object_name', 'o.optimize', 'o.parallel_angle', 'o.cutter_length',
                     'o.output_header', 'o.gcode_header', 'o.output_trailer', 'o.gcode_trailer', 'o.use_modifiers',
                     'o.minz_from_material', 'o.useG64',
                     'o.G64', 'o.enable_A', 'o.enable_B', 'o.A_along_x', 'o.rotation_A', 'o.rotation_B', 'o.straight']

    preset_subdir = "cam_operations"