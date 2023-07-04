from cam import gcodepath, utils
from bpy.types import Operator
import bpy

class PathExport(Operator):
    """Export gcode. Can be used only when the path object is present"""
    bl_idname = "object.cam_export"
    bl_label = "Export operation gcode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene
        operation = scene.cam_operations[scene.cam_active_operation]

        camPathName = utils.getCAMPathObjectNameConventionFrom(operation.name)
        print("EXPORTING", operation.filename, bpy.data.objects[camPathName].data, operation)

        objectData = [bpy.data.objects[camPathName].data]
        gcodepath.exportGcodePath(operation.filename, objectData, [operation])
        return {'FINISHED'}