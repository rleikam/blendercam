from cam import gcodepath, utils
from bpy.types import Operator
from bpy.props import IntProperty
import bpy

class ExportOperationPath(Operator):
    """Export gcode. Can be used only when the path object is present"""
    bl_idname = "object.cam_export"
    bl_label = "Export operation gcode"
    bl_options = {'REGISTER', 'UNDO'}

    operationIndex: IntProperty()

    def execute(self, context):
        scene = bpy.context.scene
        operation = scene.cam_operations[self.operationIndex]

        camPathName = utils.getCAMPathObjectNameConventionFrom(operation.name)
        print("EXPORTING", operation.filename, bpy.data.objects[camPathName].data, operation)

        objectData = [bpy.data.objects[camPathName].data]
        gcodepath.exportGcodePath(operation.filename, objectData, [operation])
        return {'FINISHED'}