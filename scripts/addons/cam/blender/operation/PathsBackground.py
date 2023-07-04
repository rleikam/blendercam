from cam.ops import threadCom, threadread
import os
import subprocess
import threading
from bpy.types import Operator
import bpy


class PathsBackground(Operator):
    """calculate CAM paths in background. File has to be saved before."""
    bl_idname = "object.calculate_cam_paths_background"
    bl_label = "Calculate CAM paths in background"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        s = bpy.context.scene
        o = s.cam_operations[s.cam_active_operation]
        self.operation = o
        o.computing = True

        bpath = bpy.app.binary_path
        fpath = bpy.data.filepath

        for p in bpy.utils.script_paths():
            scriptpath = p + os.sep + 'addons' + os.sep + 'cam' + os.sep + 'backgroundop.py'
            print(scriptpath)
            if os.path.isfile(scriptpath):
                break
        proc = subprocess.Popen([bpath, '-b', fpath, '-P', scriptpath, '--', '-o=' + str(s.cam_active_operation)],
                                bufsize=1, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

        tcom = threadCom(o, proc)
        readthread = threading.Thread(target=threadread, args=([tcom]), daemon=True)
        readthread.start()
        # self.__class__.cam_processes=[]
        if not hasattr(bpy.ops.object.calculate_cam_paths_background.__class__, 'cam_processes'):
            bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes = []
        bpy.ops.object.calculate_cam_paths_background.__class__.cam_processes.append([readthread, tcom])
        return {'FINISHED'}