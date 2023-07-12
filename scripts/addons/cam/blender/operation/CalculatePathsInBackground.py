import bpy
from bpy.types import Operator

from cam.ops import threadCom, threadread
import os
import subprocess
import threading

class CalculatePathsInBackground(Operator):
    """calculate CAM paths in background. File has to be saved before."""
    bl_idname = "object.calculate_cam_paths_background"
    bl_label = "Calculate CAM paths in background"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene
        operation = scene.cam_operations[scene.cam_active_operation]
        operation.computing = True

        bpath = bpy.app.binary_path
        fpath = bpy.data.filepath

        for path in bpy.utils.script_paths():
            scriptPath = f"{path}{os.sep}addons{os.sep}cam{os.sep}backgroundop.py"
            print(scriptPath)
            if os.path.isfile(scriptPath):
                break
        proc = subprocess.Popen([bpath, '-b', fpath, '-P', scriptPath, '--', '-o=' + str(scene.cam_active_operation)],
                                bufsize=1, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

        tcom = threadCom(operation, proc)
        readthread = threading.Thread(target=threadread, args=([tcom]), daemon=True)
        readthread.start()

        if not hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, 'cam_processes'):
            bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes = []
        bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes.append([readthread, tcom])
        return {'FINISHED'}