from cam import gcodepath, utils
from cam.ops import getChainOperations
from bpy.types import Operator
from bpy.props import IntProperty
import bpy

class ExportChainPaths(Operator):
    """calculate a chain and export the gcode alltogether. """
    bl_idname = "object.cam_export_paths_chain"
    bl_label = "Export CAM paths in current chain as gcode"
    bl_options = {'REGISTER', 'UNDO'}

    chainIndex: IntProperty()

    def execute(self, context):
        scene = bpy.context.scene

        chain = scene.cam_chains[self.chainIndex]
        chainOperations = getChainOperations(chain)
        meshes = []

        for operation in chainOperations:
            pathName = utils.getCAMPathObjectNameConventionFrom(operation.name)
            objectData = [bpy.data.objects[pathName].data]
            meshes.append(objectData)

        gcodepath.exportGcodePath(chain.filename, meshes, chainOperations)
        return {'FINISHED'}