from ..operation.CalculatePath import CalculatePath
from ..operation.KillPathsBackground import KillPathsBackground
from ..operation.PathExport import PathExport
from ..operation.CAMSimulate import CAMSimulate
from ..operation.CamChainOperationAdd import CamChainOperationAdd
from ..operation.CamOperationCopy import CamOperationCopy
from ..operation.CamOperationMove import CamOperationMove
from ..operation.CamOperationRemove import CamOperationRemove
from ..operation.ExpandOperation import ExpandOperation

from ..menu.CAMCutterMTPresets import CAMCutterMTPresets
from cam import utils
from ...simple import strInUnits

from bpy.types import UIList
import bpy

class CAMULOperations(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        itemColumn = layout.column()
        mainRow = itemColumn.column_flow(columns=2, align=False)
        row = mainRow.row(align=True)
        nameIconID = context.scene.previewCollection["name"].icon_id

        foundRowExpansions = (rowExpansion for rowExpansion in context.scene.cam_operation_expansions if rowExpansion.operationName == item.name)
        foundExpansion = next(foundRowExpansions)

        expansionIconID = "TRIA_RIGHT" if foundExpansion.operationCollapsed else "TRIA_DOWN"

        expandedButton = row.operator(ExpandOperation.bl_idname, text="", icon=expansionIconID, emboss=False)
        expandedButton.operationName = item.name

        row.prop(item, "name", text="", icon_value=nameIconID, emboss=False)
        row.prop(item, "filename", icon="FILE", text="", emboss=False)
        row.prop(item, 'geometry_source', text="")

        if item.strategy == 'CURVE':
            if item.geometry_source == 'OBJECT':
                row.prop_search(item, "object_name", bpy.data, "objects", text="")
            elif item.geometry_source == 'COLLECTION':
                row.prop_search(item, "collection_name", bpy.data, "collections", text="")
        else:
            if item.geometry_source == 'OBJECT':
                row.prop_search(item, "object_name", bpy.data, "objects", text="")
                if item.enable_A:
                    self.layout.prop(item, 'rotation_A')
                if item.enable_B:
                    self.layout.prop(item, 'rotation_B')

            elif item.geometry_source == 'COLLECTION':
                row.prop_search(item, "collection_name", bpy.data, "collections", text="")
            else:
                row.prop_search(item, "source_image_name", bpy.data, "images", text="")

        if item.strategy in ['CARVE', 'PROJECTED_CURVE']:
            row.prop_search(item, "curve_object", bpy.data, "objects", text="")
            if item.strategy == 'PROJECTED_CURVE':
                row.prop_search(item, "curve_object1", bpy.data, "objects", text="")

        buttonRow = mainRow.row(align=True)
        buttonRow.alignment = "RIGHT"

        millIconId = context.scene.previewCollection["millPath"].icon_id
        millPathSimulationId = context.scene.previewCollection["millSimulation"].icon_id
        if item.computing:
            buttonRow.label(text='computing')
            buttonRow.operator(KillPathsBackground.KillPathsBackground.bl_idname, text="", icon='CANCEL', emboss=False)
        else:
            buttonRow.operator(CalculatePath.bl_idname, text="", icon_value=millIconId, emboss=False).operationIndex = index

            buttonRow.operator(CAMSimulate.bl_idname, icon_value=millPathSimulationId, text="", emboss=False)
            name = utils.getCAMPathObjectNameConventionFrom(item.name)
            if bpy.context.scene.objects.get(name) is not None:
                exportPathId = context.scene.previewCollection["exportGCode"].icon_id
                buttonRow.operator(PathExport.bl_idname, icon_value=exportPathId, text="", emboss=False)

        scene = context.scene
        if len(scene.cam_chains) > 0:
            buttonRow.operator(CamChainOperationAdd.bl_idname, icon='ADD', text="", emboss=False)

        buttonRow.operator(CamOperationCopy.bl_idname, icon='COPYDOWN', text="", emboss=False)
        upOperator = buttonRow.operator(CamOperationMove.bl_idname, icon='TRIA_UP', text="", emboss=False)
        upOperator.direction = "UP"
        upOperator.operationIndex = index

        downOperator = buttonRow.operator(CamOperationMove.bl_idname, icon='TRIA_DOWN', text="", emboss=False)
        downOperator.direction = "DOWN"
        downOperator.operationIndex = index

        buttonRow.operator(CamOperationRemove.bl_idname, icon='REMOVE', text="", emboss=False)

        if not foundExpansion.operationCollapsed:
            # Operation options
            operationOptionsRow = itemColumn.row(align=True)
            operationOptionsRow.label(text="     Options")
            operationOptionsElementsRow = operationOptionsRow.grid_flow(row_major=True, align=True)
            self.draw_operation_options(item, operationOptionsElementsRow)

            operationCutterRow = itemColumn.row(align=True)
            operationCutterRow.label(text="     Cutter")
            operationCutterElementsRow = operationCutterRow.grid_flow(row_major=True, align=True)
            self.draw_operation_tool(item, operationCutterElementsRow)

            operationFeedrateRow = itemColumn.row(align=True)
            operationFeedrateRow.label(text="     Feedrate")
            operationFeedrateElementsRow = operationFeedrateRow.grid_flow(row_major=True, align=True)
            self.draw_feedrate(item, operationFeedrateElementsRow)

            operationMovementRow = itemColumn.row(align=True)
            operationMovementRow.label(text="     Movement")
            operationMovementElementsRow = operationMovementRow.grid_flow(row_major=True, align=True)
            self.draw_movement(item, operationMovementElementsRow)

            operationAreaRow = itemColumn.row(align=True)
            operationAreaRow.label(text="     Area")
            operationAreaElementsRow = operationAreaRow.grid_flow(row_major=True, align=True)
            self.draw_area(item, operationAreaElementsRow)

            operationOptimizationRow = itemColumn.row(align=True)
            operationOptimizationRow.label(text="     Optimization")
            operationOptimizationElementsRow = operationOptimizationRow.grid_flow(row_major=True, align=True)
            self.draw_optimization(item, operationOptimizationElementsRow)

            operationGCodeRow = itemColumn.row(align=True)
            operationGCodeRow.label(text="     G-Code")
            operationGCodeElementsRow = operationGCodeRow.grid_flow(row_major=True, align=True)
            self.draw_gcode(item, operationGCodeElementsRow)

            operationMaterialRow = itemColumn.row(align=True)
            operationMaterialRow.label(text="     Material")
            operationMaterialElementsRow = operationMaterialRow.grid_flow(row_major=True, align=True)
            self.draw_material(item, operationMaterialElementsRow)

            operationOperationPropertiesRow = itemColumn.row(align=True)
            operationOperationPropertiesRow.label(text="     Operation")
            operationOperationPropertiesElementsRow = operationOperationPropertiesRow.grid_flow(row_major=True, align=True)
            self.draw_operation_properties(item, operationOperationPropertiesElementsRow)

            operationInfoRow = itemColumn.row(align=True)
            operationInfoRow.label(text="     Info")
            operationInfoElementsRow = operationInfoRow.grid_flow(row_major=True, align=True)
            self.draw_info(item, operationInfoElementsRow)

    def draw_info(self, item, layout):
        for line in item.info.warnings.rstrip("\n").split("\n"):
            if len(line) > 0:
                layout.label(text=line, icon='ERROR')

        if int(item.info.duration * 60) > 0:
            time_estimate = f"Operation Time: {int(item.info.duration*60)}s "
            if item.info.duration > 60:
                time_estimate += f" ({int(item.info.duration / 60)}h"
                time_estimate += f" {round(item.info.duration % 60)}min)"
            elif item.info.duration > 1:
                time_estimate += f" ({round(item.info.duration % 60)}min)"

            layout.label(text=time_estimate)

        if item.info.chipload > 0:
            chipload = f"Chipload: {strInUnits(item.info.chipload, 4)}/tooth"
            layout.label(text=chipload)

        if int(item.info.duration * 60) > 0:
            row = layout.row()
            row.label(text='Hourly Rate')
            row.prop(bpy.context.scene.cam_machine, 'hourly_rate', text='')

            if float(bpy.context.scene.cam_machine.hourly_rate) < 0.01:
                return

            cost_per_second = bpy.context.scene.cam_machine.hourly_rate / 3600
            total_cost = item.info.duration * 60 * cost_per_second
            op_cost = f"Operation cost: ${total_cost:.2f} (${cost_per_second:.2f}/s)"
            layout.label(text=op_cost)

    def draw_operation_properties(self, item, layout):
        use_experimental = bpy.context.preferences.addons['cam'].preferences.experimental

        if item.valid:
            if use_experimental:
                layout.prop(item, 'machine_axes')
            if item.machine_axes == '3':
                layout.prop(item, 'strategy')
            elif item.machine_axes == '4':
                layout.prop(item, 'strategy4axis')
                if item.strategy4axis == 'INDEXED':
                    layout.prop(item, 'strategy')
                layout.prop(item, 'rotary_axis_1')

            elif item.machine_axes == '5':
                layout.prop(item, 'strategy5axis')
                if item.strategy5axis == 'INDEXED':
                    layout.prop(item, 'strategy')
                layout.prop(item, 'rotary_axis_1')
                layout.prop(item, 'rotary_axis_2')

            if item.strategy in ['BLOCK', 'SPIRAL', 'CIRCLES', 'OUTLINEFILL']:
                layout.prop(item, 'movement_insideout')

            if item.strategy in ['CUTOUT', 'CURVE']:
                if item.strategy == 'CUTOUT':
                    layout.prop(item, 'cut_type')
                    layout.label(text="Overshoot works best with curve")
                    layout.label(text="having C remove doubles")
                    layout.prop(item, 'straight')
                    layout.prop(item, 'profile_start')
                    layout.label(text="Lead in / out not fully working")
                    layout.prop(item, 'lead_in')
                    layout.prop(item, 'lead_out')
                layout.prop(item, 'enable_A')
                if item.enable_A:
                    layout.prop(item, 'rotation_A')
                    layout.prop(item, 'A_along_x')
                    if item.A_along_x:
                        layout.label(text='A || X - B || Y')
                    else:
                        layout.label(text='A || Y - B ||X')

                layout.prop(item, 'enable_B')
                if item.enable_B:
                    layout.prop(item, 'rotation_B')

                layout.prop(item, 'outlines_count')
                if item.outlines_count > 1:
                    layout.prop(item, 'dist_between_paths')
                    self.EngagementDisplay(item, layout)
                    layout.prop(item, 'movement_insideout')
                layout.prop(item, 'dont_merge')

            elif item.strategy == 'WATERLINE':
                layout.label(text="OCL doesn't support fill areas")
                if not item.optimisation.use_opencamlib:
                    layout.prop(item, 'slice_detail')
                    layout.prop(item, 'waterline_fill')
                    if item.waterline_fill:
                        layout.prop(item, 'dist_between_paths')
                        self.EngagementDisplay(item, layout)
                        layout.prop(item, 'waterline_project')
            elif item.strategy == 'CARVE':
                layout.prop(item, 'carve_depth')
                layout.prop(item, 'dist_along_paths')
            elif item.strategy == 'MEDIAL_AXIS':
                layout.prop(item, 'medial_axis_threshold')
                layout.prop(item, 'medial_axis_subdivision')
                layout.prop(item, 'add_pocket_for_medial')
                layout.prop(item, 'add_mesh_for_medial')
            elif item.strategy == 'DRILL':
                layout.prop(item, 'drill_type')
                layout.prop(item, 'enable_A')
                if item.enable_A:
                    layout.prop(item, 'rotation_A')
                    layout.prop(item, 'A_along_x')
                    if item.A_along_x:
                        layout.label(text='A || X - B || Y')
                    else:
                        layout.label(text='A || Y - B ||X')
                layout.prop(item, 'enable_B')
                if item.enable_B:
                    layout.prop(item, 'rotation_B')

            elif item.strategy == 'POCKET':
                layout.prop(item, 'pocket_option')
                layout.prop(item, 'pocketToCurve')
                layout.prop(item, 'dist_between_paths')
                self.EngagementDisplay(item, layout)
                layout.prop(item, 'enable_A')
                if item.enable_A:
                    layout.prop(item, 'rotation_A')
                    layout.prop(item, 'A_along_x')
                    if item.A_along_x:
                        layout.label(text='A || X - B || Y')
                    else:
                        layout.label(text='A || Y - B ||X')
                layout.prop(item, 'enable_B')
                if item.enable_B:
                    layout.prop(item, 'rotation_B')
            else:
                layout.prop(item, 'dist_between_paths')
                self.EngagementDisplay(item, layout)
                layout.prop(item, 'dist_along_paths')
                if item.strategy == 'PARALLEL' or item.strategy == 'CROSS':
                    layout.prop(item, 'parallel_angle')
                    layout.prop(item, 'enable_A')
                if item.enable_A:
                    layout.prop(item, 'rotation_A')
                    layout.prop(item, 'A_along_x')
                    if item.A_along_x:
                        layout.label(text='A || X - B || Y')
                    else:
                        layout.label(text='A || Y - B ||X')
                layout.prop(item, 'enable_B')
                if item.enable_B:
                    layout.prop(item, 'rotation_B')

                layout.prop(item, 'inverse')
            if item.strategy not in ['POCKET', 'DRILL', 'CURVE', 'MEDIAL_AXIS']:
                layout.prop(item, 'use_bridges')
                if item.use_bridges:
                    layout.prop(item, 'bridges_width')
                    layout.prop(item, 'bridges_height')

                    layout.prop_search(item, "bridges_collection_name", bpy.data, "collections")
                    layout.prop(item, 'use_bridge_modifiers')
                layout.operator("scene.cam_bridges_add", text="Autogenerate bridges")
        if item.strategy == 'WATERLINE':
                layout.label(text="Waterline roughing strategy")
                layout.label(text="needs a skin margin")
        layout.prop(item, 'skin')

        if item.machine_axes == '3':
            layout.prop(item, 'array')
            if item.array:
                layout.prop(item, 'array_x_count')
                layout.prop(item, 'array_x_distance')
                layout.prop(item, 'array_y_count')
                layout.prop(item, 'array_y_distance')


    def draw_material(self, item, layout):
        if item.geometry_source not in ['OBJECT', 'COLLECTION']:
            layout.label(text='Estimated from image')
            return

        layout.prop(item.material, 'estimate_from_model')

        if item.material.estimate_from_model:
            row_radius = layout.row()
            row_radius.label(text="Additional radius")
            row_radius.prop(item.material, 'radius_around_model', text='')
        else:
            layout.prop(item.material, 'origin')
            layout.prop(item.material, 'size')

            row_axis = layout.row()
            row_axis.prop(item.material, 'center_x')
            row_axis.prop(item.material, 'center_y')
            layout.prop(item.material, 'z_position')
            layout.operator("object.material_cam_position", text="Position object")

    def draw_gcode(self, item, layout):
        layout.prop(item, 'output_header')

        if item.output_header:
            layout.prop(item, 'gcode_header')
        layout.prop(item, 'output_trailer')
        if item.output_trailer:
            layout.prop(item, 'gcode_trailer')
        layout.prop(item, 'enable_dust')
        if item.enable_dust:
            layout.prop(item, 'gcode_start_dust_cmd')
            layout.prop(item, 'gcode_stop_dust_cmd')
        layout.prop(item, 'enable_hold')
        if item.enable_hold:
            layout.prop(item, 'gcode_start_hold_cmd')
            layout.prop(item, 'gcode_stop_hold_cmd')
        layout.prop(item, 'enable_mist')
        if item.enable_mist:
            layout.prop(item, 'gcode_start_mist_cmd')
            layout.prop(item, 'gcode_stop_mist_cmd')

    def draw_optimization(self, item, layout):
        layout.prop(item.optimisation, 'optimize')
        if item.optimisation.optimize:
            layout.prop(item.optimisation, 'optimize_threshold')

        if item is None:
            return
        if not item.valid:
            return

        if not item.geometry_source in ["OBJECT", "COLLECTION"]:
            return

        exact_possible = item.strategy not in [
            'MEDIAL_AXIS', 'POCKET', 'CUTOUT', 'DRILL', 'PENCIL', 'CURVE']

        if exact_possible:
            layout.prop(item.optimisation, 'use_exact')

        if not exact_possible or not item.optimisation.use_exact:

            row = layout.row(align=True)
            row.prop(item.optimisation, 'pixsize')
            row.prop(item.optimisation, 'imgres_limit')

            sx = item.max.x - item.min.x
            sy = item.max.y - item.min.y
            resx = int(sx / item.optimisation.pixsize)
            resy = int(sy / item.optimisation.pixsize)

            if resx > 0 and resy > 0:
                resolution = f"Resolution: {resx} x {resy}"
                layout.label(text=resolution)

        if not (exact_possible and item.optimisation.use_exact):
            return

        opencamlib_version = cam.utils.opencamlib_version()

        if opencamlib_version is None:
            layout.label(text="Opencamlib is not available ")
            layout.prop(item.optimisation, 'exact_subdivide_edges')
        else:
            layout.prop(item.optimisation, 'use_opencamlib')

        row = layout.row(align=True)
        row.prop(item.optimisation, 'simulation_detail')
        row.prop(item.optimisation, 'circle_detail')

    def draw_area(self, item, layout):
        layout.prop(item, 'use_layers')
        if item.use_layers:
            layout.prop(item, 'stepdown')

        layout.prop(item, 'maxz')

        if item.maxz > item.free_movement_height:
            layout.prop(item, 'free_movement_height')
            layout.label(text='Depth start > Free movement')
            layout.label(text='POSSIBLE COLLISION')

        if item.geometry_source in ['OBJECT', 'COLLECTION']:
            if item.strategy == 'CURVE':
                layout.label(text="cannot use depth from object using CURVES")

            if not item.minz_from_ob:
                if not item.minz_from_material:
                    layout.prop(item, 'minz')
                layout.prop(item, 'minz_from_material')
            if not item.minz_from_material:
                layout.prop(item, 'minz_from_ob')
        else:
            layout.prop(item, 'source_image_scale_z')
            layout.prop(item, 'source_image_size_x')
            if item.source_image_name != '':
                i = bpy.data.images[item.source_image_name]
                if i is not None:
                    sy = int((item.source_image_size_x / i.size[0]) * i.size[1] * 1000000) / 1000
                    layout.label(text='image size on y axis: ' + strInUnits(sy, 8))
                    layout.separator()
            layout.prop(item, 'source_image_offset')
            col = layout.column(align=True)
            col.prop(item, 'source_image_crop', text='Crop source image')
            if item.source_image_crop:
                col.prop(item, 'source_image_crop_start_x', text='start x')
                col.prop(item, 'source_image_crop_start_y', text='start y')
                col.prop(item, 'source_image_crop_end_x', text='end x')
                col.prop(item, 'source_image_crop_end_y', text='end y')

        if item.strategy in ['BLOCK', 'SPIRAL', 'CIRCLES', 'PARALLEL', 'CROSS']:
            layout.prop(item, 'ambient_behaviour')
            if item.ambient_behaviour == 'AROUND':
                layout.prop(item, 'ambient_radius')

            layout.prop(item, 'use_limit_curve')

            if item.use_limit_curve:
                layout.prop_search(item, "limit_curve", bpy.data, "objects")

            layout.prop(item, "ambient_cutter_restrict")

    def draw_movement(self, item, layout):
        if item.valid:
            layout.prop(item, 'movement_type')

            if item.movement_type in ['BLOCK', 'SPIRAL', 'CIRCLES']:
                layout.prop(item, 'movement_insideout')

            layout.prop(item, 'spindle_rotation_direction')
            layout.prop(item, 'free_movement_height')
            if item.maxz > item.free_movement_height:
                layout.label(text='Depth start > Free movement')
                layout.label(text='POSSIBLE COLLISION')
            layout.prop(item, 'useG64')
            if item.useG64:
                layout.prop(item, 'G64')
            if item.strategy == 'PARALLEL' or item.strategy == 'CROSS':
                if not item.ramp:
                    layout.prop(item, 'parallel_step_back')
            if item.strategy == 'CUTOUT' or item.strategy == 'POCKET' or item.strategy == 'MEDIAL_AXIS':
                layout.prop(item, 'first_down')

            if item.strategy == 'POCKET':
                layout.prop(item, 'helix_enter')
                if item.helix_enter:
                    layout.prop(item, 'ramp_in_angle')
                    layout.prop(item, 'helix_diameter')
                layout.prop(item, 'retract_tangential')
                if item.retract_tangential:
                    layout.prop(item, 'retract_radius')
                    layout.prop(item, 'retract_height')

            layout.prop(item, 'ramp')
            if item.ramp:
                layout.prop(item, 'ramp_in_angle')
                layout.prop(item, 'ramp_out')
                if item.ramp_out:
                    layout.prop(item, 'ramp_out_angle')

            layout.prop(item, 'stay_low')
            if item.stay_low:
                layout.prop(item, 'merge_dist')
            if item.cutter_type != 'BALLCONE':
                layout.prop(item, 'protect_vertical')
            if item.protect_vertical:
                layout.prop(item, 'protect_vertical_limit')

    def draw_feedrate(self, item, layout):
        #layout = layout.row(align=True, heading="Feedrate") 
        layout.prop(item, 'feedrate')
        layout.prop(item, 'do_simulation_feedrate')

        #layout = layout.row(align=True)
        layout.prop(item, 'plunge_feedrate')
        layout.prop(item, 'plunge_angle')
        layout.prop(item, 'spindle_rpm')

    def EngagementDisplay(self, operation, layout):
        if operation.cutter_type == 'BALLCONE':
            if operation.dist_between_paths > operation.ball_radius:
                layout.label(text="CAUTION: CUTTER ENGAGEMENT")
                layout.label(text="GREATER THAN 50%")
            layout.label(text="Cutter engagement: " + str(round(100 * operation.dist_between_paths / operation.ball_radius, 1)) + "%")
        else:
            if operation.dist_between_paths > operation.cutter_diameter / 2:
                layout.label(text="CAUTION: CUTTER ENGAGEMENT")
                layout.label(text="GREATER THAN 50%")
            layout.label(text="Cutter Engagement: " + str(round(100 * operation.dist_between_paths / operation.cutter_diameter, 1)) + "%")

    def draw_operation_tool(self, item, layout):
        row = layout.row(align=True)
        row.menu(CAMCutterMTPresets.__name__, text=CAMCutterMTPresets.bl_label)
        row.operator("render.cam_preset_cutter_add", text="", icon='ADD')
        row.operator("render.cam_preset_cutter_add", text="", icon='REMOVE').remove_active = True

        layout.prop(item, 'cutter_id', text="")
        if item.strategy == "POCKET" or item.strategy == "CUTOUT" :
            layout.prop(item, 'cutter_typeb', text="")
        else:
            layout.prop(item, 'cutter_type', text="")
        if item.cutter_type == 'VCARVE':
            layout.prop(item, 'cutter_tip_angle')
        if item.cutter_type == 'BALLCONE':
            layout.prop(item, 'ball_radius')
            self.EngagementDisplay(item, layout)
            layout.prop(item, 'cutter_tip_angle')
            layout.label(text='Cutter diameter = shank diameter')
        if item.cutter_type == 'CYLCONE':
            layout.prop(item, 'cylcone_diameter')
            self.EngagementDisplay(item, layout)
            layout.prop(item, 'cutter_tip_angle')
            layout.label(text='Cutter diameter = shank diameter')
        if item.cutter_type == 'BULLNOSE':
            layout.prop(item, 'bull_corner_radius')
            self.EngagementDisplay(item, layout)
            layout.label(text='Cutter diameter = shank diameter')

        if item.cutter_type == 'LASER':
            layout.prop(item, 'Laser_on')
            layout.prop(item, 'Laser_off')
            layout.prop(item, 'Laser_cmd')
            layout.prop(item, 'Laser_delay')

        if item.cutter_type == 'PLASMA':
            layout.prop(item, 'Plasma_on')
            layout.prop(item, 'Plasma_off')
            layout.prop(item, 'Plasma_delay')
            layout.prop(item, 'Plasma_dwell')
            layout.prop(item, 'lead_in')
            layout.prop(item, 'lead_out')

        if item.cutter_type == 'CUSTOM':
            if item.optimisation.use_exact:
                layout.label(text='Warning - only convex shapes are supported. ', icon='COLOR_RED')
                layout.label(text='If your custom cutter is concave,')
                layout.label(text='switch exact mode off.')

            layout.prop_search(item, "cutter_object_name", bpy.data, "objects")

        layout.prop(item, 'cutter_diameter')
        if item.strategy == "POCKET" or item.strategy == "PARALLEL" or item.strategy == "CROSS" \
                or item.strategy == "WATERLINE":
            self.EngagementDisplay(item, layout)
        if item.cutter_type != "LASER":
            layout.prop(item, 'cutter_flutes')
        layout.prop(item, 'cutter_description')

    def draw_operation_options(self, item, layout):
        if item.strategy != 'DRILL':
            layout.prop(item, 'remove_redundant_points')

        if item.remove_redundant_points:
            layout.prop(item, 'simplify_tol')
            layout.label(text='Revise your Code before running! Quality will suffer if tolerance is high')

        if item.geometry_source in ['OBJECT', 'COLLECTION']:
            layout.prop(item, 'use_modifiers')
        layout.prop(item, 'hide_all_others')
        layout.prop(item, 'parent_path_to_object')