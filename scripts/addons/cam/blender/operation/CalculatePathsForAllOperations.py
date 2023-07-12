from bpy.types import Operator
import bpy

class CalculatePathsForAllOperations(Operator):
    """calculate all CAM paths"""
    bl_idname = "object.calculate_cam_paths_all"
    bl_label = "Calculate all CAM paths"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        i = 0
        for operation in bpy.context.scene.cam_operations:
            bpy.context.scene.cam_active_operation = i
            print('\nCalculating path :' + operation.name)
            print('\n')
            bpy.ops.object.calculate_cam_paths_background()
            i += 1

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")