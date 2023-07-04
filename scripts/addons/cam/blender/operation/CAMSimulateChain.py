from cam import simulation, utils
from cam.ops import getChainOperations
from bpy.types import Operator
from bpy.props import StringProperty
import bpy


class CAMSimulateChain(Operator):
    """simulate CAM chain, compared to single op simulation just writes into one image and thus enables
    to see how ops work together."""
    bl_idname = "object.cam_simulate_chain"
    bl_label = "CAM simulation"
    bl_options = {'REGISTER', 'UNDO'}

    operation: StringProperty(name="Operation",
                              description="Specify the operation to calculate", default='Operation')

    def execute(self, context):
        scene = context.scene
        chain = scene.cam_chains[scene.cam_active_chain]
        chainops = getChainOperations(chain)

        canSimulate = True
        for operation in chainops:
            operationName = utils.getCAMPathObjectNameConventionFrom(operation.name)
            if operationName not in bpy.data.objects:
                canSimulate = True  # force true
            print("operation name " + str(operation.name))
        if canSimulate:
            simulation.doSimulation(chain.name, chainops)
        else:
            print('no computed path to simulate')
            return {'FINISHED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")