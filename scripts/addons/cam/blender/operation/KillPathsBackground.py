from bpy.types import Operator
import bpy

class KillPathsBackground(Operator):
    """Remove CAM path processes in background."""
    bl_idname = "object.kill_calculate_cam_paths_background"
    bl_label = "Kill background computation of an operation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene
        activeOperation = scene.cam_operations[scene.cam_active_operation]
        self.operation = activeOperation

        if hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, 'cam_processes'):
            processes = bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes
            for p in processes:
                tcom = p[1]
                if tcom.opname == activeOperation.name:
                    processes.remove(p)
                    tcom.proc.kill()
                    activeOperation.computing = False

        return {'FINISHED'}