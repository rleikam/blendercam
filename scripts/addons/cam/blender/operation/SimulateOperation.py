from cam import simulation, utils
from bpy.types import Operator
from bpy.props import IntProperty
import bpy

class SimulateOperation(Operator):
    """simulate CAM operation
    this is performed by: creating an image, painting Z depth of the brush substractively.
    Works only for some operations, can not be used for 4-5 axis."""
    bl_idname = "object.cam_simulate"
    bl_label = "CAM simulation"
    bl_options = {'REGISTER', 'UNDO'}

    operationIndex: IntProperty()

    def execute(self, context):
        scene = context.scene
        operation = scene.cam_operations[self.operationIndex]

        operationPathObjectName = utils.getCAMPathObjectNameConventionFrom(operation.name)

        if operationPathObjectName in bpy.data.objects:
            simulation.doSimulation(operationPathObjectName, [operation])
        else:
            print('no computed path to simulate')
            return {'FINISHED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "operation", bpy.context.scene, "cam_operations")