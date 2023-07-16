from cam import simulation, utils
from cam.ops import getChainOperations
from bpy.types import Operator
from bpy.props import IntProperty
import bpy


class SimulateChain(Operator):
    """simulate CAM chain, compared to single op simulation just writes into one image and thus enables
    to see how ops work together."""
    bl_idname = "object.cam_simulate_chain"
    bl_label = "CAM simulation"
    bl_options = {'REGISTER', 'UNDO'}

    chainIndex: IntProperty()

    def execute(self, context):
        scene = context.scene
        chain = scene.cam_chains[self.operationIndex]
        chainOperations = getChainOperations(chain)

        for operation in chainOperations:
            print(f"Operation name: {operation.name}")

        simulation.doSimulation(chain.name, chainOperations)
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")