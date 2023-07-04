from cam import gcodepath, utils
from cam.ops import getChainOperations
from bpy.types import Operator
from bpy.props import IntProperty
import bpy

class PathsChain(Operator):
    """calculate a chain and export the gcode alltogether. """
    bl_idname = "object.calculate_cam_paths_chain"
    bl_label = "Calculate CAM paths in current chain and export chain gcode"
    bl_options = {'REGISTER', 'UNDO'}

    operationIndex: IntProperty(name="Operation", description="Specify the operation to calculate")

    def execute(self, context):
        scene = context.scene
        bpy.ops.object.mode_set(mode='OBJECT')     # force object mode
        chain = scene.cam_chains[self.operationIndex]
        chainOperations = getChainOperations(chain)

        for i in range(0, len(chainOperations)):
            scene.cam_active_operation = scene.cam_operations.find(chainOperations[i].name)
            bpy.ops.object.calculate_cam_path()

        meshes = []
        for operation in chainOperations:
            camPathName = utils.getCAMPathObjectNameConventionFrom(operation.name)
            meshes.append(bpy.data.objects[camPathName].data)

        gcodepath.exportGcodePath(chain.filename, meshes, chainOperations)
        return {'FINISHED'}