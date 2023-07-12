from cam import gcodepath, utils
from cam.ops import getChainOperations
from bpy.types import Operator
import bpy

class ExportChainPaths(Operator):
    """calculate a chain and export the gcode alltogether. """
    bl_idname = "object.cam_export_paths_chain"
    bl_label = "Export CAM paths in current chain as gcode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene

        chain = scene.cam_chains[scene.cam_active_chain]
        chainOperations = getChainOperations(chain)
        meshes = []

        for operation in chainOperations:
            camPathName = utils.getCAMPathObjectNameConventionFrom(operation.name)
            objectData = [bpy.data.objects[camPathName].data]
            meshes.append(objectData)

        gcodepath.exportGcodePath(chain.filename, meshes, chainOperations)
        return {'FINISHED'}